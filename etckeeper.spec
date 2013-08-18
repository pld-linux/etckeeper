# TODO:
# - Subpackages for yum and apt plugins
# - Subpackages for backends (git, etc)
Summary:	Store /etc in a SCM system (git, mercurial, bzr or darcs)
Name:		etckeeper
Version:	1.7
Release:	1
License:	GPL v2+
Group:		Applications/System
Source0:	https://github.com/joeyh/etckeeper/archive/%{version}.tar.gz
# Source0-md5:	bd6b3a79328f77d5e682c3e24f3442c5
Source1:	poldek.sh
Patch1:		use-libdir.patch
Patch2:		update-ignore.patch
URL:		http://kitenet.net/~joey/code/etckeeper/
BuildRequires:	bzr
BuildRequires:	rpm-pythonprov
BuildRequires:	rpmbuild(macros) >= 1.219
BuildRequires:	sed >= 4.0
Requires:	findutils
Requires:	mktemp
Requires:	perl-base
Requires:	sed >= 4.0
%if "%{pld_release}" != "ac"
Requires:	poldek >= 0.30.0-1.rc7.4
%endif
Suggests:	%{name}-bzr
Suggests:	bash-completion-%{name}
Suggests:	git-core >= 1.6.1-1
Obsoletes:	yum-etckeeper
%if "%{pld_release}" != "ac"
BuildArch:	noarch
%endif
BuildRoot:	%{tmpdir}/%{name}-%{version}-root-%(id -u -n)

%if "%{pld_release}" != "ac"
%define		_poldeklibdir	%{_prefix}/lib/poldek
%else
%define		_poldeklibdir	%{_libdir}/poldek
%endif

%description
The etckeeper program is a tool to let /etc be stored in a git,
mercurial, bzr or darcs repository. It hooks into APT to automatically
commit changes made to /etc during package upgrades. It tracks file
metadata that version control systems do not normally support, but
that is important for /etc, such as the permissions of /etc/shadow.
It's quite modular and configurable, while also being simple to use if
you understand the basics of working with version control.

The default backend is git, if want to use a another backend please
install the appropriate tool (mercurial, darcs or bzr). To use bzr as
backend, please also install the %{name}-bzr package.

To start using the package please read
%{_docdir}/%{name}-%{version}/README

%package bzr
Summary:	Support for bzr with etckeeper
Group:		Applications/System
Requires:	%{name} = %{version}-%{release}
Requires:	bzr

%description bzr
This package provides a bzr backend for etckeeper, if you want to use
etckeeper with bzr backend, install this package.

%package -n bash-completion-%{name}
Summary:	Bash completion routines for %{name}
Group:		Applications/Shells
Requires:	%{name} = %{version}-%{release}
Requires:	bash-completion
Obsoletes:	etckeeper-bash-completions

%description -n bash-completion-%{name}
Bash completion routines for etckeeper.

%prep
%setup -q
%patch1 -p1
%patch2 -p1
%{__sed} -i -e '
	s|HIGHLEVEL_PACKAGE_MANAGER=apt|HIGHLEVEL_PACKAGE_MANAGER=poldek|;
	s|LOWLEVEL_PACKAGE_MANAGER=dpkg|LOWLEVEL_PACKAGE_MANAGER=rpm|;
' %{name}.conf

# cleanup backups after patching
find '(' -name '*~' -o -name '*.orig' ')' -print0 | xargs -0 -r -l512 rm -f

%build
%{__make}

%install
rm -rf $RPM_BUILD_ROOT
install -d $RPM_BUILD_ROOT{/etc/cron.daily,%{_sysconfdir}/%{name},%{_localstatedir}/cache/%{name},%{_poldeklibdir}}
%{__make} install \
	etcdir=/lib \
	LOWLEVEL_PACKAGE_MANAGER=rpm \
	HIGHLEVEL_PACKAGE_MANAGER=poldek \
	INSTALL="install -p" \
	DESTDIR=$RPM_BUILD_ROOT

mv $RPM_BUILD_ROOT{/lib,%{_sysconfdir}}/%{name}/%{name}.conf
mv $RPM_BUILD_ROOT{/lib/bash_completion.d,/etc}

install -p debian/cron.daily $RPM_BUILD_ROOT/etc/cron.daily/%{name}
install -p %{SOURCE1} $RPM_BUILD_ROOT%{_poldeklibdir}/%{name}.sh

%py_ocomp $RPM_BUILD_ROOT%{py_sitescriptdir}
%py_comp $RPM_BUILD_ROOT%{py_sitescriptdir}
%py_postclean

%clean
rm -rf $RPM_BUILD_ROOT

%post
if [ $1 -gt 1 ]; then
	%{_bindir}/%{name} update-ignore
fi

%triggerin -- poldek
# add our hook as "pm command"
if [ -f /etc/poldek/poldek.conf ] && ! grep -q '^pm command = %{_poldeklibdir}/%{name}.sh' /etc/poldek/poldek.conf; then
	%{__sed} -i -re 's,#?(pm command =).*,\1 %{_poldeklibdir}/%{name}.sh,' /etc/poldek/poldek.conf
fi

%triggerun -- poldek
# remove our hook as "pm command"
if [ "$1" -eq 0 ] && [ -f /etc/poldek/poldek.conf ]; then
	%{__sed} -i -re 's,^pm command = %{_poldeklibdir}/%{name}.sh,#&,' /etc/poldek/poldek.conf
fi

%files
%defattr(644,root,root,755)
%doc INSTALL TODO README
%dir %{_sysconfdir}/%{name}
%config(noreplace) %verify(not md5 mtime size) %{_sysconfdir}/%{name}/%{name}.conf
%dir /lib/%{name}
%dir /lib/%{name}/*.d
%attr(755,root,root) /lib/%{name}/*.d/[0-9]*
/lib/%{name}/*.d/README
%attr(755,root,root) /etc/cron.daily/%{name}
%attr(755,root,root) %{_bindir}/%{name}
%{_mandir}/man8/%{name}.8*
%attr(755,root,root) %{_poldeklibdir}/%{name}.sh
%dir %attr(750,root,root) %{_localstatedir}/cache/%{name}

%files bzr
%defattr(644,root,root,755)
%dir %{py_sitescriptdir}/bzrlib
%dir %{py_sitescriptdir}/bzrlib/plugins
%dir %{py_sitescriptdir}/bzrlib/plugins/%{name}
%{py_sitescriptdir}/bzrlib/plugins/%{name}/*.py[co]
%if "%{pld_release}" != "ac"
%{py_sitescriptdir}/bzr_etckeeper-*.egg-info
%endif

%files -n bash-completion-%{name}
%defattr(644,root,root,755)
%{_sysconfdir}/bash_completion.d/%{name}
