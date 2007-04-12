Summary:	A system integrity assessment tool
Name:		tripwire
Version:	2.4.0.1
Release:	%mkrel 4
License:	GPL
Group:		Monitoring
URL:		http://www.tripwire.org/
Source0:	http://download.sourceforge.net/tripwire/tripwire-%{version}-src.tar.bz2
Source1:	tripwire.cron
Source2:	tripwire.txt
Source3:	tripwire.gif
Source4:	twcfg.txt.in
Source5:	twinstall.sh.in
Source6:	twpol.txt.in
Source7:	README.RPM
Patch0:		tripwire-2.4.0.1-gcc4.diff
Patch1:		tripwire-2.4.0.1-install_fix.diff
Requires:	sed grep >= 2.3 gzip tar gawk
BuildRequires:	libstdc++-devel
BuildRequires:	openssl-devel
BuildRequires:	gcc-c++
BuildRoot:	%{_tmppath}/%{name}-%{version}-%{release}-buildroot

%description
Tripwire is a very valuable security tool for Linux systems, if it is
installed to a clean system.  Tripwire should be installed right after
the OS installation, and before you have connected your system to a
network (i.e., before any possibility exists that someone could alter
files on your system).

When Tripwire is initially set up, it creates a database that records
certain file information.  Then when it is run, it compares a
designated set of files and directories to the information stored in
the database.  Added or deleted files are flagged and reported, as are
any files that have changed from their previously recorded state in
the database.  When Tripwire is run against system files on a regular
basis, any file changes will be spotted when Tripwire is run.
Tripwire will report the changes, which will give system
administrators a clue that they need to enact damage control measures
immediately if certain files have been altered.

Extra-paranoid Tripwire users will set it up to run once a week and
e-mail the results to themselves.  Then if the e-mails stop coming,
you'll know someone has gotten to the Tripwire program...

After installing this package, you should run "/etc/tripwire/twinstall.sh"
to generate cryptographic keys, and "tripwire --init" to initialize the
database.

%prep

%setup -q -n tripwire-%{version}
%patch0 -p1 -b .gcc4
%patch1 -p0 -b .install_fix

for i in `find . -type d -name .svn`; do
    if [ -e "$i" ]; then rm -rf $i; fi >&/dev/null
done

cp %{SOURCE2} quickstart.txt
cp %{SOURCE3} quickstart.gif

%build
export WANT_AUTOCONF_2_5=1
rm -f configure
rm -rf autom4te.cache
libtoolize --copy --force; aclocal; autoconf; automake --foreign --add-missing --copy

# instead of buildrequires...
export path_to_vi="/bin/vi"
export path_to_sendmail="%{_sbindir}/sendmail"

# it cannot handle optimization, twadmin stalls forever
# http://qa.mandriva.com/show_bug.cgi?id=26504
export CFLAGS="-O -pipe -Wp,-D_FORTIFY_SOURCE=2"
export CXXFLAGS="$CFLAGS"

%configure2_5x \
    --sysconfdir=%{_sysconfdir}/%{name}

%make

%install
[ "%{buildroot}" != "/" ] && rm -rf %{buildroot}

%makeinstall_std

# Install configuration information.
mkdir -p %{buildroot}%{_sysconfdir}/%{name}
for infile in %{SOURCE4} %{SOURCE5} %{SOURCE6}; do
	cat $infile |\
	sed -e 's|@sbindir@|%{_sbindir}|g' |\
	sed -e 's|@vardir@|%{_var}|g' >\
	%{buildroot}/etc/tripwire/`basename $infile .in`
done

cp -p %{SOURCE7} .

# Create the reports directory.
install -d -m700 %{buildroot}%{_localstatedir}/%{name}/report

# Install the cron job.
install -d -m755 %{buildroot}%{_sysconfdir}/cron.daily
install -m755 %{SOURCE1} %{buildroot}%{_sysconfdir}/cron.daily/%{name}-check

# Fix permissions on documentation files.
chmod 644 ChangeLog COPYING policy/policyguide.txt TRADEMARK quickstart.gif quickstart.txt README.RPM

%clean
[ "%{buildroot}" != "/" ] && rm -rf %{buildroot}

%files
%attr(-,root,root)
%doc ChangeLog COPYING policy/policyguide.txt TRADEMARK quickstart.gif quickstart.txt README.RPM
%attr(0755,root,root) %dir %{_sysconfdir}/%{name}
%attr(0755,root,root) %config(noreplace) %{_sysconfdir}/%{name}/twinstall.sh
%attr(0644,root,root) %config(noreplace) %{_sysconfdir}/%{name}/twcfg.txt
%attr(0644,root,root) %config(noreplace) %{_sysconfdir}/%{name}/twpol.txt
%attr(0755,root,root) %config(noreplace) %{_sysconfdir}/cron.daily/%{name}-check
%attr(0755,root,root) %dir %{_localstatedir}/%{name}
%attr(0755,root,root) %dir %{_localstatedir}/%{name}/report
%attr(0644,root,root) %{_mandir}/*/*
%attr(0755,root,root) %{_sbindir}/*


