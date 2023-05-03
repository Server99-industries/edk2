# https://fedoraproject.org/wiki/Changes/SetBuildFlagsBuildCheck
# breaks cross-building
%undefine _auto_set_build_flags

# actual firmware builds support cross-compiling.  edk2-tools
# in theory should build everywhere without much trouble, but
# in practice the edk2 build system barfs on archs it doesn't know
# (such as ppc), so lets limit things to the known-good ones.
ExclusiveArch: x86_64 aarch64

# edk2-stable202302
%define GITDATE        20230301
%define GITCOMMIT      f80f052277c8
%define TOOLCHAIN      GCC5
%define OPENSSL_VER    1.1.1k

%define DBXDATE        20230314

%if %{defined rhel}
%define build_ovmf 0
%define build_aarch64 0
%ifarch x86_64
  %define build_ovmf 1
%endif
%ifarch aarch64
  %define build_aarch64 1
%endif
%define build_riscv64 0
%else
%define build_ovmf 1
%define build_aarch64 1
%define build_riscv64 1
%endif

%global softfloat_version 20180726-gitb64af41
%define cross %{defined fedora}
%define disable_werror %{defined fedora}


Name:       edk2
Version:    %{GITDATE}git%{GITCOMMIT}
Release:    3%{?dist}
Summary:    UEFI firmware for 64-bit virtual machines
License:    BSD-2-Clause-Patent and OpenSSL and MIT
URL:        http://www.tianocore.org

# The source tarball is created using following commands:
# COMMIT=bb1bba3d7767
# git archive --format=tar --prefix=edk2-$COMMIT/ $COMMIT \
# | xz -9ev >/tmp/edk2-$COMMIT.tar.xz
Source0: edk2-%{GITCOMMIT}.tar.xz
Source1: ovmf-whitepaper-c770f8c.txt
Source2: openssl-rhel-d00c3c5b8a9d6d3ea3dabfcafdf36afd61ba8bcc.tar.xz
Source3: softfloat-%{softfloat_version}.tar.xz
Source4: edk2-platforms-54306d023e7d.tar.xz
Source5: jansson-2.13.1.tar.bz2

# json description files
Source10: 50-edk2-aarch64.json
Source11: 51-edk2-aarch64-verbose.json

Source20: 50-edk2-arm-verbose.json

Source30: 30-edk2-ovmf-ia32-sb-enrolled.json
Source31: 40-edk2-ovmf-ia32-sb.json
Source32: 50-edk2-ovmf-ia32-nosb.json

Source40: 30-edk2-ovmf-x64-sb-enrolled.json
Source41: 40-edk2-ovmf-x64-sb.json
Source42: 50-edk2-ovmf-x64-microvm.json
Source43: 50-edk2-ovmf-x64-nosb.json
Source44: 60-edk2-ovmf-x64-amdsev.json
Source45: 60-edk2-ovmf-x64-inteltdx.json

# https://gitlab.com/kraxel/edk2-build-config
Source80: edk2-build.py
Source81: edk2-build.fedora
Source82: edk2-build.fedora.platforms
Source83: edk2-build.rhel-9

Source90: DBXUpdate-%{DBXDATE}.x64.bin
Source91: DBXUpdate-%{DBXDATE}.ia32.bin

Patch0001: 0001-BaseTools-do-not-build-BrotliCompress-RH-only.patch
Patch0002: 0002-MdeModulePkg-remove-package-private-Brotli-include-p.patch
Patch0003: 0003-MdeModulePkg-TerminalDxe-set-xterm-resolution-on-mod.patch
Patch0004: 0004-OvmfPkg-take-PcdResizeXterm-from-the-QEMU-command-li.patch
Patch0005: 0005-ArmVirtPkg-take-PcdResizeXterm-from-the-QEMU-command.patch
Patch0006: 0006-OvmfPkg-enable-DEBUG_VERBOSE-RHEL-only.patch
Patch0007: 0007-OvmfPkg-silence-DEBUG_VERBOSE-0x00400000-in-QemuVide.patch
Patch0008: 0008-ArmVirtPkg-silence-DEBUG_VERBOSE-0x00400000-in-QemuR.patch
Patch0009: 0009-OvmfPkg-QemuRamfbDxe-Do-not-report-DXE-failure-on-Aa.patch
Patch0010: 0010-OvmfPkg-silence-EFI_D_VERBOSE-0x00400000-in-NvmExpre.patch
Patch0011: 0011-CryptoPkg-OpensslLib-list-RHEL8-specific-OpenSSL-fil.patch
Patch0012: 0012-OvmfPkg-QemuKernelLoaderFsDxe-suppress-error-on-no-k.patch
Patch0013: 0013-SecurityPkg-Tcg2Dxe-suppress-error-on-no-swtpm-in-si.patch
Patch0014: 0014-SecurityPkg-add-TIS-sanity-check-tpm2.patch
Patch0015: 0015-SecurityPkg-add-TIS-sanity-check-tpm12.patch
Patch0016: 0016-OvmfPkg-NestedInterruptTplLib-replace-ASSERT-with-a-.patch


# python3-devel and libuuid-devel are required for building tools.
# python3-devel is also needed for varstore template generation and
# verification with "ovmf-vars-generator".
BuildRequires:  python3-devel
BuildRequires:  libuuid-devel
BuildRequires:  /usr/bin/iasl
BuildRequires:  binutils gcc git gcc-c++ make
BuildRequires:  qemu-img

%if %{build_ovmf}
# Only OVMF includes 80x86 assembly files (*.nasm*).
BuildRequires:  nasm

# Only OVMF includes the Secure Boot feature, for which we need to separate out
# the UEFI shell.
BuildRequires:  dosfstools
BuildRequires:  mtools
BuildRequires:  xorriso

# For generating the variable store template with the default certificates
# enrolled.
BuildRequires:  python3-virt-firmware >= 1.7

# endif build_ovmf
%endif

%if %{cross}
BuildRequires:  gcc-aarch64-linux-gnu
BuildRequires:  gcc-arm-linux-gnu
BuildRequires:  gcc-x86_64-linux-gnu
BuildRequires:  gcc-riscv64-linux-gnu
%endif



%package ovmf
Summary:    UEFI firmware for x86_64 virtual machines
BuildArch:  noarch
Provides:   OVMF = %{version}-%{release}
Obsoletes:  OVMF < 20180508-100.gitee3198e672e2.el7

# OVMF includes the Secure Boot and IPv6 features; it has a builtin OpenSSL
# library.
Provides:   bundled(openssl) = %{OPENSSL_VER}
License:    BSD-2-Clause-Patent and OpenSSL

# URL taken from the Maintainers.txt file.
URL:        http://www.tianocore.org/ovmf/

%description ovmf
OVMF (Open Virtual Machine Firmware) is a project to enable UEFI support for
Virtual Machines. This package contains a sample 64-bit UEFI firmware for QEMU
and KVM.


%package aarch64
Summary:    UEFI firmware for aarch64 virtual machines
BuildArch:  noarch
Provides:   AAVMF = %{version}-%{release}
Obsoletes:  AAVMF < 20180508-100.gitee3198e672e2.el7

# No Secure Boot for AAVMF yet, but we include OpenSSL for the IPv6 stack.
Provides:   bundled(openssl) = %{OPENSSL_VER}
License:    BSD-2-Clause-Patent and OpenSSL

# URL taken from the Maintainers.txt file.
URL:        https://github.com/tianocore/tianocore.github.io/wiki/ArmVirtPkg

%description aarch64
AAVMF (ARM Architecture Virtual Machine Firmware) is an EFI Development Kit II
platform that enables UEFI support for QEMU/KVM ARM Virtual Machines. This
package contains a 64-bit build.


%package tools
Summary:        EFI Development Kit II Tools
License:        BSD-2-Clause-Patent
URL:            https://github.com/tianocore/tianocore.github.io/wiki/BaseTools
%description tools
This package provides tools that are needed to
build EFI executables and ROMs using the GNU tools.

%package tools-doc
Summary:        Documentation for EFI Development Kit II Tools
BuildArch:      noarch
License:        BSD-2-Clause-Patent
URL:            https://github.com/tianocore/tianocore.github.io/wiki/BaseTools
%description tools-doc
This package documents the tools that are needed to
build EFI executables and ROMs using the GNU tools.

%description
EDK II is a modern, feature-rich, cross-platform firmware development
environment for the UEFI and PI specifications. This package contains sample
64-bit UEFI firmware builds for QEMU and KVM.


%if %{defined fedora}
%package ovmf-ia32
Summary:        Open Virtual Machine Firmware
License:        BSD-2-Clause-Patent and OpenSSL
Provides:       bundled(openssl)
BuildArch:      noarch
%description ovmf-ia32
EFI Development Kit II
Open Virtual Machine Firmware (ia32)

%package ovmf-xen
Summary:        Open Virtual Machine Firmware, Xen build
License:        BSD-2-Clause-Patent and OpenSSL
Provides:       bundled(openssl)
BuildArch:      noarch
%description ovmf-xen
EFI Development Kit II
Open Virtual Machine Firmware (Xen build)

%package ovmf-experimental
Summary:        Open Virtual Machine Firmware, experimental builds
License:        BSD-2-Clause-Patent and OpenSSL
Provides:       bundled(openssl)
BuildArch:      noarch
%description ovmf-experimental
EFI Development Kit II
Open Virtual Machine Firmware (experimental builds)

%package arm
Summary:        ARM Virtual Machine Firmware
BuildArch:      noarch
License:        BSD-2-Clause-Patent and OpenSSL
%description arm
EFI Development Kit II
ARMv7 UEFI Firmware

%package riscv64
Summary:        RISC-V Virtual Machine Firmware
BuildArch:      noarch
License:        BSD-2-Clause-Patent and OpenSSL
%description riscv64
EFI Development Kit II
RISC-V UEFI Firmware

%package ext4
Summary:        Ext4 filesystem driver
License:        BSD-2-Clause-Patent and OpenSSL
BuildArch:      noarch
%description ext4
EFI Development Kit II
Ext4 filesystem driver

%package tools-python
Summary:        EFI Development Kit II Tools
Requires:       python3
BuildArch:      noarch

%description tools-python
This package provides tools that are needed to build EFI executables
and ROMs using the GNU tools.  You do not need to install this package;
you probably want to install edk2-tools only.
# endif fedora
%endif



%prep
# We needs some special git config options that %%autosetup won't give us.
# We init the git dir ourselves, then tell %%autosetup not to blow it away.
%setup -q -n edk2-%{GITCOMMIT}
git init -q
git config core.whitespace cr-at-eol
git config am.keepcr true
# -T is passed to %%setup to not re-extract the archive
# -D is passed to %%setup to not delete the existing archive dir
%autosetup -T -D -n edk2-%{GITCOMMIT} -S git_am

cp -a -- %{SOURCE1} .
tar -C CryptoPkg/Library/OpensslLib -a -f %{SOURCE2} -x
# extract softfloat into place
tar -xf %{SOURCE3} --strip-components=1 --directory ArmPkg/Library/ArmSoftFloatLib/berkeley-softfloat-3/
tar -xf %{SOURCE4} --strip-components=1 "*/Drivers" "*/Features" "*/Platform" "*/Silicon"
tar -xf %{SOURCE5} --strip-components=1 --directory RedfishPkg/Library/JsonLib/jansson

# Done by %setup, but we do not use it for the auxiliary tarballs
chmod -Rf a+rX,u+w,g-w,o-w .

cp -a -- \
   %{SOURCE10} %{SOURCE11} \
   %{SOURCE20} \
   %{SOURCE30} %{SOURCE31} %{SOURCE32} \
   %{SOURCE40} %{SOURCE41} %{SOURCE42} %{SOURCE43} %{SOURCE44} %{SOURCE45} \
   %{SOURCE80} %{SOURCE81} %{SOURCE82} %{SOURCE83} \
   %{SOURCE90} %{SOURCE91} \
   .

%build

build_iso() {
  dir="$1"
  UEFI_SHELL_BINARY=${dir}/Shell.efi
  ENROLLER_BINARY=${dir}/EnrollDefaultKeys.efi
  UEFI_SHELL_IMAGE=uefi_shell.img
  ISO_IMAGE=${dir}/UefiShell.iso

  UEFI_SHELL_BINARY_BNAME=$(basename -- "$UEFI_SHELL_BINARY")
  UEFI_SHELL_SIZE=$(stat --format=%s -- "$UEFI_SHELL_BINARY")
  ENROLLER_SIZE=$(stat --format=%s -- "$ENROLLER_BINARY")

  # add 1MB then 10% for metadata
  UEFI_SHELL_IMAGE_KB=$((
    (UEFI_SHELL_SIZE + ENROLLER_SIZE + 1 * 1024 * 1024) * 11 / 10 / 1024
  ))

  # create non-partitioned FAT image
  rm -f -- "$UEFI_SHELL_IMAGE"
  mkdosfs -C "$UEFI_SHELL_IMAGE" -n UEFI_SHELL -- "$UEFI_SHELL_IMAGE_KB"

  # copy the shell binary into the FAT image
  export MTOOLS_SKIP_CHECK=1
  mmd   -i "$UEFI_SHELL_IMAGE"                       ::efi
  mmd   -i "$UEFI_SHELL_IMAGE"                       ::efi/boot
  mcopy -i "$UEFI_SHELL_IMAGE"  "$UEFI_SHELL_BINARY" ::efi/boot/bootx64.efi
  mcopy -i "$UEFI_SHELL_IMAGE"  "$ENROLLER_BINARY"   ::
  mdir  -i "$UEFI_SHELL_IMAGE"  -/                   ::

  # build ISO with FAT image file as El Torito EFI boot image
  mkisofs -input-charset ASCII -J -rational-rock \
    -e "$UEFI_SHELL_IMAGE" -no-emul-boot \
    -o "$ISO_IMAGE" "$UEFI_SHELL_IMAGE"
}

export EXTRA_OPTFLAGS="%{optflags}"
export EXTRA_LDFLAGS="%{__global_ldflags}"
export RELEASE_DATE="$(echo %{GITDATE} | sed -e 's|\(....\)\(..\)\(..\)|\2/\3/\1|')"

touch OvmfPkg/AmdSev/Grub/grub.efi   # dummy

%if %{build_ovmf}
%if %{defined rhel}

./edk2-build.py --config edk2-build.rhel-9 --silent --release-date "$RELEASE_DATE" -m ovmf
virt-fw-vars --input   RHEL-9/ovmf/OVMF_VARS.fd \
             --output  RHEL-9/ovmf/OVMF_VARS.secboot.fd \
             --set-dbx DBXUpdate-%{DBXDATE}.x64.bin \
             --enroll-redhat --secure-boot
build_iso RHEL-9/ovmf

%else

./edk2-build.py --config edk2-build.fedora --silent --release-date "$RELEASE_DATE" -m ovmf
./edk2-build.py --config edk2-build.fedora.platforms --silent -m x64
virt-fw-vars --input   Fedora/ovmf/OVMF_VARS.fd \
             --output  Fedora/ovmf/OVMF_VARS.secboot.fd \
             --set-dbx DBXUpdate-%{DBXDATE}.x64.bin \
             --enroll-redhat --secure-boot
virt-fw-vars --input   Fedora/ovmf-4m/OVMF_VARS.fd \
             --output  Fedora/ovmf-4m/OVMF_VARS.secboot.fd \
             --set-dbx DBXUpdate-%{DBXDATE}.x64.bin \
             --enroll-redhat --secure-boot
virt-fw-vars --input   Fedora/ovmf-ia32/OVMF_VARS.fd \
             --output  Fedora/ovmf-ia32/OVMF_VARS.secboot.fd \
             --set-dbx DBXUpdate-%{DBXDATE}.ia32.bin \
             --enroll-redhat --secure-boot
build_iso Fedora/ovmf
build_iso Fedora/ovmf-ia32

# experimental stateless builds
virt-fw-vars --input   Fedora/experimental/OVMF.stateless.fd \
             --output  Fedora/experimental/OVMF.stateless.secboot.fd \
             --set-dbx DBXUpdate-%{DBXDATE}.x64.bin \
             --enroll-redhat --secure-boot

for image in \
	Fedora/ovmf/OVMF_CODE.secboot.fd \
	Fedora/ovmf-4m/OVMF_CODE.secboot.fd \
	Fedora/experimental/OVMF.stateless.secboot.fd \
; do
	pcr="${image%.fd}.pcr"
	python3 /usr/share/doc/python3-virt-firmware/experimental/measure.py \
		--image "$image" \
		--version "%{name}-%{version}-%{release}" \
                --no-shim \
		> "$pcr"
done

%endif
%endif

%if %{build_aarch64}
%if %{defined rhel}
./edk2-build.py --config edk2-build.rhel-9 --silent --release-date "$RELEASE_DATE" -m armvirt
%else
./edk2-build.py --config edk2-build.fedora --silent --release-date "$RELEASE_DATE" -m armvirt
./edk2-build.py --config edk2-build.fedora.platforms --silent -m aa64
%endif
for raw in */aarch64/*.raw; do
    qcow2="${raw%.raw}.qcow2"
    qemu-img convert -f raw -O qcow2 -o cluster_size=4096 -S 4096 "$raw" "$qcow2"
done
%endif

%if %{build_riscv64}
./edk2-build.py --config edk2-build.fedora --silent --release-date "$RELEASE_DATE" -m riscv
./edk2-build.py --config edk2-build.fedora.platforms --silent -m riscv
%endif

%install

cp -a OvmfPkg/License.txt License.OvmfPkg.txt
cp -a CryptoPkg/Library/OpensslLib/openssl/LICENSE LICENSE.openssl
mkdir -p %{buildroot}%{_datadir}/qemu/firmware

# install the tools
mkdir -p %{buildroot}%{_bindir} \
         %{buildroot}%{_datadir}/%{name}/Conf \
         %{buildroot}%{_datadir}/%{name}/Scripts
install BaseTools/Source/C/bin/* \
        %{buildroot}%{_bindir}
install BaseTools/BinWrappers/PosixLike/LzmaF86Compress \
        %{buildroot}%{_bindir}
install BaseTools/BuildEnv \
        %{buildroot}%{_datadir}/%{name}
install BaseTools/Conf/*.template \
        %{buildroot}%{_datadir}/%{name}/Conf
install BaseTools/Scripts/GccBase.lds \
        %{buildroot}%{_datadir}/%{name}/Scripts

# install firmware images
mkdir -p %{buildroot}%{_datadir}/%{name}
%if %{defined rhel}
cp -av RHEL-9/* %{buildroot}%{_datadir}/%{name}
%else
cp -av Fedora/* %{buildroot}%{_datadir}/%{name}
%endif


%if %{build_ovmf}

# compat symlinks
mkdir -p %{buildroot}%{_datadir}/OVMF
ln -s ../%{name}/ovmf/OVMF_CODE.fd         %{buildroot}%{_datadir}/OVMF/
ln -s ../%{name}/ovmf/OVMF_CODE.secboot.fd %{buildroot}%{_datadir}/OVMF/
ln -s ../%{name}/ovmf/OVMF_VARS.fd         %{buildroot}%{_datadir}/OVMF/
ln -s ../%{name}/ovmf/OVMF_VARS.secboot.fd %{buildroot}%{_datadir}/OVMF/
ln -s ../%{name}/ovmf/UefiShell.iso        %{buildroot}%{_datadir}/OVMF/
ln -s OVMF_CODE.fd %{buildroot}%{_datadir}/%{name}/ovmf/OVMF_CODE.cc.fd

# json description files
mkdir -p %{buildroot}%{_datadir}/qemu/firmware
install -m 0644 \
        30-edk2-ovmf-x64-sb-enrolled.json \
        40-edk2-ovmf-x64-sb.json \
        50-edk2-ovmf-x64-nosb.json \
        60-edk2-ovmf-x64-amdsev.json \
        60-edk2-ovmf-x64-inteltdx.json \
        %{buildroot}%{_datadir}/qemu/firmware
%if %{defined fedora}
install -m 0644 \
        50-edk2-ovmf-x64-microvm.json \
        30-edk2-ovmf-ia32-sb-enrolled.json \
        40-edk2-ovmf-ia32-sb.json \
        50-edk2-ovmf-ia32-nosb.json \
        %{buildroot}%{_datadir}/qemu/firmware
%endif

# endif build_ovmf
%endif

%if %{build_aarch64}

# compat symlinks
mkdir -p %{buildroot}%{_datadir}/AAVMF
ln -s ../%{name}/aarch64/QEMU_EFI-pflash.raw \
  %{buildroot}%{_datadir}/AAVMF/AAVMF_CODE.verbose.fd
ln -s ../%{name}/aarch64/QEMU_EFI-silent-pflash.raw \
  %{buildroot}%{_datadir}/AAVMF/AAVMF_CODE.fd
ln -s ../%{name}/aarch64/vars-template-pflash.raw \
  %{buildroot}%{_datadir}/AAVMF/AAVMF_VARS.fd
%if %{defined fedora}
ln -s ../%{name}/arm/QEMU_EFI-pflash.raw \
   %{buildroot}%{_datadir}/AAVMF/AAVMF32_CODE.fd
%endif

# json description files
install -m 0644 \
        50-edk2-aarch64.json \
        51-edk2-aarch64-verbose.json \
        %{buildroot}%{_datadir}/qemu/firmware
%if %{defined fedora}
install -m 0644 \
        50-edk2-arm-verbose.json \
        %{buildroot}%{_datadir}/qemu/firmware
%endif

# endif build_aarch64
%endif

%if %{defined fedora}

# edk2-tools-python install
cp -R BaseTools/Source/Python %{buildroot}%{_datadir}/%{name}/Python
for i in build BPDG Ecc GenDepex GenFds GenPatchPcdTable PatchPcdValue TargetTool Trim UPT; do
echo '#!/bin/sh
export PYTHONPATH=%{_datadir}/%{name}/Python
exec python3 '%{_datadir}/%{name}/Python/$i/$i.py' "$@"' > %{buildroot}%{_bindir}/$i
  chmod +x %{buildroot}%{_bindir}/$i
done

%if 0%{?py_byte_compile:1}
# https://docs.fedoraproject.org/en-US/packaging-guidelines/Python_Appendix/#manual-bytecompilation
%py_byte_compile %{python3} %{buildroot}%{_datadir}/edk2/Python
%endif

%endif

%check
for file in %{buildroot}%{_datadir}/%{name}/*/*VARS.secboot.fd; do
    test -f "$file" || continue
    virt-fw-vars --input $file --print | grep "SecureBootEnable.*ON" || exit 1
done

%global common_files \
  %%license License.txt License.OvmfPkg.txt License-History.txt LICENSE.openssl \
  %%dir %%{_datadir}/%%{name}/ \
  %%dir %%{_datadir}/qemu \
  %%dir %%{_datadir}/qemu/firmware

%if %{build_ovmf}
%files ovmf
%common_files
%doc OvmfPkg/README
%doc ovmf-whitepaper-c770f8c.txt
%dir %{_datadir}/OVMF/
%{_datadir}/OVMF/OVMF_CODE.fd
%{_datadir}/OVMF/OVMF_CODE.secboot.fd
%{_datadir}/OVMF/OVMF_VARS.fd
%{_datadir}/OVMF/OVMF_VARS.secboot.fd
%{_datadir}/OVMF/UefiShell.iso
%dir %{_datadir}/%{name}/ovmf/
%{_datadir}/%{name}/ovmf/OVMF_CODE.fd
%{_datadir}/%{name}/ovmf/OVMF_CODE.cc.fd
%{_datadir}/%{name}/ovmf/OVMF_CODE.secboot.fd
%{_datadir}/%{name}/ovmf/OVMF_VARS.fd
%{_datadir}/%{name}/ovmf/OVMF_VARS.secboot.fd
%{_datadir}/%{name}/ovmf/OVMF.amdsev.fd
%{_datadir}/%{name}/ovmf/OVMF.inteltdx.fd
%{_datadir}/%{name}/ovmf/UefiShell.iso
%{_datadir}/%{name}/ovmf/Shell.efi
%{_datadir}/%{name}/ovmf/EnrollDefaultKeys.efi
%{_datadir}/qemu/firmware/30-edk2-ovmf-x64-sb-enrolled.json
%{_datadir}/qemu/firmware/40-edk2-ovmf-x64-sb.json
%{_datadir}/qemu/firmware/50-edk2-ovmf-x64-nosb.json
%{_datadir}/qemu/firmware/60-edk2-ovmf-x64-amdsev.json
%{_datadir}/qemu/firmware/60-edk2-ovmf-x64-inteltdx.json
%if %{defined fedora}
%{_datadir}/%{name}/ovmf/MICROVM.fd
%{_datadir}/qemu/firmware/50-edk2-ovmf-x64-microvm.json
%dir %{_datadir}/%{name}/ovmf-4m/
%{_datadir}/%{name}/ovmf-4m/OVMF_CODE.fd
%{_datadir}/%{name}/ovmf-4m/OVMF_CODE.secboot.fd
%{_datadir}/%{name}/ovmf-4m/OVMF_VARS.fd
%{_datadir}/%{name}/ovmf-4m/OVMF_VARS.secboot.fd
%{_datadir}/%{name}/ovmf/*.pcr
%{_datadir}/%{name}/ovmf-4m/*.pcr
%endif
# endif build_ovmf
%endif

%if %{build_aarch64}
%files aarch64
%common_files
%dir %{_datadir}/AAVMF/
%{_datadir}/AAVMF/AAVMF_CODE.verbose.fd
%{_datadir}/AAVMF/AAVMF_CODE.fd
%{_datadir}/AAVMF/AAVMF_VARS.fd
%dir %{_datadir}/%{name}/aarch64/
%{_datadir}/%{name}/aarch64/QEMU_EFI-pflash.*
%{_datadir}/%{name}/aarch64/QEMU_EFI-silent-pflash.*
%{_datadir}/%{name}/aarch64/vars-template-pflash.*
%{_datadir}/%{name}/aarch64/QEMU_EFI.fd
%{_datadir}/%{name}/aarch64/QEMU_EFI.silent.fd
%{_datadir}/%{name}/aarch64/QEMU_VARS.fd
%if %{defined fedora}
%{_datadir}/%{name}/aarch64/BL32_AP_MM.fd
%{_datadir}/%{name}/aarch64/QEMU_EFI.kernel.fd
%endif
%{_datadir}/qemu/firmware/50-edk2-aarch64.json
%{_datadir}/qemu/firmware/51-edk2-aarch64-verbose.json
# endif build_aarch64
%endif

%files tools
%license License.txt
%license License-History.txt
%{_bindir}/DevicePath
%{_bindir}/EfiRom
%{_bindir}/GenCrc32
%{_bindir}/GenFfs
%{_bindir}/GenFv
%{_bindir}/GenFw
%{_bindir}/GenSec
%{_bindir}/LzmaCompress
%{_bindir}/LzmaF86Compress
%{_bindir}/TianoCompress
%{_bindir}/VfrCompile
%{_bindir}/VolInfo
%dir %{_datadir}/%{name}
%{_datadir}/%{name}/BuildEnv
%{_datadir}/%{name}/Conf
%{_datadir}/%{name}/Scripts

%files tools-doc
%doc BaseTools/UserManuals/*.rtf


%if %{defined fedora}
%if %{build_ovmf}
%files ovmf-ia32
%common_files
%dir %{_datadir}/%{name}/ovmf-ia32
%{_datadir}/%{name}/ovmf-ia32/EnrollDefaultKeys.efi
%{_datadir}/%{name}/ovmf-ia32/OVMF_CODE.fd
%{_datadir}/%{name}/ovmf-ia32/OVMF_CODE.secboot.fd
%{_datadir}/%{name}/ovmf-ia32/OVMF_VARS.fd
%{_datadir}/%{name}/ovmf-ia32/OVMF_VARS.secboot.fd
%{_datadir}/%{name}/ovmf-ia32/Shell.efi
%{_datadir}/%{name}/ovmf-ia32/UefiShell.iso
%{_datadir}/qemu/firmware/30-edk2-ovmf-ia32-sb-enrolled.json
%{_datadir}/qemu/firmware/40-edk2-ovmf-ia32-sb.json
%{_datadir}/qemu/firmware/50-edk2-ovmf-ia32-nosb.json

%files ovmf-experimental
%common_files
%dir %{_datadir}/%{name}/experimental
%{_datadir}/%{name}/experimental/*.fd
%{_datadir}/%{name}/experimental/*.raw
%{_datadir}/%{name}/experimental/*.pcr

%files ovmf-xen
%common_files
%dir %{_datadir}/%{name}/xen
%{_datadir}/%{name}/xen/*.fd
%endif

%files arm
%common_files
%dir %{_datadir}/AAVMF/
%{_datadir}/AAVMF/AAVMF32_CODE.fd
%dir %{_datadir}/%{name}/arm
%{_datadir}/%{name}/arm/QEMU_EFI-pflash.raw
%{_datadir}/%{name}/arm/QEMU_EFI.fd
%{_datadir}/%{name}/arm/QEMU_VARS.fd
%{_datadir}/%{name}/arm/vars-template-pflash.raw
%{_datadir}/qemu/firmware/50-edk2-arm-verbose.json

%files riscv64
%common_files
%{_datadir}/%{name}/riscv/*.fd
%{_datadir}/%{name}/riscv/*.raw

%files ext4
%common_files
%dir %{_datadir}/%{name}/drivers
%{_datadir}/%{name}/drivers/ext4*.efi


%files tools-python
%{_bindir}/build
%{_bindir}/BPDG
%{_bindir}/Ecc
%{_bindir}/GenDepex
%{_bindir}/GenFds
%{_bindir}/GenPatchPcdTable
%{_bindir}/PatchPcdValue
%{_bindir}/TargetTool
%{_bindir}/Trim
%{_bindir}/UPT
%dir %{_datadir}/%{name}
%{_datadir}/%{name}/Python

# endif fedora
%endif


%changelog
* Mon Apr 17 2023 Gerd Hoffmann <kraxel@redhat.com> - 20230301gitf80f052277c8-3
- revert: add json files for qcow2 images.

* Thu Apr 13 2023 Gerd Hoffmann <kraxel@redhat.com> - 20230301gitf80f052277c8-2
- add StandaloneMM and ArmVirtQemuKernel builds.
- add json files for qcow2 images.
- update dbx files to 2023-03.

* Mon Mar 06 2023 Gerd Hoffmann <kraxel@redhat.com> - 20230301gitf80f052277c8-1
- update to edk2-stable202302
- update dbx database to 20220812
- add riscv64 sub-rpm

* Fri Feb 17 2023 Gerd Hoffmann <kraxel@redhat.com> - 20221117gitfff6d81270b5-14
- add sub-package with xen build (resolves: rhbz#2170730)

* Sat Feb 11 2023 Gerd Hoffmann <kraxel@redhat.com> - 20221117gitfff6d81270b5-13
- update openssl (CVE-2023-0286, CVE-2023-0215, CVE-2022-4450, CVE-2022-4304).

* Wed Feb 08 2023 Gerd Hoffmann <kraxel@redhat.com> - 20221117gitfff6d81270b5-12
- cherry-pick aarch64 bugfixes.
- set firmware build release date.
- add ext4 sub-package.

* Fri Jan 06 2023 Gerd Hoffmann <kraxel@redhat.com> - 20221117gitfff6d81270b5-10
- add experimental builds with strict nx checking.

* Mon Jan 02 2023 Gerd Hoffmann <kraxel@redhat.com> - 20221117gitfff6d81270b5-9
- revert 'make files sparse again' (resolves: rhbz#2155673).
- pick up compiler + linker flags from rpm

* Tue Dec 20 2022 Gerd Hoffmann <kraxel@redhat.com> - 20221117gitfff6d81270b5-8
- make files sparse again

* Thu Dec 15 2022 Gerd Hoffmann <kraxel@redhat.com> - 20221117gitfff6d81270b5-7
- backport https://github.com/tianocore/edk2/pull/3770

* Mon Dec 12 2022 Gerd Hoffmann <kraxel@redhat.com> - 20221117gitfff6d81270b5-6
- fix ovmf platform config (revert broken commit).
- show version information in smbios (backport).

* Mon Dec 05 2022 Gerd Hoffmann <kraxel@redhat.com> - 20221117gitfff6d81270b5-5
- rename *.json files to be more consistent.
- build script update

* Fri Dec 02 2022 Gerd Hoffmann <kraxel@redhat.com> - 20221117gitfff6d81270b5-4
- apply dbx updates

* Tue Nov 29 2022 Gerd Hoffmann <kraxel@redhat.com> - 20221117gitfff6d81270b5-3
- fix build script

* Mon Nov 28 2022 Gerd Hoffmann <kraxel@redhat.com> - 20221117gitfff6d81270b5-2
- add workaround for broken grub

* Tue Sep 20 2022 Gerd Hoffmann <kraxel@redhat.com> - 20220826gitba0e0e4c6a17-1
- update edk2 to 2022-08 stable tag.
- update openssl bundle to rhel-8.7 level.
- add stdvga fix.
- add 4MB firmware builds.

* Thu Aug 18 2022 Gerd Hoffmann <kraxel@redhat.com> - 20220526git16779ede2d36-5
- comment out patch #4 (bug 2116534 workaround)
- comment out patch #12 (bug 2114858 workaround)

* Thu Jul 21 2022 Fedora Release Engineering <releng@fedoraproject.org> - 20220526git16779ede2d36-4
- Rebuilt for https://fedoraproject.org/wiki/Fedora_37_Mass_Rebuild

* Fri Jun 10 2022 Gerd Hoffmann <kraxel@redhat.com> - 20220526git16779ede2d36-3
- swap stack fix patch.

* Wed Jun 08 2022 Gerd Hoffmann <kraxel@redhat.com> - 20220526git16779ede2d36-2
- fix PcdResizeXterm patch.
- minor specfile cleanup.
- add 0021-OvmfPkg-Sec-fix-stack-switch.patch
- Resolves rhbz#2093745

* Tue May 31 2022 Gerd Hoffmann <kraxel@redhat.com> - 20220526git16779ede2d36-1
- update to new edk2 stable tag (2022-05), refresh patches.
- add amdsev and inteltdx builds
- drop qosb

* Tue Apr 19 2022 Gerd Hoffmann <kraxel@redhat.com> - 20220221gitb24306f15daa-4
- switch to virt-firmware for secure boot key enrollment
- Stop builds on armv7 too (iasl missing).

* Thu Apr 07 2022 Gerd Hoffmann <kraxel@redhat.com> - 20220221gitb24306f15daa-3
- Fix TPM build options.
- Stop builds on i686 (iasl missing).
- Resolves rhbz#2072827

* Wed Mar 23 2022 Gerd Hoffmann <kraxel@redhat.com> - 20220221gitb24306f15daa-1
- Update to edk2-stable202202

* Thu Jan 20 2022 Fedora Release Engineering <releng@fedoraproject.org> - 20211126gitbb1bba3d7767-2
- Rebuilt for https://fedoraproject.org/wiki/Fedora_36_Mass_Rebuild

* Mon Dec 6 2021 Gerd Hoffmann <kraxel@redhat.com> - 20211126gitbb1bba3d7767-1
- Update to edk2-stable202111
- Resolves rhbz#1978966
- Resolves rhbz#2026744

* Mon Dec  6 2021 Daniel P. Berrangé <berrange@redhat.com> - 20210527gite1999b264f1f-5
- Drop glibc strcmp workaround

* Mon Nov 29 2021 Daniel P. Berrangé <berrange@redhat.com> - 20210527gite1999b264f1f-4
- Drop customized splash screen boot logo
- Temporary workaround for suspected glibc strcmp bug breaking builds in koji

* Wed Sep  1 2021 Daniel P. Berrangé <berrange@redhat.com> - 20210527gite1999b264f1f-3
- Fix qemu packaging conditionals for ELN builds

* Wed Jul 21 2021 Fedora Release Engineering <releng@fedoraproject.org> - 20210527gite1999b264f1f-2
- Rebuilt for https://fedoraproject.org/wiki/Fedora_35_Mass_Rebuild

* Tue Jul 20 2021 Cole Robinson <crobinso@redhat.com> - 20210527gite1999b264f1f-1
- Update to git snapshot
- Sync with c9s packaging

* Mon Jun 14 2021 Jiri Kucera <jkucera@redhat.com> - 20200801stable-5
- Replace genisoimage with xorriso

* Tue Jan 26 2021 Fedora Release Engineering <releng@fedoraproject.org> - 20200801stable-4
- Rebuilt for https://fedoraproject.org/wiki/Fedora_34_Mass_Rebuild

* Thu Dec 03 2020 Cole Robinson <aintdiscole@gmail.com> - 20200801stable-3
- Really fix TPM breakage (bz 1897367)

* Tue Nov 24 2020 Cole Robinson <aintdiscole@gmail.com> - 20200801stable-2
- Fix openssl usage, unbreak TPM (bz 1897367)

* Wed Sep 16 2020 Cole Robinson <crobinso@redhat.com> - 20200801stable-1
- Update to edk2 stable 202008

* Sat Sep 12 2020 Peter Robinson <pbrobinson@fedoraproject.org> - 20200201stable-6
- Tweaks for aarch64/ARMv7 builds
- Minor cleanups

* Tue Aug 04 2020 Cole Robinson <aintdiscole@gmail.com> - 20200201stable-5
- Fix build failures on rawhide

* Sat Aug 01 2020 Fedora Release Engineering <releng@fedoraproject.org> - 20200201stable-4
- Second attempt - Rebuilt for
  https://fedoraproject.org/wiki/Fedora_33_Mass_Rebuild

* Mon Jul 27 2020 Fedora Release Engineering <releng@fedoraproject.org> - 20200201stable-3
- Rebuilt for https://fedoraproject.org/wiki/Fedora_33_Mass_Rebuild

* Mon Jul 13 2020 Tom Stellard <tstellar@redhat.com> - 20200201stable-2
- Use make macros
- https://fedoraproject.org/wiki/Changes/UseMakeBuildInstallMacro

* Mon Apr 13 2020 Cole Robinson <aintdiscole@gmail.com> - 20200201stable-1
- Update to stable-202002

* Tue Jan 28 2020 Fedora Release Engineering <releng@fedoraproject.org> - 20190501stable-5
- Rebuilt for https://fedoraproject.org/wiki/Fedora_32_Mass_Rebuild

* Fri Sep 06 2019 Patrick Uiterwijk <puiterwijk@redhat.com> - 20190501stable-4
- Updated HTTP_BOOT option to new upstream value

* Wed Jul 24 2019 Fedora Release Engineering <releng@fedoraproject.org> - 20190501stable-3
- Rebuilt for https://fedoraproject.org/wiki/Fedora_31_Mass_Rebuild

* Mon Jul 15 2019 Cole Robinson <aintdiscole@gmail.com> - 20190501stable-2
- License is now BSD-2-Clause-Patent
- Re-enable secureboot enrollment
- Use qemu-ovmf-secureboot from git

* Thu Jul 11 2019 Cole Robinson <crobinso@redhat.com> - 20190501stable-1
- Update to stable-201905
- Update to openssl-1.1.1b
- Ship VARS file for ovmf-ia32 (bug 1688596)
- Ship Fedora-variant JSON "firmware descriptor files"
- Resolves rhbz#1728652

* Mon Mar 18 2019 Cole Robinson <aintdiscole@gmail.com> - 20190308stable-1
- Use YYYYMMDD versioning to fix upgrade path

* Fri Mar 15 2019 Cole Robinson <aintdiscole@gmail.com> - 201903stable-1
- Update to stable-201903
- Update to openssl-1.1.0j
- Move to python3 deps

* Thu Jan 31 2019 Fedora Release Engineering <releng@fedoraproject.org> - 20180815gitcb5f4f45ce-6
- Rebuilt for https://fedoraproject.org/wiki/Fedora_30_Mass_Rebuild

* Wed Nov 14 2018 Patrick Uiterwijk <puiterwijk@redhat.com> - 20180815gitcb5f4f45ce-5
- Add -qosb dependency on python3

* Fri Nov 9 2018 Paolo Bonzini <pbonzini@redhat.com> - 20180815gitcb5f4f45ce-4
- Fix network boot via grub (bz 1648476)

* Wed Sep 12 2018 Paolo Bonzini <pbonzini@redhat.com> - 20180815gitcb5f4f45ce-3
- Explicitly compile the scripts using py_byte_compile

* Fri Aug 31 2018 Cole Robinson <crobinso@redhat.com> - 20180815gitcb5f4f45ce-2
- Fix passing through RPM build flags (bz 1540244)

* Tue Aug 21 2018 Cole Robinson <crobinso@redhat.com> - 20180815gitcb5f4f45ce-1
- Update to edk2 git cb5f4f45ce, edk2-stable201808
- Update to qemu-ovmf-secureboot-1.1.3
- Enable TPM2 support

* Mon Jul 23 2018 Paolo Bonzini <pbonzini@redhat.com> - 20180529gitee3198e672e2-5
- Fixes for AMD SEV on OVMF_CODE.fd
- Add Provides for bundled OpenSSL

* Wed Jul 18 2018 Paolo Bonzini <pbonzini@redhat.com> - 20180529gitee3198e672e2-4
- Enable IPv6

* Thu Jul 12 2018 Fedora Release Engineering <releng@fedoraproject.org> - 20180529gitee3198e672e2-3
- Rebuilt for https://fedoraproject.org/wiki/Fedora_29_Mass_Rebuild

* Wed Jun 20 2018 Paolo Bonzini <pbonzini@redhat.com> - 20180529gitee3198e672e2-2
- Backport two bug fixes from RHEL: connect again virtio-rng devices, and
  connect consoles unconditionally in OVMF (ARM firmware already did it)

* Tue May 29 2018 Paolo Bonzini <pbonzini@redhat.com> - 20180529gitee3198e672e2-1
- Rebase to ee3198e672e2

* Tue May 01 2018 Cole Robinson <crobinso@redhat.com> - 20171011git92d07e4-7
- Bump release for new build

* Fri Mar 30 2018 Patrick Uiterwijk <puiterwijk@redhat.com> - 20171011git92d07e4-6
- Add qemu-ovmf-secureboot (qosb)
- Generate pre-enrolled Secure Boot OVMF VARS files

* Wed Mar 07 2018 Paolo Bonzini <pbonzini@redhat.com> - 20171011git92d07e4-5
- Fix GCC 8 compilation
- Replace dosfstools and mtools with qemu-img vvfat

* Wed Feb 07 2018 Fedora Release Engineering <releng@fedoraproject.org> - 20171011git92d07e4-4
- Rebuilt for https://fedoraproject.org/wiki/Fedora_28_Mass_Rebuild

* Fri Jan 19 2018 Paolo Bonzini <pbonzini@redhat.com> - 20170209git296153c5-3
- Add OpenSSL patches from Fedora
- Enable TLS_MODE

* Fri Nov 17 2017 Paolo Bonzini <pbonzini@redhat.com> - 20170209git296153c5-2
- Backport patches 19-21 from RHEL
- Add patches 22-24 to fix SEV slowness
- Add fedora conditionals

* Tue Nov 14 2017 Paolo Bonzini <pbonzini@redhat.com> - 20171011git92d07e4-1
- Import source and patches from RHEL version
- Update OpenSSL to 1.1.0e
- Refresh 0099-Tweak-the-tools_def-to-support-cross-compiling.patch

* Mon Nov 13 2017 Paolo Bonzini <pbonzini@redhat.com> - 20170209git296153c5-6
- Allow non-cross builds
- Install /usr/share/OVMF and /usr/share/AAVMF

* Wed Aug 02 2017 Fedora Release Engineering <releng@fedoraproject.org> - 20170209git296153c5-5
- Rebuilt for https://fedoraproject.org/wiki/Fedora_27_Binutils_Mass_Rebuild

* Wed Jul 26 2017 Fedora Release Engineering <releng@fedoraproject.org> - 20170209git296153c5-4
- Rebuilt for https://fedoraproject.org/wiki/Fedora_27_Mass_Rebuild

* Wed Mar 15 2017 Cole Robinson <crobinso@redhat.com> - 20170209git296153c5-3
- Ship ovmf-ia32 package (bz 1424722)

* Thu Feb 16 2017 Cole Robinson <crobinso@redhat.com> - 20170209git296153c5-2
- Update EnrollDefaultKeys patch (bz #1398743)

* Mon Feb 13 2017 Paolo Bonzini <pbonzini@redhat.com> - 20170209git296153c5-1
- Rebase to git master
- New patch 0010 fixes failure to build from source.

* Fri Feb 10 2017 Fedora Release Engineering <releng@fedoraproject.org> - 20161105git3b25ca8-2
- Rebuilt for https://fedoraproject.org/wiki/Fedora_26_Mass_Rebuild

* Sun Nov 06 2016 Cole Robinson <crobinso@redhat.com> - 20161105git3b25ca8-1
- Rebase to git master

* Fri Sep  9 2016 Tom Callaway <spot@fedoraproject.org> - 20160418gita8c39ba-5
- replace legally problematic openssl source with "hobbled" tarball

* Thu Jul 21 2016 Gerd Hoffmann <kraxel@redhat.com> - 20160418gita8c39ba-4
- Also build for armv7.

* Tue Jul 19 2016 Gerd Hoffmann <kraxel@redhat.com> 20160418gita8c39ba-3
- Update EnrollDefaultKeys patch.

* Fri Jul 8 2016 Paolo Bonzini <pbonzini@redhat.com> - 20160418gita8c39ba-2
- Distribute edk2-ovmf on aarch64

* Sat May 21 2016 Cole Robinson <crobinso@redhat.com> - 20160418gita8c39ba-1
- Distribute edk2-aarch64 on x86 (bz #1338027)

* Mon Apr 18 2016 Gerd Hoffmann <kraxel@redhat.com> 20160418gita8c39ba-0
- Update to latest git.
- Add firmware builds (FatPkg is free now).

* Mon Feb 15 2016 Cole Robinson <crobinso@redhat.com> 20151127svn18975-3
- Fix FTBFS gcc warning (bz 1307439)

* Wed Feb 03 2016 Fedora Release Engineering <releng@fedoraproject.org> - 20151127svn18975-2
- Rebuilt for https://fedoraproject.org/wiki/Fedora_24_Mass_Rebuild

* Fri Nov 27 2015 Paolo Bonzini <pbonzini@redhat.com> - 20151127svn18975-1
- Rebase to 20151127svn18975-1
- Linker script renamed to GccBase.lds

* Wed Jun 17 2015 Fedora Release Engineering <rel-eng@lists.fedoraproject.org> - 20150519svn17469-2
- Rebuilt for https://fedoraproject.org/wiki/Fedora_23_Mass_Rebuild

* Tue May 19 2015 Paolo Bonzini <pbonzini@redhat.com> - 20150519svn17469-1
- Rebase to 20150519svn17469-1
- edk2-remove-tree-check.patch now upstream

* Sat May 02 2015 Kalev Lember <kalevlember@gmail.com> - 20140724svn2670-6
- Rebuilt for GCC 5 C++11 ABI change

* Sat Aug 16 2014 Fedora Release Engineering <rel-eng@lists.fedoraproject.org> - 20140724svn2670-5
- Rebuilt for https://fedoraproject.org/wiki/Fedora_21_22_Mass_Rebuild

* Thu Jul 24 2014 Paolo Bonzini <pbonzini@redhat.com> - 20140724svn2670-1
- Rebase to 20140724svn2670-1

* Tue Jun 24 2014 Paolo Bonzini <pbonzini@redhat.com> - 20140624svn2649-1
- Use standalone .tar.xz from buildtools repo

* Tue Jun 24 2014 Paolo Bonzini <pbonzini@redhat.com> - 20140328svn15376-4
- Install BuildTools/BaseEnv

* Mon Jun 23 2014 Paolo Bonzini <pbonzini@redhat.com> - 20140328svn15376-3
- Rebase to get GCC48 configuration
- Package EDK_TOOLS_PATH as /usr/share/edk2
- Package "build" and LzmaF86Compress too, as well as the new
  tools Ecc and TianoCompress.

* Sat Jun 07 2014 Fedora Release Engineering <rel-eng@lists.fedoraproject.org> - 20131114svn14844-2
- Rebuilt for https://fedoraproject.org/wiki/Fedora_21_Mass_Rebuild

* Thu Nov 14 2013 Paolo Bonzini <pbonzini@redhat.com> - 20131114svn14844-1
- Upgrade to r14844.
- Remove upstreamed parts of patch 1.

* Fri Nov 8 2013 Paolo Bonzini <pbonzini@redhat.com> - 20130515svn14365-7
- Make BaseTools compile on ARM.

* Fri Aug 30 2013 Paolo Bonzini <pbonzini@redhat.com> - 20130515svn14365-6
- Revert previous change; firmware packages should be noarch, and building
  BaseTools twice is simply wrong.

* Mon Aug 19 2013 Kay Sievers <kay@redhat.com> - 20130515svn14365-5
- Add sub-package with EFI shell

* Sat Aug 03 2013 Fedora Release Engineering <rel-eng@lists.fedoraproject.org> - 20130515svn14365-4
- Rebuilt for https://fedoraproject.org/wiki/Fedora_20_Mass_Rebuild

* Thu May 23 2013 Dan Horák <dan[at]danny.cz> 20130515svn14365-3
- set ExclusiveArch

* Thu May 16 2013 Paolo Bonzini <pbonzini@redhat.com> 20130515svn14365-2
- Fix edk2-tools-python Requires

* Wed May 15 2013 Paolo Bonzini <pbonzini@redhat.com> 20130515svn14365-1
- Split edk2-tools-doc and edk2-tools-python
- Fix Python BuildRequires
- Remove FatBinPkg at package creation time.
- Use fully versioned dependency.
- Add comment on how to generate the sources.

* Thu May 2 2013 Paolo Bonzini <pbonzini@redhat.com> 20130502.g732d199-1
- Create.
