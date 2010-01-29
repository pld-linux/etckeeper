Summary:	Store /etc in git, mercurial, bzr or darcs
Name:		etckeeper
Version:	0.42
Release:	0.1
License:	GPL v2
Group:		Applications/System
Source0:	http://ftp.debian.org/debian/pool/main/e/etckeeper/%{name}_%{version}.tar.gz
# Source0-md5:	405716f64cad0156e060cd411e19215e
URL:		http://kitenet.net/~joey/code/etckeeper/
BuildRequires:	rpm-pythonprov
BuildRequires:	rpmbuild(macros) >= 1.219
BuildRequires:	sed >= 4.0
Requires:	git >= 1.6.1-1
Requires:	python-modules
Obsoletes:	etckeeper = snapshot
Obsoletes:	yum-etckeeper
BuildArch:	noarch
BuildRoot:	%{tmpdir}/%{name}-%{version}-root-%(id -u -n)

%description
The %{name} program is a tool to let /etc be stored in a git,
mercurial, bzr or darcs repository. It hooks into APT to automatically
commit changes made to /etc during package upgrades. It tracks file
metadata that version control systems do not normally support, but
that is important for /etc, such as the permissions of /etc/shadow.
It's quite modular and configurable, while also being simple to use if
you understand the basics of working with version control.

%prep
%setup -q -n %{name}

%{__sed} -i -e '
	s|HIGHLEVEL_PACKAGE_MANAGER=apt|HIGHLEVEL_PACKAGE_MANAGER=yum|;
	s|LOWLEVEL_PACKAGE_MANAGER=dpkg|LOWLEVEL_PACKAGE_MANAGER=rpm|;
' %{name}.conf

%build
%{__make}

%install
rm -rf $RPM_BUILD_ROOT
install -d $RPM_BUILD_ROOT/etc/cron.daily
%{__make} install \
	DESTDIR=$RPM_BUILD_ROOT

install -p debian/cron.daily $RPM_BUILD_ROOT/etc/cron.daily/%{name}

%py_ocomp $RPM_BUILD_ROOT%{py_sitescriptdir}
%py_comp $RPM_BUILD_ROOT%{py_sitescriptdir}
%py_postclean

%clean
rm -rf $RPM_BUILD_ROOT

%files
%defattr(644,root,root,755)
%doc INSTALL TODO README
%attr(755,root,root) %{_sbindir}/%{name}
%{_mandir}/man8/%{name}.8*

%dir %{_sysconfdir}/%{name}
%{_sysconfdir}/%{name}/*.d/*
# this isn't very clever and its a manaual process update.
# but it works
%config(noreplace) %verify(not md5 mtime size) %{_sysconfdir}/yum/pluginconf.d/%{name}.conf
%config(noreplace) %verify(not md5 mtime size) %{_sysconfdir}/%{name}/%{name}.conf

%attr(755,root,root) /etc/cron.daily/%{name}
/etc/bash_completion.d/%{name}
%{_libdir}/yum-plugins/%{name}.py

%{py_sitescriptdir}/bzrlib/plugins/%{name}/__init__.py[co]
