# Created by pyp2rpm-3.3.5
%global srcname te

Name:           %{srcname}
Version:        0.1.0
Release:        1%{?dist}
Summary:        General multi-host workload execution utility

License:        Apache License 2.0
URL:            https://github.com/neoave/te
Source0:        https://github.com/neoave/te/releases/download/v%{version}/te-%{version}.tar.gz
BuildArch:      noarch

BuildRequires:  python3-devel
BuildRequires:  python3-click
BuildRequires:  python3-setuptools

%description
te is general purpose multi-host workload execution utility. Its main
use cases are

%{?python_provide:%python_provide %{srcname}}

Requires:       python3-click
Requires:       python3-pyyaml

%prep
%autosetup -n %{srcname}-%{version}
# Remove bundled egg-info
rm -rf %{srcname}.egg-info

%build
%py3_build

%install
%py3_install

%files -n %{srcname}
%license LICENSE
%doc README.md
%{_bindir}/te
%{python3_sitelib}/%{srcname}
%{python3_sitelib}/%{srcname}-%{version}-py%{python3_version}.egg-info

%changelog
* Sun Oct 02 2022 Vobornik Petr <pvoborni@redhat.com> - 0.1.0-1
- Initial package.
