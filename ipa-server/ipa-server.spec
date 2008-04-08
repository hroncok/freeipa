Name:           ipa-server
Version:        0.99.0
Release:        5%{?dist}
Summary:        IPA authentication server

Group:          System Environment/Base
License:        GPLv2
URL:            http://www.freeipa.org
Source0:        %{name}-%{version}.tgz
BuildRoot:      %{_tmppath}/%{name}-%{version}-%{release}-root-%(%{__id_u} -n)

BuildRequires: fedora-ds-base-devel >= 1.1
BuildRequires: mozldap-devel
BuildRequires: openssl-devel
BuildRequires: openldap-devel
BuildRequires: krb5-devel
BuildRequires: nss-devel
BuildRequires: libcap-devel

Requires: ipa-server-selinux
Requires: ipa-python
Requires: ipa-admintools
Requires: ipa-client
Requires: fedora-ds-base >= 1.1
Requires: openldap-clients
Requires: nss
Requires: nss-tools
Requires: krb5-server
Requires: krb5-server-ldap
Requires: cyrus-sasl-gssapi
Requires: ntp
Requires: httpd
Requires: mod_python
Requires: mod_auth_kerb
Requires: mod_nss >= 1.0.7-2
Requires: python-ldap
Requires: python
Requires: python-krbV
Requires: TurboGears
Requires: python-tgexpandingformwidget
Requires: acl
Requires: python-pyasn1
Requires: libcap

Conflicts: mod_ssl

%define httpd_conf /etc/httpd/conf.d
%define plugin_dir %{_libdir}/dirsrv/plugins

%{!?python_sitelib: %define python_sitelib %(%{__python} -c "from distutils.sysconfig import get_python_lib; print get_python_lib()")}

%description
IPA is a server for identity, policy, and audit.

%prep
%setup -q
./configure --prefix=%{buildroot}/usr --libdir=%{buildroot}/%{_libdir} --sysconfdir=%{buildroot}/etc --localstatedir=%{buildroot}/var

%build

make

%install
rm -rf %{buildroot}

make install

# Remove .la files from libtool - we don't want to package
# these files
rm %{buildroot}/%{plugin_dir}/libipa_pwd_extop.la
rm %{buildroot}/%{plugin_dir}/libipa-memberof-plugin.la
rm %{buildroot}/%{plugin_dir}/libipa-dna-plugin.la

# Some user-modifiable HTML files are provided. Move these to /etc
# and link back.
mkdir -p %{buildroot}/%{_sysconfdir}/ipa/html
mv %{buildroot}/%{_usr}/share/ipa/html/ssbrowser.html %{buildroot}/%{_sysconfdir}/ipa/html
mv %{buildroot}/%{_usr}/share/ipa/html/unauthorized.html %{buildroot}/%{_sysconfdir}/ipa/html
ln -s ../../../..%{_sysconfdir}/ipa/html/ssbrowser.html \
    %{buildroot}%{_usr}/share/ipa/html/ssbrowser.html
ln -s ../../../..%{_sysconfdir}/ipa/html/unauthorized.html \
    %{buildroot}%{_usr}/share/ipa/html/unauthorized.html

%clean
rm -rf %{buildroot}

%post
if [ $1 = 1 ]; then
    /sbin/chkconfig --add ipa_kpasswd
    /sbin/chkconfig --add ipa_webgui
fi
/bin/touch /var/log/ipa_error.log
/bin/chown apache /var/log/ipa_error.log
/bin/chmod 600 /var/log/ipa_error.log
restorecon /var/log/ipa_error.log

%preun
if [ $1 = 0 ]; then
    /sbin/chkconfig --del ipa_kpasswd
    /sbin/chkconfig --del ipa_webgui
    /sbin/service ipa_kpasswd stop >/dev/null 2>&1 || :
    /sbin/service ipa_webgui stop >/dev/null 2>&1 || :
fi

%postun
if [ "$1" -ge "1" ]; then
    /sbin/service ipa_kpasswd condrestart >/dev/null 2>&1 || :
    /sbin/service ipa_webgui condrestart >/dev/null 2>&1 || :
fi

%files
%defattr(-,root,root,-)
%{_sbindir}/ipa-server-install
%{_sbindir}/ipa-replica-install
%{_sbindir}/ipa-replica-prepare
%{_sbindir}/ipa-replica-manage
%{_sbindir}/ipa-server-certinstall
%{_sbindir}/ipactl
%{_sbindir}/ipa_kpasswd
%{_sbindir}/ipa_webgui
%attr(755,root,root) %{_initrddir}/ipa_kpasswd
%attr(755,root,root) %{_initrddir}/ipa_webgui

%dir %{_usr}/share/ipa
%{_usr}/share/ipa/*.ldif
%{_usr}/share/ipa/*.template
%dir %{_usr}/share/ipa/html
%{_usr}/share/ipa/html/ssbrowser.html
%{_usr}/share/ipa/html/unauthorized.html
%dir %{_sysconfdir}/ipa
%dir %{_sysconfdir}/ipa/html
%config(noreplace) %{_sysconfdir}/ipa/html/ssbrowser.html
%config(noreplace) %{_sysconfdir}/ipa/html/unauthorized.html
%{_usr}/share/ipa/ipa_webgui.cfg
%{_usr}/share/ipa/ipa.conf
%{_usr}/share/ipa/ipa-rewrite.conf
%dir %{_usr}/share/ipa/ipagui
%{_usr}/share/ipa/ipagui/*
%dir %{_usr}/share/ipa/ipa_gui.egg-info
%{_usr}/share/ipa/ipa_gui.egg-info/*
%dir %{_usr}/share/ipa/ipaserver
%{_usr}/share/ipa/ipaserver/*
%dir %{_usr}/share/ipa/locales/
%{_usr}/share/ipa/locales/*

%dir %{python_sitelib}/ipaserver
%{python_sitelib}/ipaserver/*.py*

%attr(755,root,root) %{plugin_dir}/libipa_pwd_extop.so
%attr(755,root,root) %{plugin_dir}/libipa-memberof-plugin.so
%attr(755,root,root) %{plugin_dir}/libipa-dna-plugin.so

%dir %{_localstatedir}/lib/ipa
%attr(700,root,root) %dir %{_localstatedir}/lib/ipa/sysrestore
%dir %{_localstatedir}/cache/ipa
%attr(700,root,root) %dir %{_localstatedir}/cache/ipa/kpasswd
%attr(700,apache,apache) %dir %{_localstatedir}/cache/ipa/sessions

%{_mandir}/man8/ipactl.8.gz
%{_mandir}/man8/ipa_kpasswd.8.gz
%{_mandir}/man8/ipa_webgui.8.gz
%{_mandir}/man1/ipa-replica-install.1.gz
%{_mandir}/man1/ipa-replica-manage.1.gz
%{_mandir}/man1/ipa-replica-prepare.1.gz
%{_mandir}/man1/ipa-server-certinstall.1.gz
%{_mandir}/man1/ipa-server-install.1.gz

%changelog
* Fri Mar 14 2008 Rob Crittenden <rcritten@redhat.com> - 0.99.0-5
- Run restorecon on /var/log/ipa_error.log to ensure correct selinux context

* Fri Mar 14 2008 Rob Crittenden <rcritten@redhat.com> - 0.99.0-4
- Add missing man pages
- Add Conflicts for mod_ssl

* Thu Feb 26 2008 Rob Crittenden <rcritten@redhat.com> - 0.99.0-3
- Add ipactl command

* Thu Feb 21 2008 Rob Crittenden <rcritten@redhat.com> - 0.99.0-2
- package new file ipa-rewrite.conf

* Thu Feb 21 2008 Rob Crittenden <rcritten@redhat.com> - 0.99.0-1
- Version bump for release

* Thu Feb  7 2008 Masato Taruishi <taruishi@redhat.com> = 0.6.0-9
- Internationalize the kid templates and include a Japanese translation.

* Thu Feb  6 2008 Karl MacMillan <kmacmill@redhat.com> = 0.6.0-8
- Add requirement on ipa-server-selinux

* Thu Jan 31 2008 Rob Crittenden <rcritten@redhat.com> = 0.6.0-7
- Marked with wrong license. IPA is GPLv2.

* Thu Jan 31 2008 Rob Crittenden <rcritten@redhat.com> = 0.6.0-6
- Ensure that the ipa_webgui error log exists and has correct permissions.

* Tue Jan 29 2008 Rob Crittenden <rcritten@redhat.com> = 0.6.0-5
- Put user-modifiable files into /etc/ipa so they can be marked as
  config(noreplace).

* Thu Jan 24 2008 Rob Crittenden <rcritten@redhat.com> = 0.6.0-4
- Use new name of pyasn1, python-pyasn1, in Requires

* Tue Jan 22 2008 Rob Crittenden <rcritten@redhat.com> = 0.6.0-3
- add session cache directory

* Thu Jan 17 2008 Rob Crittenden <rcritten@redhat.com> = 0.6.0-2
- Fixed License in specfile
- Include files from /usr/lib/python*/site-packages/ipaserver

* Fri Dec 21 2007 Karl MacMillan <kmacmill@redhat.com> - 0.6.0-1
- Version bump for release

* Wed Nov 21 2007 Karl MacMillan <kmacmill@mentalrootkit.com> - 0.5.0-1
- Preverse mode on ipa-keytab-util
- Version bump for relase and rpm name change

* Thu Nov 15 2007 Rob Crittenden <rcritten@redhat.com> - 0.4.1-2
- Broke invididual Requires and BuildRequires onto separate lines and
  reordered them
- Added python-tgexpandingformwidget as a dependency
- Require at least fedora-ds-base 1.1

* Thu Nov  1 2007 Karl MacMillan <kmacmill@redhat.com> - 0.4.1-1
- Version bump for release

* Wed Oct 31 2007 Karl MacMillan <kmacmill@redhat.com> - 0.4.0-6
- Add dep for freeipa-admintools and acl

* Wed Oct 24 2007 Rob Crittenden <rcritten@redhat.com> - 0.4.0-5
- Add dependency for python-krbV

* Fri Oct 19 2007 Rob Crittenden <rcritten@redhat.com> - 0.4.0-4
- Require mod_nss-1.0.7-2 for mod_proxy fixes

* Thu Oct 18 2007 Karl MacMillan <kmacmill@redhat.com> - 0.4.0-3
- Convert to autotools-based build

* Tue Sep 25 2007 Karl MacMillan <kmacmill@redhat.com> - 0.4.0-2
- Package ipa-webgui

* Fri Sep 7 2007 Karl MacMillan <kmacmill@redhat.com> - 0.3.0-1
- Added support for libipa-dna-plugin

* Fri Aug 10 2007 Karl MacMillan <kmacmill@redhat.com> - 0.2.0-1
- Added support for ipa_kpasswd and ipa_pwd_extop

* Mon Aug  5 2007 Rob Crittenden <rcritten@redhat.com> - 0.1.0-3
- Abstracted client class to work directly or over RPC

* Wed Aug  1 2007 Rob Crittenden <rcritten@redhat.com> - 0.1.0-2
- Add mod_auth_kerb and cyrus-sasl-gssapi to Requires
- Remove references to admin server in ipa-server-setupssl
- Generate a client certificate for the XML-RPC server to connect to LDAP with
- Create a keytab for Apache
- Create an ldif with a test user
- Provide a certmap.conf for doing SSL client authentication

* Fri Jul 27 2007 Karl MacMillan <kmacmill@redhat.com> - 0.1.0-1
- Initial rpm version
