# vim:ft=spec

%define file_prefix M4_FILE_PREFIX
%define file_ext M4_FILE_EXT

%define file_version M4_FILE_VERSION
%define file_release_tag %{nil}M4_FILE_RELEASE_TAG
%define file_release_number M4_FILE_RELEASE_NUMBER
%define file_build_number M4_FILE_BUILD_NUMBER
%define file_commit_ref M4_FILE_COMMIT_REF

Name:           file-scraper
Version:        %{file_version}
Release:        %{file_release_number}%{file_release_tag}.%{file_build_number}.git%{file_commit_ref}%{?dist}
Summary:        File scraper analysis tool
Group:          Applications/Archiving
License:        LGPLv3+
URL:            http://www.csc.fi
Source0:        %{file_prefix}-v%{file_version}%{?file_release_tag}-%{file_build_number}-g%{file_commit_ref}.%{file_ext}
BuildRoot:      %{_tmppath}/%{name}-%{version}-%{release}-root-%(%{__id_u} -n)
BuildArch:      noarch
BuildRequires:  python-setuptools

%package light
Summary: 	Light file scraper analysis tool
Group:          Applications/Archiving
Requires:	python python2-pymediainfo python-pillow python-magic python-opf-fido
Requires:       python-wand >= 0.5.1

%package full
Summary: 	Full file scraper analysis tool
Group:          Applications/Archiving
Requires:       python python2-pymediainfo python-pillow python-magic python-opf-fido
Requires:       python-wand >= 0.5.1
Requires:       ffmpeg-python ffmpeg ghostscript jhove python-lxml veraPDF dpx-validator
Requires:       warc-tools >= 4.8.3
Requires:       pngcheck libreoffice pspp file-5.30 xhtml1-dtds vnu iso-schematron-xslt1

%description light
File detector and metadata collector

%description full
File detector, metadata collector and well-formed checker tool

%prep
%setup -n %{file_prefix}-v%{file_version}%{?file_release_tag}-%{file_build_number}-g%{file_commit_ref}

%build

%install
rm -rf $RPM_BUILD_ROOT
make install PREFIX="%{_prefix}" ROOT="%{buildroot}"

%clean
rm -rf $RPM_BUILD_ROOT

%files light -f INSTALLED_FILES
%defattr(-,root,root,-)

%files full -f INSTALLED_FILES
%defattr(-,root,root,-)

# TODO: For now changelog must be last, because it is generated automatically
# from git log command. Appending should be fixed to happen only after %changelog macro
%changelog
