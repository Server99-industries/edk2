%global edk2_date        20160418
%global edk2_githash     a8c39ba
%global openssl_version  1.0.2g

Name:           edk2
Version:        %{edk2_date}git%{edk2_githash}
Release:        0%{dist}
Summary:        EFI Development Kit II

Group:          Applications/Emulators
License:        BSD
URL:            http://www.tianocore.org/edk2/
Source0:        edk2-%{edk2_date}-%{edk2_githash}.tar.gz
Source1:        https://www.openssl.org/source/openssl-%{openssl_version}.tar.gz
Source3:        build-iso.sh
Source9:        update-tarball.sh

# Debug output tweaks, not for upstream
Patch0001: 0001-OvmfPkg-silence-EFI_D_VERBOSE-0x00400000-in-NvmExpre.patch
Patch0002: 0002-OvmfPkg-silence-EFI_D_VERBOSE-0x00400000-in-the-DXE-.patch
Patch0003: 0003-OvmfPkg-enable-DEBUG_VERBOSE.patch
Patch0004: 0004-OvmfPkg-increase-max-debug-message-length-to-512.patch
Patch0005: 0005-OvmfPkg-QemuVideoDxe-enable-debug-messages-in-VbeShi.patch
# Exclude EFI shell from firmware, suggested by pjones re: secureboot.
# Not for upstream, see bug 1325023#c16
Patch0006: 0006-EXCLUDE_SHELL_FROM_FD.patch
# Ship EnrollDefaultKeys application.
# Not for upstream, see bug 1325023#c16
Patch0007: 0007-OvmfPkg-EnrollDefaultKeys-application-for-enrolling-.patch
# More text console resolutions. Upstreaming attempted, but failed
Patch0008: 0008-MdeModulePkg-TerminalDxe-add-other-text-resolutions.patch
# Support qemu 'secondary-vga'. Not send upstream yet
Patch0009: 0009-pick-up-any-display-device-not-only-vga.patch

#
# actual firmware builds are done on x86_64 and aarch64,
# see all the %ifarch blocks below.
#
# edk2-tools builds are done on all x86 and arm.
# in theory they should build everywhere without much trouble, but
# in practice the edk2 build system barfs on archs it doesn't know
# (such as ppc), so lets limit things to the known-good ones.
#
ExclusiveArch:  %{ix86} x86_64 %{arm} aarch64

BuildRequires:  python
BuildRequires:  libuuid-devel
%ifarch x86_64
BuildRequires:  iasl
BuildRequires:  nasm
BuildRequires:  dosfstools
BuildRequires:  mtools
BuildRequires:  genisoimage
%endif

%description
EDK II is a development code base for creating UEFI drivers, applications
and firmware images.

%package tools
Summary:        EFI Development Kit II Tools
Group:          Development/Tools
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
BuildArch:      noarch
%description tools-doc
This package documents the tools that are needed to
build EFI executables and ROMs using the GNU tools.

%ifarch x86_64
%package ovmf
Summary:        Open Virtual Machine Firmware
License:        BSD and OpenSSL
Provides:       OVMF
BuildArch:      noarch
%description ovmf
EFI Development Kit II
Open Virtual Machine Firmware (x64)
%endif

%ifarch aarch64
%package aarch64
Summary:        AARCH64 Virtual Machine Firmware
Provides:       AAVMF
BuildArch:      noarch
%description aarch64
EFI Development Kit II
AARCH64 UEFI Firmware
%endif

%prep
%setup -q -n tianocore-%{name}-%{edk2_githash}
%autopatch -p1

# add openssl
tar -C CryptoPkg/Library/OpensslLib -xf %{SOURCE1}
(cd CryptoPkg/Library/OpensslLib/openssl-%{openssl_version};
 patch -p1 < ../EDKII_openssl-%{openssl_version}.patch)
(cd CryptoPkg/Library/OpensslLib; ./Install.sh)
cp CryptoPkg/Library/OpensslLib/openssl-*/LICENSE LICENSE.openssl

%build
source ./edksetup.sh

# compiler
CC_FLAGS="-t GCC49"

# parallel builds
JOBS="%{?_smp_mflags}"
JOBS="${JOBS#-j}"
if test "$JOBS" != ""; then
        CC_FLAGS="${CC_FLAGS} -n $JOBS"
fi

# common features
CC_FLAGS="${CC_FLAGS} -b DEBUG"
CC_FLAGS="${CC_FLAGS} --cmd-len=65536"

# ovmf features
OVMF_FLAGS="${CC_FLAGS}"
OVMF_FLAGS="${OVMF_FLAGS} -D HTTP_BOOT_ENABLE"
OVMF_FLAGS="${OVMF_FLAGS} -D NETWORK_IP6_ENABLE"

# ovmf + secure boot features
OVMF_SB_FLAGS="${OVMF_FLAGS}"
OVMF_SB_FLAGS="${OVMF_SB_FLAGS} -D SECURE_BOOT_ENABLE"
OVMF_SB_FLAGS="${OVMF_SB_FLAGS} -D SMM_REQUIRE"
OVMF_SB_FLAGS="${OVMF_SB_FLAGS} -D EXCLUDE_SHELL_FROM_FD"

# arm firmware features
ARM_FLAGS="${CC_FLAGS}"
ARM_FLAGS="${ARM_FLAGS} -D DEBUG_PRINT_ERROR_LEVEL=0x8040004F"

make -C BaseTools #%{?_smp_mflags}
sed -i -e 's/-Werror//' Conf/tools_def.txt

%ifarch x86_64
# build ovmf
mkdir -p ovmf
build ${OVMF_FLAGS} -a X64 -p OvmfPkg/OvmfPkgX64.dsc
cp Build/OvmfX64/*/FV/OVMF_*.fd ovmf
rm -rf Build/OvmfX64

# build ovmf with secure boot
build ${OVMF_SB_FLAGS} -a IA32 -a X64 -p OvmfPkg/OvmfPkgIa32X64.dsc
cp Build/Ovmf3264/*/FV/OVMF_CODE.fd ovmf/OVMF_CODE.secboot.fd

# build shell iso with EnrollDefaultKeys
cp Build/Ovmf3264/*/X64/Shell.efi ovmf
cp Build/Ovmf3264/*/X64/EnrollDefaultKeys.efi ovmf
sh %{SOURCE3} ovmf
%endif

%ifarch aarch64
# build arm/aarch64 firmware
mkdir -p aarch64
build $ARM_FLAGS -a AARCH64 -p ArmVirtPkg/ArmVirtQemu.dsc
cp Build/ArmVirtQemu-AARCH64/DEBUG_*/FV/*.fd aarch64
dd of="aarch64/QEMU_EFI-pflash.raw" if="/dev/zero" bs=1M count=64
dd of="aarch64/QEMU_EFI-pflash.raw" if="aarch64/QEMU_EFI.fd" conv=notrunc
dd of="aarch64/vars-template-pflash.raw" if="/dev/zero" bs=1M count=64
%endif

%install
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

cp -R BaseTools/Source/Python %{buildroot}%{_datadir}/%{name}/Python
for i in build BPDG Ecc GenDepex GenFds GenPatchPcdTable PatchPcdValue TargetTool Trim UPT; do
echo '#!/bin/sh
export PYTHONPATH=%{_datadir}/%{name}/Python
exec python '%{_datadir}/%{name}/Python/$i/$i.py' "$@"' > %{buildroot}%{_bindir}/$i
  chmod +x %{buildroot}%{_bindir}/$i
done

mkdir -p %{buildroot}/usr/share/%{name}
%ifarch x86_64
cp -a ovmf %{buildroot}/usr/share/%{name}
%endif
%ifarch aarch64
cp -a aarch64 %{buildroot}/usr/share/%{name}
%endif

%files tools
%{_bindir}/BootSectImage
%{_bindir}/EfiLdrImage
%{_bindir}/EfiRom
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
%dir %{_datadir}/%{name}
%{_datadir}/%{name}/BuildEnv
%{_datadir}/%{name}/Conf
%{_datadir}/%{name}/Scripts

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

%files tools-doc
%doc BaseTools/UserManuals/*.rtf

%ifarch x86_64
%files ovmf
%license OvmfPkg/License.txt
%license LICENSE.openssl
%doc OvmfPkg/README
%dir /usr/share/%{name}
%dir /usr/share/%{name}/ovmf
/usr/share/%{name}/ovmf/OVMF*.fd
/usr/share/%{name}/ovmf/*.efi
/usr/share/%{name}/ovmf/*.iso
%endif

%ifarch aarch64
%files aarch64
%license ArmVirtPkg/License.txt
%dir /usr/share/%{name}
%dir /usr/share/%{name}/aarch64
/usr/share/%{name}/aarch64/QEMU*.fd
/usr/share/%{name}/aarch64/*.raw
%endif

%changelog
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
