#!/usr/bin/python3
import os
import sys
import glob
import shutil
import optparse
import subprocess
import configparser

rebase_prefix    = ""
version_override = None
release_date     = None

def check_rebase():
    """ detect 'git rebase -x edk2-build.py master' testbuilds """
    global rebase_prefix
    global version_override

    if not os.path.exists('.git/rebase-merge/msgnum'):
        return ""
    with open('.git/rebase-merge/msgnum', 'r') as f:
        msgnum = int(f.read())
    with open('.git/rebase-merge/end', 'r') as f:
        end = int(f.read())
    with open('.git/rebase-merge/head-name', 'r') as f:
        head = f.read().strip().split('/')

    rebase_prefix = f'[ {int(msgnum/2)} / {int(end/2)} - {head[-1]} ] '
    if msgnum != end and not version_override:
        # fixed version speeds up builds
        version_override = "test-build-patch-series"

def get_coredir(cfg):
    if cfg.has_option('global', 'core'):
        return os.path.abspath(cfg['global']['core'])
    else:
        return os.getcwd()

def get_version(cfg):
    coredir = get_coredir(cfg)
    if version_override:
        version = version_override
        print('')
        print(f'### version [override]: {version}')
        return version
    if os.environ.get('RPM_PACKAGE_NAME'):
        version = os.environ.get('RPM_PACKAGE_NAME');
        version += '-' + os.environ.get('RPM_PACKAGE_VERSION');
        version += '-' + os.environ.get('RPM_PACKAGE_RELEASE');
        print('')
        print(f'### version [rpmbuild]: {version}')
        return version
    if os.path.exists(coredir + '/.git'):
        cmdline = [ 'git', 'describe', '--tags', '--abbrev=8', '--match=edk2-stable*' ]
        result = subprocess.run(cmdline, stdout = subprocess.PIPE, cwd = coredir)
        version = result.stdout.decode().strip()
        print('')
        print(f'### version [git]: {version}')
        return version
    return None

def pcd_string(name, value):
    return f'{name}=L{value}\\0'

def pcd_version(cfg):
    version = get_version(cfg)
    if version is None:
        return []
    return [ '--pcd', pcd_string('PcdFirmwareVersionString', version) ]

def pcd_release_date(cfg):
    if release_date is None:
        return []
    return [ '--pcd', pcd_string('PcdFirmwareReleaseDateString', release_date) ]

def build_message(line, line2 = None):
    if os.environ.get('TERM') in [ 'xterm', 'xterm-256color' ]:
        # setxterm  title
        start  = '\x1b]2;'
        end    = '\x07'
        print(f'{start}{rebase_prefix}{line}{end}', end = '')

    print('')
    print('###')
    print(f'### {rebase_prefix}{line}')
    if line2:
        print(f'### {line2}')
    print('###')

def build_run(cmdline, name, section, silent = False):
    print(cmdline)
    if silent:
        print('### building in silent mode ...', flush = True)
        result = subprocess.run(cmdline,
                                stdout = subprocess.PIPE,
                                stderr = subprocess.STDOUT)

        logfile = f'{section}.log'
        print(f'### writing log to {logfile} ...')
        with open(logfile, 'wb') as f:
            f.write(result.stdout)

        if result.returncode:
            print('### BUILD FAILURE')
            print('### output')
            print(result.stdout.decode())
            print(f'### exit code: {result.returncode}')
        else:
            print('### OK')
    else:
        result = subprocess.run(cmdline)
    if result.returncode:
        print(f'ERROR: {cmdline[0]} exited with {result.returncode} while building {name}')
        sys.exit(result.returncode)

def build_copy(plat, tgt, dstdir, copy):
    srcdir = f'Build/{plat}/{tgt}_GCC5'
    names = copy.split()
    srcfile = names[0]
    if len(names) > 1:
        dstfile = names[1]
    else:
        dstfile = os.path.basename(srcfile)
    print(f'# copy: {srcdir} / {srcfile}  =>  {dstdir} / {dstfile}')

    src = srcdir + '/' + srcfile
    dst = dstdir + '/' + dstfile
    os.makedirs(os.path.dirname(dst), exist_ok = True)
    shutil.copy(src, dst)

def pad_file(dstdir, pad):
    args = pad.split()
    if len(args) < 2:
        raise RuntimeError(f'missing arg for pad ({args})')
    name = args[0]
    size = args[1]
    cmdline = [
        'truncate',
        '--size', size,
        dstdir + '/' + name,
    ]
    print(f'# padding: {dstdir} / {name}  =>  {size}')
    subprocess.run(cmdline)

def build_one(cfg, build, jobs = None, silent = False):
    cmdline  = [ 'build' ]
    cmdline += [ '-t', 'GCC5' ]
    cmdline += [ '-p', cfg[build]['conf'] ]

    if (cfg[build]['conf'].startswith('OvmfPkg/') or
        cfg[build]['conf'].startswith('ArmVirtPkg/')):
        cmdline += pcd_version(cfg)
        cmdline += pcd_release_date(cfg)

    if jobs:
        cmdline += [ '-n', jobs ]
    for arch in cfg[build]['arch'].split():
        cmdline += [ '-a', arch ]
    if 'opts' in cfg[build]:
        for name in cfg[build]['opts'].split():
            section = 'opts.' + name
            for opt in cfg[section]:
                cmdline += [ '-D', opt + '=' + cfg[section][opt] ]
    if 'pcds' in cfg[build]:
        for name in cfg[build]['pcds'].split():
            section = 'pcds.' + name
            for pcd in cfg[section]:
                cmdline += [ '--pcd', pcd + '=' + cfg[section][pcd] ]
    if 'tgts' in cfg[build]:
        tgts = cfg[build]['tgts'].split()
    else:
        tgts = [ 'DEBUG' ]
    for tgt in tgts:
        desc = None
        if 'desc' in cfg[build]:
            desc = cfg[build]['desc']
        build_message(f'building: {cfg[build]["conf"]} ({cfg[build]["arch"]}, {tgt})',
                      f'description: {desc}')
        build_run(cmdline + [ '-b', tgt ],
                  cfg[build]['conf'],
                  build + '.' + tgt,
                  silent)

        if 'plat' in cfg[build]:
            # copy files
            for cpy in cfg[build]:
                if not cpy.startswith('cpy'):
                    continue
                build_copy(cfg[build]['plat'],
                           tgt,
                           cfg[build]['dest'],
                           cfg[build][cpy])
            # pad builds
            for pad in cfg[build]:
                if not pad.startswith('pad'):
                    continue
                pad_file(cfg[build]['dest'],
                         cfg[build][pad])

def build_basetools(silent = False):
    build_message(f'building: BaseTools')
    basedir = os.environ['EDK_TOOLS_PATH']
    cmdline = [ 'make', '-C', basedir ]
    build_run(cmdline, 'BaseTools', 'build.basetools', silent)

def binary_exists(name):
    for dir in os.environ['PATH'].split(':'):
        if os.path.exists(dir + '/' + name):
            return True
    return False

def prepare_env(cfg):
    """ mimic Conf/BuildEnv.sh """
    workspace = os.getcwd()
    packages = [ workspace, ]
    path = os.environ['PATH'].split(':')
    dirs = [
        'BaseTools/Bin/Linux-x86_64',
        'BaseTools/BinWrappers/PosixLike'
    ]

    if cfg.has_option('global', 'pkgs'):
        for pkgdir in cfg['global']['pkgs'].split():
            packages.append(os.path.abspath(pkgdir))
    coredir = get_coredir(cfg)
    if coredir != workspace:
        packages.append(coredir)

    # add basetools to path
    for dir in dirs:
        p = coredir + '/' + dir
        if not os.path.exists(p):
            continue
        if p in path:
            continue
        path.insert(0, p)

    # run edksetup if needed
    toolsdef = coredir + '/Conf/tools_def.txt';
    if not os.path.exists(toolsdef):
        os.makedirs(os.path.dirname(toolsdef), exist_ok = True)
        build_message('running BaseTools/BuildEnv')
        cmdline = [ 'sh', 'BaseTools/BuildEnv' ]
        subprocess.run(cmdline, cwd = coredir)

    # set variables
    os.environ['PATH'] = ':'.join(path)
    os.environ['PACKAGES_PATH'] = ':'.join(packages)
    os.environ['WORKSPACE'] = workspace
    os.environ['EDK_TOOLS_PATH'] = coredir + '/BaseTools'
    os.environ['CONF_PATH'] = coredir + '/Conf'
    os.environ['PYTHON_COMMAND'] = '/usr/bin/python3'
    os.environ['PYTHONHASHSEED'] = '1'

    # for cross builds
    if binary_exists('arm-linux-gnu-gcc'):
        os.environ['GCC5_ARM_PREFIX'] = 'arm-linux-gnu-'
    if binary_exists('aarch64-linux-gnu-gcc'):
        os.environ['GCC5_AARCH64_PREFIX'] = 'aarch64-linux-gnu-'
    if binary_exists('riscv64-linux-gnu-gcc'):
        os.environ['GCC5_RISCV64_PREFIX'] = 'riscv64-linux-gnu-'
    if binary_exists('loongarch64-linux-gnu-gcc'):
        os.environ['GCC5_LOONGARCH64_PREFIX'] = 'loongarch64-linux-gnu-'
    if binary_exists('x86_64-linux-gnu-gcc'):
        os.environ['GCC5_IA32_PREFIX'] = 'x86_64-linux-gnu-'
        os.environ['GCC5_X64_PREFIX'] = 'x86_64-linux-gnu-'
        os.environ['GCC5_BIN'] = 'x86_64-linux-gnu-'

def build_list(cfg):
    for build in cfg.sections():
        if not build.startswith('build.'):
            continue
        name = build.lstrip('build.')
        desc = 'no description'
        if 'desc' in cfg[build]:
            desc = cfg[build]['desc']
        print(f'# {name:20s} - {desc}')
    
def main():
    parser = optparse.OptionParser()
    parser.add_option('-c', '--config', dest = 'configfile',
                      type = 'string', default = '.edk2.builds')
    parser.add_option('-C', '--directory', dest = 'directory', type = 'string')
    parser.add_option('-j', '--jobs', dest = 'jobs', type = 'string')
    parser.add_option('-m', '--match', dest = 'match', type = 'string')
    parser.add_option('-x', '--exclude', dest = 'exclude', type = 'string')
    parser.add_option('-l', '--list', dest = 'list', action = 'store_true', default = False)
    parser.add_option('--silent', dest = 'silent', action = 'store_true', default = False)
    parser.add_option('--core', dest = 'core', type = 'string')
    parser.add_option('--pkg', '--package', dest = 'pkgs', type = 'string', action = 'append')
    parser.add_option('--version-override', dest = 'version_override', type = 'string')
    parser.add_option('--release-date', dest = 'release_date', type = 'string')
    (options, args) = parser.parse_args()

    if options.directory:
        os.chdir(options.directory)

    cfg = configparser.ConfigParser()
    cfg.optionxform = str
    cfg.read(options.configfile)

    if options.list:
        build_list(cfg)
        return

    if not cfg.has_section('global'):
        cfg.add_section('global')
    if options.core:
        cfg.set('global', 'core', options.core)
    if options.pkgs:
        cfg.set('global', 'pkgs', ' '.join(options.pkgs))

    global version_override
    global release_date
    check_rebase()
    if options.version_override:
        version_override = options.version_override
    if options.release_date:
        release_date = options.release_date

    prepare_env(cfg)
    build_basetools(options.silent)
    for build in cfg.sections():
        if not build.startswith('build.'):
            continue
        if options.match and options.match not in build:
            print(f'# skipping "{build}" (not matching "{options.match}")')
            continue
        if options.exclude and options.exclude in build:
            print(f'# skipping "{build}" (matching "{options.exclude}")')
            continue
        build_one(cfg, build, options.jobs, options.silent)

if __name__ == '__main__':
    sys.exit(main())
