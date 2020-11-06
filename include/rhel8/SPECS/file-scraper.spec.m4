# vim:ft=spec

%define file_prefix M4_FILE_PREFIX
%define file_ext M4_FILE_EXT

%define file_version M4_FILE_VERSION
%define file_release_tag %{nil}M4_FILE_RELEASE_TAG
%define file_release_number M4_FILE_RELEASE_NUMBER
%define file_build_number M4_FILE_BUILD_NUMBER
%define file_commit_ref M4_FILE_COMMIT_REF

Name:           file-scraper-core
Version:        %{file_version}
Release:        %{file_release_number}%{file_release_tag}.%{file_build_number}.git%{file_commit_ref}%{?dist}
Summary:        File scraper analysis tool
Group:          Applications/Archiving
License:        LGPLv3+
URL:            https://www.digitalpreservation.fi
Source0:        %{file_prefix}-v%{file_version}%{?file_release_tag}-%{file_build_number}-g%{file_commit_ref}.%{file_ext}
BuildRoot:      %{_tmppath}/%{name}-%{version}-%{release}-root-%(%{__id_u} -n)
BuildArch:      noarch
Requires:       python3 python3-pymediainfo python3-magic python3-opf-fido veraPDF
Requires:       python3-ffmpeg-python ffmpeg python3-click
Requires:       file >= 5.30
Requires:       python3-wand >= 0.6.1
Requires:       python3-pillow >= 6.0, python3-pillow < 6.1
BuildRequires:  python3-setuptools ImageMagick libmediainfo
Conflicts:      file-scraper-full < %{version}-%{release}, file-scraper-full > %{version}-%{release}

%package -n file-scraper-full
Summary: 	File scraper analysis tool - full installation
Group:          Applications/Archiving
Conflicts:      %{name} < %{version}-%{release}, %{name} > %{version}-%{release}
Requires:       %{name} = %{version}-%{release}
Requires:       ghostscript jhove python3-lxml dpx-validator dpres-xml-schemas
Requires:       warc-tools >= 4.8.3
Requires:       pngcheck
Requires:       libreoffice-calc libreoffice-draw libreoffice-emailmerge
Requires:       libreoffice-graphicfilter libreoffice-impress libreoffice-math
Requires:       pspp xhtml1-dtds vnu iso-schematron-xslt1
Requires:       python3-mimeparse

%description
File scraper: Basic file detector and metadata collector tools

%description -n file-scraper-full
File scraper full: File detector, metadata collector and well-formed checker tools

%prep
%setup -n %{file_prefix}-v%{file_version}%{?file_release_tag}-%{file_build_number}-g%{file_commit_ref}

%build

%install
rm -rf $RPM_BUILD_ROOT
make install3 PREFIX="%{_prefix}" ROOT="%{buildroot}"

%clean
rm -rf $RPM_BUILD_ROOT

%files -f INSTALLED_FILES
%defattr(-,root,root,-)

# 'full' only contains dependencies and is thus empty
%files -n file-scraper-full

# TODO: For now changelog must be last, because it is generated automatically
# from git log command. Appending should be fixed to happen only after %changelog macro
%changelog
