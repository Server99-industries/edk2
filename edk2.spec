%global edk2_date        20171011
%global edk2_githash     92d07e4
%global openssl_version  1.1.0e
%global qosb_version     1.1.2

%define qosb_testing 0

%ifarch x86_64
%define qosb_testing 1
%endif
%if 0%{?fedora:1}
%define cross 1
%endif

%ifarch %{ix86} x86_64
%if 0%{?fedora:1}
%define build_ovmf_ia32 1
%endif
%ifarch x86_64
%define build_ovmf_x64 1
%endif
%endif
%ifarch aarch64
%define build_aavmf_aarch64 1
%endif
%ifarch %{arm}
%define build_aavmf_arm 1
%endif
%if 0%{?cross:1}
%define build_ovmf_x64 1
%define build_ovmf_ia32 1
%define build_aavmf_aarch64 1
%define build_aavmf_arm 1
%endif

Name:           edk2
Version:        %{edk2_date}git%{edk2_githash}
Release:        6%{dist}
Summary:        EFI Development Kit II

Group:          Applications/Emulators
License:        BSD
URL:            http://www.tianocore.org/edk2/
Source0:        edk2-%{edk2_date}-%{edk2_githash}.tar.xz
Source1:        openssl-%{openssl_version}-hobbled.tar.xz
Source2:        ovmf-whitepaper-c770f8c.txt
Source3:        https://github.com/puiterwijk/qemu-ovmf-secureboot/archive/v%{qosb_version}/qemu-ovmf-secureboot-%{qosb_version}.tar.gz
Source10:       hobble-openssl
Source11:       build-iso.sh
Source12:       update-tarball.sh
Source13:       openssl-patch-to-tarball.sh

# non-upstream patches
Patch0001: 0001-OvmfPkg-silence-EFI_D_VERBOSE-0x00400000-in-NvmExpre.patch
Patch0002: 0002-OvmfPkg-silence-EFI_D_VERBOSE-0x00400000-in-the-DXE-.patch
Patch0003: 0003-OvmfPkg-enable-DEBUG_VERBOSE.patch
Patch0004: 0004-OvmfPkg-increase-max-debug-message-length-to-512.patch
Patch0005: 0005-BuildEnv-override-set-C-noclobber-of-sourcing-env.patch
Patch0006: 0006-advertise-OpenSSL-on-TianoCore-splash-screen-boot-lo.patch
Patch0008: 0008-OvmfPkg-QemuVideoDxe-enable-debug-messages-in-VbeShi.patch
Patch0009: 0009-MdeModulePkg-TerminalDxe-add-other-text-resolutions-.patch
Patch0010: 0010-MdeModulePkg-TerminalDxe-set-xterm-resolution-on-mod.patch
Patch0011: 0011-OvmfPkg-take-PcdResizeXterm-from-the-QEMU-command-li.patch
Patch0012: 0012-ArmVirtPkg-QemuFwCfgLib-allow-UEFI_DRIVER-client-mod.patch
Patch0013: 0013-ArmVirtPkg-take-PcdResizeXterm-from-the-QEMU-command.patch
Patch0014: 0014-OvmfPkg-allow-exclusion-of-the-shell-from-the-firmwa.patch
Patch0015: 0015-OvmfPkg-EnrollDefaultKeys-application-for-enrolling-.patch
Patch0016: 0016-ArmPlatformPkg-introduce-fixed-PCD-for-early-hello-m.patch
Patch0017: 0017-ArmPlatformPkg-PrePeiCore-write-early-hello-message-.patch
Patch0018: 0018-ArmVirtPkg-set-early-hello-message.patch

# upstream backports
Patch0019: 0019-MdeModulePkg-PciBus-Fix-bug-that-PCI-BUS-claims-too-much-resource.patch
Patch0020: 0020-MdeModulePkg-Bds-Remove-assertion-in-BmCharToUint.patch
Patch0021: 0021-MdeModulePkg-Bds-Check-variable-name-even-if-OptionNumber-is-NULL.patch
Patch0022: 0022-OvmfPkg-make-it-a-proper-BASE-library.patch
Patch0023: 0023-OvmfPkg-create-a-separate-PlatformDebugLibIoPort-ins.patch
Patch0024: 0024-OvmfPkg-save-on-I-O-port-accesses-when-the-debug-por.patch
Patch0025: 0025-BaseTools-header.makefile-add-Wno-stringop-truncatio.patch
Patch0026: 0026-BaseTools-header.makefile-add-Wno-restrict.patch
Patch0027: 0027-BaseTools-GenVtf-silence-false-stringop-overflow-war.patch

%if 0%{?cross:1}
# Tweak the tools_def to support cross-compiling.
# These files are meant for customization, so this is not upstream too.
Patch0099: 0099-Tweak-the-tools_def-to-support-cross-compiling.patch
%endif

# openssl patches from Fedora
Patch1021: openssl-1.1.0-issuer-hash.patch
Patch1039: openssl-1.1.0-cc-reqs.patch
Patch1040: openssl-1.1.0-disable-ssl3.patch
Patch1044: openssl-1.1.0-bio-fd-preserve-nl.patch

%if 0%{?fedora:1}
#
# actual firmware builds support cross-compiling.  edk2-tools
# in theory should build everywhere without much trouble, but
# in practice the edk2 build system barfs on archs it doesn't know
# (such as ppc), so lets limit things to the known-good ones.
#
ExclusiveArch:  %{ix86} x86_64 %{arm} aarch64
%else
ExclusiveArch:  x86_64 aarch64
%endif

BuildRequires:  gcc gcc-c++
BuildRequires:  python
BuildRequires:  libuuid-devel
%if 0%{?cross:1}
BuildRequires:  gcc-aarch64-linux-gnu
BuildRequires:  gcc-arm-linux-gnu
BuildRequires:  gcc-x86_64-linux-gnu
%endif
BuildRequires:  iasl
BuildRequires:  nasm
BuildRequires:  qemu-img
BuildRequires:  genisoimage

# These are for QOSB
BuildRequires:  python3-requests
BuildRequires:  qemu
%if %{?qosb_testing}
# This is used for testing the enrollment: builds are run in a chroot, lacking
# a kernel. The testing is only performed on x86_64 for now, but we can't make
# the BuildRequires only on a specific arch, as that'd come through in the SRPM
# NOTE: The actual enrollment needs to happen in all builds for all architectures,
# because OVMF is built as noarch, which means that koji enforces that the build
# results don't actually differ per arch, and then it picks a random arches' build
# for the actual RPM.
BuildRequires:  kernel-core
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

%package qosb
Summary:        Tool to enroll secureboot
Group:          Development/Tools
Buildarch:      noarch
%description qosb
This package contains QOSB (QEMU OVMF Secure Boot), which can enroll OVMF
variable files to enforce Secure Boot.


%if 0%{?build_ovmf_x64:1}
%package ovmf
Summary:        Open Virtual Machine Firmware
License:        BSD and OpenSSL
Provides:       OVMF = %{version}-%{release}
Obsoletes:      OVMF < %{version}-%{release}
BuildArch:      noarch
%description ovmf
EFI Development Kit II
Open Virtual Machine Firmware (x64)
%endif

%if 0%{?build_ovmf_ia32:1}
%package ovmf-ia32
Summary:        Open Virtual Machine Firmware
License:        BSD and OpenSSL
BuildArch:      noarch
%description ovmf-ia32
EFI Development Kit II
Open Virtual Machine Firmware (ia32)
%endif

%if 0%{?build_aavmf_aarch64:1}
%package aarch64
Summary:        AARCH64 Virtual Machine Firmware
Provides:       AAVMF = %{version}-%{release}
Obsoletes:      AAVMF < %{version}-%{release}
BuildArch:      noarch
%description aarch64
EFI Development Kit II
AARCH64 UEFI Firmware
%endif

%if 0%{?build_aavmf_arm:1}
%package arm
Summary:        ARM Virtual Machine Firmware
BuildArch:      noarch
%description arm
EFI Development Kit II
armv7 UEFI Firmware
%endif


%prep
%setup -q -n tianocore-%{name}-%{edk2_githash}


# Ensure old shell and binary packages are not used
rm -rf EdkShellBinPkg
rm -rf EdkShellPkg
rm -rf FatBinPkg
rm -rf ShellBinPkg

cp -a -- %{SOURCE2} .

# add openssl
(cd .. && tar -xvf %{SOURCE1})
cp CryptoPkg/Library/OpensslLib/openssl/LICENSE LICENSE.openssl

# Extract QOSB
tar -xvf %{SOURCE3}
mv qemu-ovmf-secureboot-%{qosb_version}/README.md README.qosb
mv qemu-ovmf-secureboot-%{qosb_version}/LICENSE LICENSE.qosb

%autopatch -p1
base64 --decode < MdeModulePkg/Logo/Logo-OpenSSL.bmp.b64 > MdeModulePkg/Logo/Logo-OpenSSL.bmp

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
OVMF_FLAGS="${OVMF_FLAGS} -D TLS_ENABLE"
OVMF_FLAGS="${OVMF_FLAGS} -D HTTP_BOOT_ENABLE"
OVMF_FLAGS="${OVMF_FLAGS} -D NETWORK_IP6_ENABLE"
OVMF_FLAGS="${OVMF_FLAGS} -D FD_SIZE_2MB"

# ovmf + secure boot features
OVMF_SB_FLAGS="${OVMF_FLAGS}"
OVMF_SB_FLAGS="${OVMF_SB_FLAGS} -D SECURE_BOOT_ENABLE"
OVMF_SB_FLAGS="${OVMF_SB_FLAGS} -D SMM_REQUIRE"
OVMF_SB_FLAGS="${OVMF_SB_FLAGS} -D EXCLUDE_SHELL_FROM_FD"

# arm firmware features
ARM_FLAGS="${CC_FLAGS}"
ARM_FLAGS="${ARM_FLAGS} -D DEBUG_PRINT_ERROR_LEVEL=0x8040004F"

unset MAKEFLAGS
make -C BaseTools #%{?_smp_mflags}
sed -i -e 's/-Werror//' Conf/tools_def.txt


%if 0%{?cross:1}
export GCC49_IA32_PREFIX="x86_64-linux-gnu-"
export GCC49_X64_PREFIX="x86_64-linux-gnu-"
export GCC49_AARCH64_PREFIX="aarch64-linux-gnu-"
export GCC49_ARM_PREFIX="arm-linux-gnu-"
%endif

# build ovmf (x64)
%if 0%{?build_ovmf_x64:1}
mkdir -p ovmf
build ${OVMF_FLAGS} -a X64 -p OvmfPkg/OvmfPkgX64.dsc
cp Build/OvmfX64/*/FV/OVMF_*.fd ovmf/
rm -rf Build/OvmfX64

# build ovmf (x64) with secure boot
build ${OVMF_SB_FLAGS} -a IA32 -a X64 -p OvmfPkg/OvmfPkgIa32X64.dsc
cp Build/Ovmf3264/*/FV/OVMF_CODE.fd ovmf/OVMF_CODE.secboot.fd

# build ovmf (x64) shell iso with EnrollDefaultKeys
cp Build/Ovmf3264/*/X64/Shell.efi ovmf/
cp Build/Ovmf3264/*/X64/EnrollDefaultKeys.efi ovmf
sh %{_sourcedir}/build-iso.sh ovmf/

# Build enrolled VARS file
python3 qemu-ovmf-secureboot-%{qosb_version}/ovmf-vars-generator \
	--qemu-binary /usr/bin/qemu-system-x86_64 \
	--skip-testing \
	--ovmf-binary ovmf/OVMF_CODE.secboot.fd \
	--ovmf-template-vars ovmf/OVMF_VARS.fd \
	--uefi-shell-iso ovmf/UefiShell.iso \
	ovmf/OVMF_VARS.secboot.fd
%endif


# build ovmf-ia32
%if 0%{?build_ovmf_ia32:1}
mkdir -p ovmf-ia32
build ${OVMF_FLAGS} -a IA32 -p OvmfPkg/OvmfPkgIa32.dsc
cp Build/OvmfIa32/*/FV/OVMF_CODE.fd ovmf-ia32/
rm -rf Build/OvmfIa32

# build ovmf-ia32 with secure boot
build ${OVMF_SB_FLAGS} -a IA32 -p OvmfPkg/OvmfPkgIa32.dsc
cp Build/OvmfIa32/*/FV/OVMF_CODE.fd ovmf-ia32/OVMF_CODE.secboot.fd

# build ovmf-ia32 shell iso with EnrollDefaultKeys
cp Build/OvmfIa32/*/IA32/Shell.efi ovmf-ia32/Shell.efi
cp Build/OvmfIa32/*/IA32/EnrollDefaultKeys.efi ovmf-ia32/EnrollDefaultKeys.efi
sh %{_sourcedir}/build-iso.sh ovmf-ia32/
%endif


# build aarch64 firmware
%if 0%{?build_aavmf_aarch64:1}
mkdir -p aarch64
build $ARM_FLAGS -a AARCH64 -p ArmVirtPkg/ArmVirtQemu.dsc
cp Build/ArmVirtQemu-AARCH64/DEBUG_*/FV/*.fd aarch64
dd of="aarch64/QEMU_EFI-pflash.raw" if="/dev/zero" bs=1M count=64
dd of="aarch64/QEMU_EFI-pflash.raw" if="aarch64/QEMU_EFI.fd" conv=notrunc
dd of="aarch64/vars-template-pflash.raw" if="/dev/zero" bs=1M count=64
%endif


# build aarch64 firmware
%if 0%{?build_aavmf_arm:1}
mkdir -p arm
build $ARM_FLAGS -a ARM -p ArmVirtPkg/ArmVirtQemu.dsc
cp Build/ArmVirtQemu-ARM/DEBUG_*/FV/*.fd arm
dd of="arm/QEMU_EFI-pflash.raw" if="/dev/zero" bs=1M count=64
dd of="arm/QEMU_EFI-pflash.raw" if="arm/QEMU_EFI.fd" conv=notrunc
dd of="arm/vars-template-pflash.raw" if="/dev/zero" bs=1M count=64
%endif

%check
%if 0%{?build_ovmf_x64:1}
%if 0%{?qosb_testing}
# Verify enrolled VARS file
python3 qemu-ovmf-secureboot-%{qosb_version}/ovmf-vars-generator \
	--qemu-binary /usr/bin/qemu-system-x86_64 \
	--skip-enrollment \
	--print-output \
	--ovmf-binary ovmf/OVMF_CODE.secboot.fd \
	--ovmf-template-vars ovmf/OVMF_VARS.fd \
	--uefi-shell-iso ovmf/UefiShell.iso \
	--no-download \
	--kernel-path `rpm -ql kernel-core | grep "\/vmlinuz$" -m 1` \
	ovmf/OVMF_VARS.secboot.fd
%endif
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
%if 0%{?build_ovmf_x64:1}
cp -a ovmf %{buildroot}/usr/share/%{name}
# Libvirt hardcodes this directory name
mkdir %{buildroot}/usr/share/OVMF
ln -sf ../%{name}/ovmf/OVMF_CODE.fd                %{buildroot}/usr/share/OVMF
ln -sf ../%{name}/ovmf/OVMF_CODE.secboot.fd        %{buildroot}/usr/share/OVMF
ln -sf ../%{name}/ovmf/OVMF_VARS.fd                %{buildroot}/usr/share/OVMF
ln -sf ../%{name}/ovmf/OVMF_VARS.secboot.fd        %{buildroot}/usr/share/OVMF
ln -sf ../%{name}/ovmf/UefiShell.iso               %{buildroot}/usr/share/OVMF
%endif
%if 0%{?build_ovmf_ia32:1}
cp -a ovmf-ia32 %{buildroot}/usr/share/%{name}
%endif
%if 0%{?build_aavmf_aarch64:1}
cp -a aarch64 %{buildroot}/usr/share/%{name}
# Libvirt hardcodes this directory name
mkdir %{buildroot}/usr/share/AAVMF
ln -sf ../%{name}/aarch64/QEMU_EFI-pflash.raw      %{buildroot}/usr/share/AAVMF/AAVMF_CODE.fd
ln -sf ../%{name}/aarch64/vars-template-pflash.raw %{buildroot}/usr/share/AAVMF/AAVMF_VARS.fd
%endif
%if 0%{?build_aavmf_arm:1}
cp -a arm %{buildroot}/usr/share/%{name}
ln -sf ../%{name}/arm/QEMU_EFI-pflash.raw          %{buildroot}/usr/share/AAVMF/AAVMF32_CODE.fd
%endif

install qemu-ovmf-secureboot-%{qosb_version}/ovmf-vars-generator %{buildroot}%{_bindir}


%files tools
%license License.txt
%{_bindir}/BootSectImage
%{_bindir}/Brotli
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

%files qosb
%license LICENSE.qosb
%doc README.qosb
%{_bindir}/ovmf-vars-generator

%if 0%{?build_ovmf_x64:1}
%files ovmf
%license OvmfPkg/License.txt
%license LICENSE.openssl
%doc OvmfPkg/README
%doc ovmf-whitepaper-c770f8c.txt
%dir /usr/share/%{name}
%dir /usr/share/%{name}/ovmf
/usr/share/%{name}/ovmf/OVMF*.fd
/usr/share/%{name}/ovmf/*.efi
/usr/share/%{name}/ovmf/*.iso
/usr/share/OVMF
%endif

%if 0%{?build_ovmf_ia32:1}
%files ovmf-ia32
%license OvmfPkg/License.txt
%license LICENSE.openssl
%doc OvmfPkg/README
%doc ovmf-whitepaper-c770f8c.txt
%dir /usr/share/%{name}
%dir /usr/share/%{name}/ovmf-ia32
/usr/share/%{name}/ovmf-ia32/OVMF*.fd
/usr/share/%{name}/ovmf-ia32/*.efi
/usr/share/%{name}/ovmf-ia32/*.iso
%endif

%if 0%{?build_aavmf_aarch64:1}
%files aarch64
%license OvmfPkg/License.txt
%license LICENSE.openssl
%dir /usr/share/%{name}
%dir /usr/share/%{name}/aarch64
/usr/share/%{name}/aarch64/QEMU*.fd
/usr/share/%{name}/aarch64/*.raw
/usr/share/AAVMF/AAVMF_*
%endif

%if 0%{?build_aavmf_arm:1}
%files arm
%license OvmfPkg/License.txt
%license LICENSE.openssl
%dir /usr/share/%{name}
%dir /usr/share/%{name}/arm
/usr/share/%{name}/arm/QEMU*.fd
/usr/share/%{name}/arm/*.raw
/usr/share/AAVMF/AAVMF32_*
%endif


%changelog
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
