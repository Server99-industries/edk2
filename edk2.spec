%define SVNDATE 20130515
%define SVNREV  14365

# More subpackages to come once licensing issues are fixed
Name:		edk2
Version:	%{SVNDATE}svn%{SVNREV}
Release:	2%{?dist}
Summary:	EFI Development Kit II

# There are no formal releases from upstream.
# Tarballs are created with:

# svn export -r ${SVNREV} \
#     https://edk2.svn.sourceforge.net/svnroot/edk2/trunk/edk2 edk2-r${SVNREV}
# rm -rf edk2-r${SVNREV}/BaseTools/Bin
# rm -rf edk2-r${SVNREV}/ShellBinPkg
# rm -rf edk2-r${SVNREV}/FatBinPkg
# tar -cv edk2-r${SVNREV} | xz -6 > edk2-r${SVNREV}.tar.xz
Source0:	edk2-r%{SVNREV}.tar.xz

License:	BSD
Group:		Applications/Emulators
URL:		http://sourceforge.net/apps/mediawiki/tianocore/index.php?title=EDK2

BuildRequires:	python2-devel
BuildRequires:	libuuid-devel

Requires:	edk2-tools%{?_isa} = %{version}-%{release}

%description
This package provides tools that are needed to build EFI executables
and ROMs using the GNU tools.


%package tools
Summary:	EFI Development Kit II Tools
Group:		Development/Tools
Requires:	edk2-tools-python = %{version}-%{release}

%description tools
This package provides tools that are needed to
build EFI executables and ROMs using the GNU tools.

%package tools-python
Summary:	EFI Development Kit II Tools
Group:		Development/Tools
Requires:	python
BuildArch:      noarch

%description tools-python
This package provides tools that are needed to build EFI executables
and ROMs using the GNU tools.  You do not need to install this package;
you probably want to install edk2-tools only.

%package tools-doc
Summary:	Documentation for EFI Development Kit II Tools
Group:		Development/Tools

%description tools-doc
This package documents the tools that are needed to
build EFI executables and ROMs using the GNU tools.

%prep
%setup -q -n %{name}-r%{SVNREV}

%build
source ./edksetup.sh

make -C $WORKSPACE/BaseTools

%install
mkdir -p %{buildroot}%{_bindir}
install	\
	BaseTools/Source/C/bin/BootSectImage \
	BaseTools/Source/C/bin/EfiLdrImage \
	BaseTools/Source/C/bin/EfiRom \
	BaseTools/Source/C/bin/GenCrc32 \
	BaseTools/Source/C/bin/GenFfs \
	BaseTools/Source/C/bin/GenFv \
	BaseTools/Source/C/bin/GenFw \
	BaseTools/Source/C/bin/GenPage \
	BaseTools/Source/C/bin/GenSec \
	BaseTools/Source/C/bin/GenVtf \
	BaseTools/Source/C/bin/GnuGenBootSector \
	BaseTools/Source/C/bin/LzmaCompress \
	BaseTools/Source/C/bin/Split \
	BaseTools/Source/C/bin/VfrCompile \
	BaseTools/Source/C/bin/VolInfo \
	%{buildroot}%{_bindir}

ln -f %{buildroot}%{_bindir}/GnuGenBootSector \
	%{buildroot}%{_bindir}/GenBootSector

mkdir -p %{buildroot}%{_datadir}/%{name}
cp -R BaseTools/Source/Python %{buildroot}%{_datadir}/%{name}/Python

find %{buildroot}%{_datadir}/%{name}/Python -name "*.pyd" | xargs rm

for i in BPDG GenDepex GenFds GenPatchPcdTable PatchPcdValue TargetTool Trim UPT; do
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
%{_bindir}/Split
%{_bindir}/VfrCompile
%{_bindir}/VolInfo

%files tools-python
%{_bindir}/BPDG
%{_bindir}/GenDepex
%{_bindir}/GenFds
%{_bindir}/GenPatchPcdTable
%{_bindir}/PatchPcdValue
%{_bindir}/TargetTool
%{_bindir}/Trim
%{_bindir}/UPT
%{_datadir}/%{name}/Python/

%files tools-doc
%doc BaseTools/UserManuals/BootSectImage_Utility_Man_Page.rtf
%doc BaseTools/UserManuals/EfiLdrImage_Utility_Man_Page.rtf
%doc BaseTools/UserManuals/EfiRom_Utility_Man_Page.rtf
%doc BaseTools/UserManuals/GenBootSector_Utility_Man_Page.rtf
%doc BaseTools/UserManuals/GenCrc32_Utility_Man_Page.rtf
%doc BaseTools/UserManuals/GenDepex_Utility_Man_Page.rtf
%doc BaseTools/UserManuals/GenFds_Utility_Man_Page.rtf
%doc BaseTools/UserManuals/GenFfs_Utility_Man_Page.rtf
%doc BaseTools/UserManuals/GenFv_Utility_Man_Page.rtf
%doc BaseTools/UserManuals/GenFw_Utility_Man_Page.rtf
%doc BaseTools/UserManuals/GenPage_Utility_Man_Page.rtf
%doc BaseTools/UserManuals/GenPatchPcdTable_Utility_Man_Page.rtf
%doc BaseTools/UserManuals/GenSec_Utility_Man_Page.rtf
%doc BaseTools/UserManuals/GenVtf_Utility_Man_Page.rtf
%doc BaseTools/UserManuals/LzmaCompress_Utility_Man_Page.rtf
%doc BaseTools/UserManuals/PatchPcdValue_Utility_Man_Page.rtf
%doc BaseTools/UserManuals/SplitFile_Utility_Man_Page.rtf
%doc BaseTools/UserManuals/TargetTool_Utility_Man_Page.rtf
%doc BaseTools/UserManuals/Trim_Utility_Man_Page.rtf
%doc BaseTools/UserManuals/VfrCompiler_Utility_Man_Page.rtf
%doc BaseTools/UserManuals/VolInfo_Utility_Man_Page.rtf

%changelog
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
