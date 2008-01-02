%define		path_to_vi /bin/vi
%define		path_to_sendmail /usr/sbin/sendmail

Summary:	A system integrity assessment tool
Name:		tripwire
Version:	2.4.1.2
Release:	%mkrel 1
License:	GPL
Group:		Monitoring
URL:		http://www.tripwire.org/
Source0:	http://download.sourceforge.net/tripwire/tripwire-%{version}-src.tar.bz2
Source1:	tripwire.cron.in
Source2:	tripwire.txt
Source3:	tripwire.gif
Source4:	twcfg.txt.in
Source5:	twinstall.sh.in
Source6:	twpol.txt.in
Source7:	README.RPM
Source8:	config.guess
Source9:	tripwire-setup-keyfiles.in
Patch0:		tripwire-2.4.0.1-gcc4.diff
Patch1:		tripwire-2.4.0.1-install_fix.diff
Patch2:		tripwire-siggen-man8.patch


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
%setup -q -n %{name}-%{version}-src
%{__cp} -p %{SOURCE3} .
%{__cp} -p %{SOURCE8} .

%patch2 -p1 -b .siggen.manpage

%build
%{__chmod} 755 configure
# RPM_OPT_FLAGS break the code (deadlock).
export CXXFLAGS="-O -Wall -pipe -g"
./configure -q \
	path_to_vi=%{path_to_vi} \
	path_to_sendmail=%{path_to_sendmail} \
	--prefix=/ \
	--sysconfdir=%{_sysconfdir}/tripwire \
	--sbindir=%{_sbindir} \
	--libdir=%{_var}/lib \
	--mandir=%{_mandir}

%make 

%install
%{__rm} -fr ${RPM_BUILD_ROOT}

# Install the binaries.
%{__mkdir_p} ${RPM_BUILD_ROOT}%{_sbindir}
%{__install} -p -m755 bin/siggen ${RPM_BUILD_ROOT}%{_sbindir}
%{__install} -p -m755 bin/tripwire ${RPM_BUILD_ROOT}%{_sbindir}
%{__install} -p -m755 bin/twadmin ${RPM_BUILD_ROOT}%{_sbindir}
%{__install} -p -m755 bin/twprint ${RPM_BUILD_ROOT}%{_sbindir}

# Install the man pages.
%{__mkdir_p} ${RPM_BUILD_ROOT}%{_mandir}/{man4,man5,man8}
%{__install} -p -m644 man/man4/*.4 ${RPM_BUILD_ROOT}%{_mandir}/man4/
%{__install} -p -m644 man/man5/*.5 ${RPM_BUILD_ROOT}%{_mandir}/man5/
%{__install} -p -m644 man/man8/*.8 ${RPM_BUILD_ROOT}%{_mandir}/man8/

# Create configuration files from templates.
%{__rm} -fr _tmpcfg
%{__mkdir} _tmpcfg
for infile in %{SOURCE1} %{SOURCE4} %{SOURCE5} %{SOURCE6} %{SOURCE7} %{SOURCE8} %{SOURCE9}; do
	outfile=${infile##/*/}
	outfile=${outfile%.*n}
	cat ${infile} |\
	%{__sed} -e 's|@path_to_vi@|%{path_to_vi}|g' |\
	%{__sed} -e 's|@path_to_sendmail@|%{path_to_sendmail}|g' |\
	%{__sed} -e 's|@sysconfdir@|%{_sysconfdir}|g' |\
	%{__sed} -e 's|@sbindir@|%{_sbindir}|g' |\
	%{__sed} -e 's|@vardir@|%{_var}|g' >\
	_tmpcfg/${outfile}
done
%{__mv} _tmpcfg/{tripwire-setup-keyfiles,README.RPM} .

# Create the reports directory.
%{__install} -d -m700 ${RPM_BUILD_ROOT}%{_var}/lib/tripwire/report

# Install the cron job.
%{__install} -d -m755 ${RPM_BUILD_ROOT}%{_sysconfdir}/cron.daily
%{__install} -p -m755 _tmpcfg/tripwire.cron \
	${RPM_BUILD_ROOT}%{_sysconfdir}/cron.daily/tripwire-check
%{__rm} _tmpcfg/tripwire.cron

# Install configuration files.
%{__mkdir_p} ${RPM_BUILD_ROOT}%{_sysconfdir}/tripwire
for file in _tmpcfg/* ; do
	%{__install} -p -m644 ${file} ${RPM_BUILD_ROOT}%{_sysconfdir}/tripwire
done

# Install the keyfile setup script
%{__install} -p -m755 tripwire-setup-keyfiles ${RPM_BUILD_ROOT}%{_sbindir}

# Fix permissions on documentation files.
%{__cp} -p %{SOURCE9} .
%{__chmod} 644 \
	ChangeLog COMMERCIAL COPYING TRADEMARK tripwire.gif \
	README.RPM policy/policyguide.txt


%clean
%{__rm} -rf ${RPM_BUILD_ROOT}


%post
# Set the real hostname in twpol.txt
%{__sed} -i -e "s|localhost|$HOSTNAME|g" %{_sysconfdir}/tripwire/twpol.txt


%files
%defattr(0644,root,root,0755)
%doc ChangeLog COMMERCIAL COPYING TRADEMARK tripwire.gif
%doc README.RPM policy/policyguide.txt 
%attr(0700,root,root) %dir %{_sysconfdir}/tripwire
%config(noreplace) %{_sysconfdir}/tripwire/config.guess
%config(noreplace) %{_sysconfdir}/tripwire/twinstall.sh
%config(noreplace) %{_sysconfdir}/tripwire/twcfg.txt
%config(noreplace) %{_sysconfdir}/tripwire/twpol.txt
%attr(0755,root,root) %{_sysconfdir}/cron.daily/tripwire-check
%attr(0700,root,root) %dir %{_var}/lib/tripwire
%attr(0700,root,root) %dir %{_var}/lib/tripwire/report
%{_mandir}/*/*
%attr(0755,root,root) %{_sbindir}/*
