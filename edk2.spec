%global SVNDATE   20151127
%global SVNREV    18975

Name:           edk2
Version:        %{SVNDATE}svn%{SVNREV}
Release:        2%{?dist}
Summary:        EFI Development Kit II

# There are no formal releases from upstream.
# Tarballs are created with:

# svn export -r ${SVNREV} \
#     https://svn.code.sf.net/p/edk2/code/trunk/edk2/BaseTools edk2-buildtools-r${SVNREV}
# rm -rf edk2-buildtools-r${SVNREV}/Bin
# tar -cv edk2-buildtools-r${SVNREV} | xz -6 > edk2-buildtools-r${SVNREV}.tar.xz
Source0:        edk2-buildtools-r%{SVNREV}.tar.xz
Patch1:         basetools-arm.patch

License:        BSD
Group:          Applications/Emulators
URL:            http://sourceforge.net/apps/mediawiki/tianocore/index.php?title=EDK2

# We need to build tools everywhere, but how is still an open question
# https://bugzilla.redhat.com/show_bug.cgi?id=992180
ExclusiveArch:  %{ix86} x86_64 %{arm}

BuildRequires:  python2-devel
BuildRequires:  libuuid-devel

Requires:       edk2-tools%{?_isa} = %{version}-%{release}
Requires:       edk2-tools-doc%{?_isa} = %{version}-%{release}

%description
EDK II is a development code base for creating UEFI drivers, applications
and firmware images.

%package tools
Summary:        EFI Development Kit II Tools
Group:          Development/Tools
Requires:       edk2-tools-python = %{version}-%{release}

%description tools
This package provides tools that are needed to
build EFI executables and ROMs using the GNU tools.

%package tools-python
Summary:        EFI Development Kit II Tools
Group:          Development/Tools
Requires:       python
BuildArch:      noarch

%description tools-python
This package provides tools that are needed to build EFI executables
and ROMs using the GNU tools.  You do not need to install this package;
you probably want to install edk2-tools only.

%package tools-doc
Summary:        Documentation for EFI Development Kit II Tools
Group:          Development/Tools

%description tools-doc
This package documents the tools that are needed to
build EFI executables and ROMs using the GNU tools.

%prep
%setup -q -n edk2-buildtools-r%{SVNREV}
%patch1 -p1

%build
export WORKSPACE=`pwd`

# Build is broken if MAKEFLAGS contains -j option.
unset MAKEFLAGS
make

%install
mkdir -p %{buildroot}%{_bindir}
install \
        Source/C/bin/BootSectImage \
        Source/C/bin/EfiLdrImage \
        Source/C/bin/EfiRom \
        Source/C/bin/GenCrc32 \
        Source/C/bin/GenFfs \
        Source/C/bin/GenFv \
        Source/C/bin/GenFw \
        Source/C/bin/GenPage \
        Source/C/bin/GenSec \
        Source/C/bin/GenVtf \
        Source/C/bin/GnuGenBootSector \
        Source/C/bin/LzmaCompress \
        BinWrappers/PosixLike/LzmaF86Compress \
        Source/C/bin/Split \
        Source/C/bin/TianoCompress \
        Source/C/bin/VfrCompile \
        Source/C/bin/VolInfo \
        %{buildroot}%{_bindir}

ln -f %{buildroot}%{_bindir}/GnuGenBootSector \
        %{buildroot}%{_bindir}/GenBootSector

mkdir -p %{buildroot}%{_datadir}/%{name}
install \
        BuildEnv \
        %{buildroot}%{_datadir}/%{name}

mkdir -p %{buildroot}%{_datadir}/%{name}/Conf
install \
        Conf/build_rule.template \
        Conf/tools_def.template \
        Conf/target.template \
        %{buildroot}%{_datadir}/%{name}/Conf

mkdir -p %{buildroot}%{_datadir}/%{name}/Scripts
install \
        Scripts/GccBase.lds \
        %{buildroot}%{_datadir}/%{name}/Scripts

cp -R Source/Python %{buildroot}%{_datadir}/%{name}/Python

find %{buildroot}%{_datadir}/%{name}/Python -name "*.pyd" | xargs rm

for i in build BPDG Ecc GenDepex GenFds GenPatchPcdTable PatchPcdValue TargetTool Trim UPT; do
  echo '#!/bin/sh
PYTHONPATH=%{_datadir}/%{name}/Python
export PYTHONPATH
exec python '%{_datadir}/%{name}/Python/$i/$i.py' "$@"' > %{buildroot}%{_bindir}/$i
  chmod +x %{buildroot}%{_bindir}/$i
done

%files tools
%{_bindir}/BootSectImage
%{_bindir}/EfiLdrImage
%{_bindir}/EfiRom
%{_bindir}/GenBootSector
%{_bindir}/GenCrc32
%{_bindir}/GenFfs
%{_bindir}/GenFv
%{_bindir}/GenFw
%{_bindir}/GenPage
%{_bindir}/GenSec
%{_bindir}/GenVtf
%{_bindir}/GnuGenBootSector
%{_bindir}/LzmaCompress
%{_bindir}/LzmaF86Compress
%{_bindir}/Split
%{_bindir}/TianoCompress
%{_bindir}/VfrCompile
%{_bindir}/VolInfo
%{_datadir}/%{name}/BuildEnv
%{_datadir}/%{name}/Conf/
%{_datadir}/%{name}/Scripts/

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
%{_datadir}/%{name}/Python/

%files tools-doc
%doc UserManuals/BootSectImage_Utility_Man_Page.rtf
%doc UserManuals/Build_Utility_Man_Page.rtf
%doc UserManuals/EfiLdrImage_Utility_Man_Page.rtf
%doc UserManuals/EfiRom_Utility_Man_Page.rtf
%doc UserManuals/GenBootSector_Utility_Man_Page.rtf
%doc UserManuals/GenCrc32_Utility_Man_Page.rtf
%doc UserManuals/GenDepex_Utility_Man_Page.rtf
%doc UserManuals/GenFds_Utility_Man_Page.rtf
%doc UserManuals/GenFfs_Utility_Man_Page.rtf
%doc UserManuals/GenFv_Utility_Man_Page.rtf
%doc UserManuals/GenFw_Utility_Man_Page.rtf
%doc UserManuals/GenPage_Utility_Man_Page.rtf
%doc UserManuals/GenPatchPcdTable_Utility_Man_Page.rtf
%doc UserManuals/GenSec_Utility_Man_Page.rtf
%doc UserManuals/GenVtf_Utility_Man_Page.rtf
%doc UserManuals/LzmaCompress_Utility_Man_Page.rtf
%doc UserManuals/PatchPcdValue_Utility_Man_Page.rtf
%doc UserManuals/SplitFile_Utility_Man_Page.rtf
%doc UserManuals/TargetTool_Utility_Man_Page.rtf
%doc UserManuals/TianoCompress_Utility_Man_Page.rtf
%doc UserManuals/Trim_Utility_Man_Page.rtf
%doc UserManuals/VfrCompiler_Utility_Man_Page.rtf
%doc UserManuals/VolInfo_Utility_Man_Page.rtf

%changelog
* Wed Feb 03 2016 Fedora Release Engineering <releng@fedoraproject.org> - 20151127svn18975-2
- Rebuilt for https://fedoraproject.org/wiki/Fedora_24_Mass_Rebuild

* Tue Nov 27 2015 Paolo Bonzini <pbonzini@redhat.com> - 20151127svn18975-1
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
