#! /bin/sh

: << \EOF
  For importing the hobbled OpenSSL tarball from Fedora, the following
  steps are necessary. Note that both the "sources" file format and the
  pkgs.fedoraproject.org directory structure have changed, accommodating
  SHA512 checksums.

  # in a separate directory
  fedpkg clone -a openssl
  cd openssl
  fedpkg switch-branch master
  gitk -- sources

  # the commit that added the 1.1.0e hobbled tarball is c676ac32d544,
  # subject "update to upstream version 1.1.0e"
  git checkout c676ac32d544

  # fetch the hobbled tarball and verify the checksum
  (
    set -e
    while read HASH_TYPE FN EQ HASH; do
      # remove leading and trailing parens
      FN="${FN#(*}"
      FN="${FN%*)}"
      wget \
        http://pkgs.fedoraproject.org/repo/pkgs/openssl/$FN/sha512/$HASH/$FN
    done <sources
    sha512sum -c sources
  )

  # unpack the hobbled tarball into edk2, according to
  # "OpenSSL-HOWTO.txt"; WORKSPACE stands for the root of the edk2 project
  # tree
  tar -x --xz -f openssl-1.1.0e-hobbled.tar.xz
  mv -- openssl-1.1.0e "$WORKSPACE"/CryptoPkg/Library/OpensslLib/openssl

  # update the INF files as described in "OpenSSL-HOWTO.txt", then save
  # the results as a single commit
  cd "$WORKSPACE"/CryptoPkg/Library/OpensslLib
  perl process_files.pl
  git add -A
  git commit
  git format-patch -1

Then run the patch through this script which will build a new tar file.
EOF

set -e
edk2_githash=$(awk '/^%global edk2_githash/ {print $3}' edk2.spec)
openssl_version=$(awk '/^%global openssl_version/ {print $3}' edk2.spec)
mkdir -p tianocore-openssl-${openssl_version}
(exec 3> openssl-${openssl_version}-hobbled.tar.xz
 cd tianocore-openssl-${openssl_version}
 git init .
 git config core.whitespace cr-at-eol
 git config am.keepcr true
 git am
 git archive --format=tar --prefix=tianocore-edk2-${edk2_githash}/ \
  HEAD CryptoPkg/Library/OpensslLib/ | \
  xz -9ev >&3) < $1
rm -rf tianocore-openssl-${openssl_version}
