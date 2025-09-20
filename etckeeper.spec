# TODO:
# - Subpackages for yum and apt plugins
# - Subpackages for backends (darcs, git, hg)
#
# Conditional build:
%bcond_with	bzr		# build bzr subpackage
#
Summary:	Store /etc in a SCM system (git, mercurial, bzr or darcs)
Name:		etckeeper
Version:	1.18.23
Release:	2
License:	GPL v2+
Group:		Applications/System
#Source0:	https://git.joeyh.name/index.cgi/etckeeper.git/snapshot/%{name}-%{version}.tar.gz
Source0:	https://ftp.debian.org/debian/pool/main/e/etckeeper/%{name}_%{version}.orig.tar.gz
# Source0-md5:	075fcafc6bd7ac0d42e20743f31517d9
Source1:	pre-install.sh
Source2:	post-install.sh
Source3:	https://ftp.debian.org/debian/pool/main/e/etckeeper/etckeeper_%{version}-2.debian.tar.xz
# Source3-md5:	fa217e124e12f4a5752ad03f36618ae2
Patch1:		use-libdir.patch
Patch2:		update-ignore.patch
URL:		http://etckeeper.branchable.com/
%{?with_bzr:BuildRequires:	bzr}
BuildRequires:	python-devel
BuildRequires:	rpm-pythonprov
BuildRequires:	rpmbuild(macros) >= 1.717
BuildRequires:	sed >= 4.0
Requires:	diffutils
Requires:	findutils
Requires:	mktemp
Requires:	perl-base
Requires:	poldek >= 0.30.1-7.1
Requires:	sed >= 4.0
Suggests:	%{name}-bzr
Suggests:	bash-completion-%{name}
Suggests:	git-core >= 1.6.1-1
Obsoletes:	yum-etckeeper
BuildArch:	noarch
BuildRoot:	%{tmpdir}/%{name}-%{version}-root-%(id -u -n)

%define		_poldekconfdir	/etc/poldek
%define		_poldeklibdir	%{_prefix}/lib/poldek

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
%setup -q -a3
%patch -P1 -p1
%patch -P2 -p1

patch -p1 < debian/patches/0002-Default-to-UTF8-encoding-for-consistent-ordering.patch || exit 1

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
install -d $RPM_BUILD_ROOT{/etc/cron.daily,%{_sysconfdir}/%{name},%{_localstatedir}/cache/%{name}} \
	$RPM_BUILD_ROOT%{_poldekconfdir}/{pre,post}-install.d

%{__make} install \
	etcdir=/lib \
	LOWLEVEL_PACKAGE_MANAGER=rpm \
	HIGHLEVEL_PACKAGE_MANAGER=poldek \
	PYTHON=%{__python} \
	PYTHON_INSTALL_OPTS="%py_install_opts" \
	INSTALL="install -p" \
	DESTDIR=$RPM_BUILD_ROOT

mv $RPM_BUILD_ROOT{/lib,%{_sysconfdir}}/%{name}/%{name}.conf

install -p cron.daily $RPM_BUILD_ROOT/etc/cron.daily/%{name}
install -p %{SOURCE1} $RPM_BUILD_ROOT%{_poldekconfdir}/pre-install.d/%{name}
install -p %{SOURCE2} $RPM_BUILD_ROOT%{_poldekconfdir}/post-install.d/%{name}

%py_ocomp $RPM_BUILD_ROOT%{py_sitescriptdir}
%py_comp $RPM_BUILD_ROOT%{py_sitescriptdir}
%py_postclean

%clean
rm -rf $RPM_BUILD_ROOT

%post
if [ $1 -gt 1 ]; then
	%{_bindir}/%{name} update-ignore
fi

if [ $1 -eq 1 ] && [ -e "/etc/etckeeper/etckeeper.conf" ]; then
	# Fresh install.
	. /etc/etckeeper/etckeeper.conf || true
	if [ -n "$VCS" ] && [ -x "`which $VCS 2>/dev/null`" ]; then
		if %{_bindir}/etckeeper init; then
			if ! %{_bindir}/etckeeper commit "Initial commit"; then
			echo "etckeeper commit failed; run it by hand" >&2
			fi
		else
			echo "etckeeper init failed; run it by hand" >&2
		fi
	else
		echo "etckeeper init not ran as $VCS is not installed" >&2
	fi
fi

%triggerpostun -- %{name} < 1.18-2
# don't do anything on --downgrade
[ $1 -le 1 ] && exit 0
# poldek itself may be removed
test -f /etc/poldek/poldek.conf || exit 0
# remove our hook as "pm command", poldek supports hooks dir now
# NOTE: poldek own trigger migrating to hooks dir is invoked after this trigger
%{__sed} -i -re 's,^pm command = %{_poldeklibdir}/%{name}.sh,#&,' /etc/poldek/poldek.conf

%files
%defattr(644,root,root,755)
%doc doc/README.mdwn doc/install.mdwn
%dir %{_sysconfdir}/%{name}
%config(noreplace) %verify(not md5 mtime size) %{_sysconfdir}/%{name}/%{name}.conf
%dir /lib/%{name}
%dir /lib/%{name}/*.d
%attr(755,root,root) /lib/%{name}/daily
%attr(755,root,root) /lib/%{name}/*.d/[0-9]*
/lib/%{name}/*.d/README
%attr(755,root,root) /etc/cron.daily/%{name}
%attr(755,root,root) %{_bindir}/%{name}
%{_mandir}/man8/%{name}.8*
%attr(755,root,root) %{_poldekconfdir}/pre-install.d/%{name}
%attr(755,root,root) %{_poldekconfdir}/post-install.d/%{name}
%dir %attr(750,root,root) %{_localstatedir}/cache/%{name}

%{systemdunitdir}/etckeeper.service
%{systemdunitdir}/etckeeper.timer

# subpackages
%exclude /lib/etckeeper/commit.d/30bzr-add

%if %{with bzr}
%files bzr
%defattr(644,root,root,755)
/lib/etckeeper/commit.d/30bzr-add
%dir %{py_sitescriptdir}/bzrlib
%dir %{py_sitescriptdir}/bzrlib/plugins
%dir %{py_sitescriptdir}/bzrlib/plugins/%{name}
%{py_sitescriptdir}/bzrlib/plugins/%{name}/*.py[co]
%{py_sitescriptdir}/bzr_etckeeper-*.egg-info
%endif

%files -n bash-completion-%{name}
%defattr(644,root,root,755)
%{bash_compdir}/etckeeper
