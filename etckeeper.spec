#TODO:
# - Subpackages for yum and apt plugins
# - Subpackages for backends (git, bzr, etc)
# - Write PLD %pre and %post macros that trigger pre-install and post-install runs
# - %{py_sitescriptdir}/bzrlib/plugins also created by qbzr package?
Summary:	Store /etc in git, mercurial, bzr or darcs
Name:		etckeeper
Version:	0.61
Release:	0.1
License:	GPL v2
Group:		Applications/System
Source0:	http://ftp.debian.org/debian/pool/main/e/etckeeper/%{name}_%{version}.tar.gz
# Source0-md5:	1f5568f01ebca2546c819c8f5bdfb906
URL:		http://kitenet.net/~joey/code/etckeeper/
BuildRequires:	bzr
BuildRequires:	rpm-pythonprov
BuildRequires:	rpmbuild(macros) >= 1.219
BuildRequires:	sed >= 4.0
Requires:	perl
Requires:	python-modules
Suggests:	%{name}-bash-completions
Suggests:	git-core >= 1.6.1-1
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

%package bash-completions
Summary:	Bash completion routies for %{name}
Group:		Applications/Shells
Requires:	%{name} = %{version}-%{release}
Requires:	bash-completion

%description bash-completions
Bash completion routines for %{name}

%prep
%setup -q -n %{name}

%{__sed} -i -e '
	s|HIGHLEVEL_PACKAGE_MANAGER=apt|HIGHLEVEL_PACKAGE_MANAGER=poldek|;
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
%attr(755,root,root) %{_bindir}/%{name}

%dir %{_sysconfdir}/%{name}
%config(noreplace) %verify(not md5 mtime size) %{_sysconfdir}/%{name}/%{name}.conf
%dir %{_sysconfdir}/%{name}/*.d
%attr(755,root,root) %{_sysconfdir}/%{name}/*.d/[0-9]*
%{_sysconfdir}/%{name}/*.d/README

%attr(755,root,root) /etc/cron.daily/%{name}

%dir %{py_sitescriptdir}/bzrlib
%dir %{py_sitescriptdir}/bzrlib/plugins
%dir %{py_sitescriptdir}/bzrlib/plugins/%{name}
%{py_sitescriptdir}/bzrlib/plugins/%{name}/__init__.py[co]

%doc INSTALL TODO README
%{_mandir}/man8/%{name}.8*

%files bash-completions
%defattr(644,root,root,755)
%{_sysconfdir}/bash_completion.d/%{name}
