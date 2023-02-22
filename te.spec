Name:           te
Version:        0.1.0
Release:        1%{?dist}

Summary:        General multi-host workload execution utility
License:        Apache-2.0

URL:            https://github.com/neoave/te
Source0:        https://github.com/neoave/te/releases/download/v%{version}/te-%{version}.tar.gz
BuildArch:      noarch

BuildRequires:  python3-devel
BuildRequires:  python3-click
BuildRequires:  python3-setuptools

Requires:       python3-%{name}lib = %{version}-%{release}
Recommends:     %{name}-data = %{version}-%{release}

%description
te is general purpose multi-host workload execution utility.

%package        data
Summary:        Common `te` playbooks and files.

%description    data
The tmt Python module and command line tool implement the test
metadata specification (L1 and L2) and allows easy test execution.
This package contains the Python 3 module.

%package        -n python3-%{name}lib
Summary:        Core `te` libraries
%{?python_provide:%python_provide python3-%{name}lib}
%?python_enable_dependency_generator

%description    -n  python3-%{name}lib
The `te` Python module implementing core `te` functionality and built-in steps.

%prep
%autosetup

%build
%py3_build

%install
%py3_install

%files
%license LICENSE
%doc README.md
%{_bindir}/te

%files data
%{_datadir}/%{name}

%files -n python3-%{name}lib
%{python3_sitelib}/%{name}
%{python3_sitelib}/%{name}-%{version}-py%{python3_version}.egg-info

%changelog
* Sun Oct 02 2022 Vobornik Petr <pvoborni@redhat.com> - 0.1.0-1
- Initial package.
