# vim:ft=spec

%define file_prefix M4_FILE_PREFIX
%define file_ext M4_FILE_EXT

%define file_version M4_FILE_VERSION
%define file_release_tag %{nil}M4_FILE_RELEASE_TAG
%define file_release_number M4_FILE_RELEASE_NUMBER
%define file_build_number M4_FILE_BUILD_NUMBER
%define file_commit_ref M4_FILE_COMMIT_REF

# The name of the "full" subpackage, for dependencies
%global full_sp_name python3-file-scraper-full
# The name of the "core" subpackage, for dependencies
%global core_sp_name python3-file-scraper-core

Name:           python-file-scraper
Version:        %{file_version}
Release:        %{file_release_number}%{file_release_tag}.%{file_build_number}.git%{file_commit_ref}%{?dist}
Summary:        File scraper analysis tool
License:        LGPLv3+
URL:            https://www.digitalpreservation.fi
Source0:        %{file_prefix}-v%{file_version}%{?file_release_tag}-%{file_build_number}-g%{file_commit_ref}.%{file_ext}
Source1:        file-scraper.conf
BuildArch:      noarch
BuildRequires:  python3-devel
BuildRequires:  pyproject-rpm-macros
BuildRequires:  %{py3_dist pip}
BuildRequires:  %{py3_dist wheel}
BuildRequires:  %{py3_dist setuptools}
BuildRequires:  %{py3_dist setuptools-scm}
BuildRequires:  ImageMagick
BuildRequires:  libmediainfo

%global _description %{expand:
File scraper: Basic file detector and metadata collector tools
}

%description %_description

%package -n %{core_sp_name}
Summary:        File scraper analysis tool
Requires:       %{py3_dist ffmpeg-python}
Requires:       %{py3_dist opf-fido}
Requires:       %{py3_dist xml-helpers}
# Specific minimum version needed for the class UnknownValue
Requires:       %{py3_dist dpres-file-formats} >= 1.1.0
Requires:       %{py3_dist dpx-validator}
Requires:       /usr/bin/ffmpeg
Requires:       perl-Image-ExifTool
# Exiftool can process zlib-compressed PDFs better with package installed,
# see https://jira.ci.csc.fi/browse/KDKPAS-3632
Requires:       perl-IO-Compress
Requires:       veraPDF
Conflicts:      %{full_sp_name} < %{version}-%{release}, %{full_sp_name} > %{version}-%{release}
# The ffmpeg-free package in EPEL does not have all the codecs we need for
# validation. The ffmpeg package from RPMFusion should be installed with
# file-scraper.
Conflicts:	ffmpeg-free

%description -n %{core_sp_name} %_description

%package -n %{full_sp_name}
Summary:        File scraper analysis tool - full installation
Conflicts:      %{core_sp_name} < %{version}-%{release}, %{core_sp_name} > %{version}-%{release}
Requires:       %{core_sp_name} = %{version}-%{release}
Requires:       %{py3_dist warctools}
Requires:       dpres-xml-schemas
Requires:       dbptk-developer
Requires:       jhove
Requires:       pngcheck
Requires:       pspp
Requires:       vnu
Requires:       xhtml1-dtds
Requires:       iso-schematron-xslt1
Requires:       libreoffice24.8-full
Conflicts:      ffmpeg-free
Requires:       warchaeology

# Manually packaged Ghostscript and file with fixes not found in stock RHEL9
Requires:       ghostscript-10.06
Requires:       file-5.45

%description -n %{full_sp_name}
File scraper full: File detector, metadata collector and well-formed checker tools

%prep
%autosetup -n %{file_prefix}-v%{file_version}%{?file_release_tag}-%{file_build_number}-g%{file_commit_ref}

%build
export SETUPTOOLS_SCM_PRETEND_VERSION_FOR_FILE_SCRAPER=%{file_version}
%pyproject_wheel

%install
%pyproject_install
%pyproject_save_files file_scraper

mkdir -p %{buildroot}/etc/file-scraper
install -m 644 %{SOURCE1} %{buildroot}/etc/file-scraper/file-scraper.conf

# TODO: executables with "-3" suffix are added to maintain compatibility with our systems.
# executables with "-3" suffix should be deprecated.
cp %{buildroot}%{_bindir}/scraper %{buildroot}%{_bindir}/scraper-3

%files -n %{core_sp_name} -f %{pyproject_files}
%{_bindir}/scraper*
%config(noreplace) /etc/file-scraper/file-scraper.conf

# 'full' only contains dependencies and is thus empty
%files -n %{full_sp_name}

# TODO: For now changelog must be last, because it is generated automatically
# from git log command. Appending should be fixed to happen only after %changelog macro
%changelog
