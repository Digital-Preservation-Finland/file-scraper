# vim:ft=spec

%define file_prefix M4_FILE_PREFIX
%define file_ext M4_FILE_EXT

%define file_version M4_FILE_VERSION
%define file_release_tag %{nil}M4_FILE_RELEASE_TAG
%define file_release_number M4_FILE_RELEASE_NUMBER
%define file_build_number M4_FILE_BUILD_NUMBER
%define file_commit_ref M4_FILE_COMMIT_REF

Name:           python3-file-scraper-core
Version:        %{file_version}
Release:        %{file_release_number}%{file_release_tag}.%{file_build_number}.git%{file_commit_ref}%{?dist}
Summary:        File scraper analysis tool
Group:          Applications/Archiving
License:        LGPLv3+
URL:            https://www.digitalpreservation.fi
Source0:        %{file_prefix}-v%{file_version}%{?file_release_tag}-%{file_build_number}-g%{file_commit_ref}.%{file_ext}
Source1:        file-scraper.conf
BuildRoot:      %{_tmppath}/%{name}-%{version}-%{release}-root-%(%{__id_u} -n)
BuildArch:      noarch
Requires:       python3 python3-pymediainfo python3-magic python3-opf-fido veraPDF
Requires:       python3-ffmpeg-python ffmpeg file-5.30 python36-click
Requires:       python3-wand >= 0.6.1
Requires:       python3-pillow >= 6.0, python3-pillow < 6.1
Requires:       python3-pyexiftool perl-Image-ExifTool ufraw
BuildRequires:  python3-setuptools ImageMagick libmediainfo
Conflicts:      python3-file-scraper-full < %{version}-%{release}, python3-file-scraper-full > %{version}-%{release}

%package -n python3-file-scraper-full
Summary: 	File scraper analysis tool - full installation
Group:          Applications/Archiving
Conflicts:      %{name} < %{version}-%{release}, %{name} > %{version}-%{release}
Requires:       %{name} = %{version}-%{release}
Requires:       ghostscript jhove python36-lxml python3-dpx-validator dpres-xml-schemas
Requires:       python3-warc-tools >= 4.8.3
Requires:       pngcheck
Requires:       pspp xhtml1-dtds vnu iso-schematron-xslt1
Requires:       python36-mimeparse
Requires:       python3-jpylyzer >= 2.2.0
Requires:       libreoffice7.2-full
Requires:       dbptk-developer
Requires:       python3-xml-helpers

%description
File scraper: Basic file detector and metadata collector tools

%description -n python3-file-scraper-full
File scraper full: File detector, metadata collector and well-formed checker tools

%prep
%setup -n %{file_prefix}-v%{file_version}%{?file_release_tag}-%{file_build_number}-g%{file_commit_ref}

%build

%install
rm -rf $RPM_BUILD_ROOT
make install3 PREFIX="%{_prefix}" ROOT="%{buildroot}"

mkdir -p %{buildroot}/etc/file-scraper
install -m 644 %{SOURCE1} %{buildroot}/etc/file-scraper/file-scraper.conf

# Rename executable to prevent naming collision with Python 2 RPM
sed -i 's/\/bin\/scraper$/\/bin\/scraper-3/g' INSTALLED_FILES
mv %{buildroot}%{_bindir}/scraper %{buildroot}%{_bindir}/scraper-3

%clean
rm -rf $RPM_BUILD_ROOT

%files -f INSTALLED_FILES
%defattr(-,root,root,-)
%config(noreplace) /etc/file-scraper/file-scraper.conf

# 'full' only contains dependencies and is thus empty
%files -n python3-file-scraper-full

# TODO: For now changelog must be last, because it is generated automatically
# from git log command. Appending should be fixed to happen only after %changelog macro
%changelog
