Summary: nginx high performance web server
Name: nginx
Version: 1.10.0
Release: 9.el7
# MIT License
# http://opensource.org/licenses/MIT
License: MIT
Source:  http://nginx.org/download/nginx-1.10.0.tar.gz
Source1: ftp://ftp.csx.cam.ac.uk/pub/software/programming/pcre/pcre-8.38.tar.gz
Source2: http://zlib.net/zlib-1.2.8.tar.gz
Source3: https://www.openssl.org/source/openssl-1.0.2h.tar.gz

%description
The nginx-filesystem package contains the basic directory layout
for the Nginx server including the correct permissions for the
directories.

%global bin_dir %_usr/bin
%global nginx_prefix %_sysconfdir/nginx

%prep
%setup
%setup -D -T -b 1
%setup -D -T -b 2
%setup -D -T -b 3

%pre
# shamelessly nabbed and modified from 
# http://stackoverflow.com/questions/14810684/check-whether-a-user-exists
ret=0
%bin_dir/getent passwd %name >> /dev/null 2>&1 && ret=1
if [ ${ret} -lt 1 ]
  then 
    %_sbindir/useradd -c "Nginx" -s /bin/false -r -d %nginx_prefix/sbin %name 2>/dev/null
  fi

%post
%bin_dir/systemctl daemon-reload
%bin_dir/systemctl enable nginx.service 2>/dev/null
%bin_dir/systemctl start nginx.service

%preun
%bin_dir/systemctl disable nginx.service 2>/dev/null
%bin_dir/systemctl stop nginx.service

# preserve configs and index.html
%__cp -f %nginx_prefix/html/index.html %nginx_prefix/html/index.html.rpmsave
%__cp -f %nginx_prefix/conf/nginx.conf %nginx_prefix/conf/nginx.conf.rpmsave
%__cp -f %nginx_prefix/sites-available/vhost.example.conf %nginx_prefix/sites-available/vhost.example.conf.rpmsave

%postun
for i in cache logs sbin ssl
  do
    %__rm -rf %nginx_prefix/${i}
  done
%__rm -f %_unitdir/nginx.service
%__rm -f %_sysconfdir/logrotate.d/nginx
%__rm -f %_usr/local/bin/nginx

%build
./configure \
--prefix=%nginx_prefix \
--with-http_gzip_static_module \
--with-http_v2_module \
--with-http_stub_status_module \
--with-ipv6 \
--with-file-aio \
--with-zlib=%_builddir/zlib-1.2.8 \
--with-pcre=%_builddir/pcre-8.38 \
--http-client-body-temp-path=%nginx_prefix/cache/client_temp \
--http-proxy-temp-path=%nginx_prefix/cache/proxy_temp \
--http-fastcgi-temp-path=%nginx_prefix/cache/fastcgi_temp \
--http-uwsgi-temp-path=%nginx_prefix/cache/uwsgi_temp \
--http-scgi-temp-path=%nginx_prefix/cache/scgi_temp \
--user=%name \
--group=%name \
--with-http_ssl_module \
--with-openssl-opt=enable-tlsext \
--with-openssl=%_builddir/openssl-1.0.2h

%install
%make_install

%__install -p -m 0755 -d %buildroot/%nginx_prefix/logs
%__install -p -m 0755 -d %buildroot/%nginx_prefix/ssl
%__install -p -m 0755 -d %buildroot/%nginx_prefix/cache
%__install -p -m 0755 -d %buildroot/%nginx_prefix/sites-available
%__install -p -m 0755 -d %buildroot/%nginx_prefix/sites-enabled

# nabbed and modified from the el7 nginx rpm in the epel repo
# thanks Jamie Nguyen
%__install -p -m 0644 -o root -g root -D %_sourcedir/nginxtras/nginx.service %buildroot/%_unitdir/nginx.service
%__install -p -m 0644 -D %_sourcedir/nginxtras/nginx.logrotate %buildroot/%_sysconfdir/logrotate.d/nginx

# add custom nginx config
%__install -p -m 0644 -o nginx -g nginx -D %_sourcedir/nginxtras/nginx.conf %buildroot/%nginx_prefix/conf/nginx.conf
%__install -p -m 0644 -o nginx -g nginx -D %_sourcedir/nginxtras/vhost.example.conf %buildroot/%nginx_prefix/sites-available/vhost.example.conf
%__ln_s %nginx_prefix/sites-available/vhost.example.conf %buildroot/%nginx_prefix/sites-enabled/vhost.example.conf

# add binary symlink to /usr/local/bin
%__install -p -m 0755 -o root -g root -d %buildroot/%_prefix/local/bin
%__ln_s %nginx_prefix/sbin/nginx %buildroot/%_prefix/local/bin/nginx

# add custom html / php files
%__install -p -m 0644 -o nginx -g nginx -D %_sourcedir/nginxtras/index.html %buildroot/%nginx_prefix/html/index.html
%__install -p -m 0644 -o nginx -g nginx -D %_sourcedir/nginxtras/php-test.php %buildroot/%nginx_prefix/html/php-test.php

# adjust permissions
%bin_dir/find %buildroot/%nginx_prefix -type f -exec %__chmod 0644 {} \; -exec %__chown %name:%name {} \;
%bin_dir/find %buildroot/%nginx_prefix -type d -exec %__chmod 0755 {} \; -exec %__chown %name:%name {} \;
%__chmod 0755 %buildroot/%nginx_prefix/sbin/nginx

%files
%nginx_prefix/sbin/nginx
%config(noreplace) %nginx_prefix/conf/fastcgi.conf
%config(noreplace) %nginx_prefix/conf/fastcgi.conf.default
%config(noreplace) %nginx_prefix/conf/fastcgi_params
%config(noreplace) %nginx_prefix/conf/fastcgi_params.default
%config(noreplace) %nginx_prefix/conf/koi-utf
%config(noreplace) %nginx_prefix/conf/koi-win
%config(noreplace) %nginx_prefix/conf/mime.types
%config(noreplace) %nginx_prefix/conf/mime.types.default
%config(noreplace) %nginx_prefix/conf/nginx.conf
%config(noreplace) %nginx_prefix/conf/nginx.conf.default
%config(noreplace) %nginx_prefix/conf/scgi_params
%config(noreplace) %nginx_prefix/conf/scgi_params.default
%config(noreplace) %nginx_prefix/conf/uwsgi_params
%config(noreplace) %nginx_prefix/conf/uwsgi_params.default
%config(noreplace) %nginx_prefix/conf/win-utf
%config(noreplace) %nginx_prefix/sites-available/vhost.example.conf
%config(noreplace) %nginx_prefix/sites-enabled/vhost.example.conf
%config(noreplace) %_prefix/local/bin/nginx
%config(noreplace) %_sysconfdir/logrotate.d/nginx
%nginx_prefix/html/50x.html
%config(noreplace) %nginx_prefix/html/index.html
%nginx_prefix/html/php-test.php
%_unitdir/nginx.service
%dir %nginx_prefix/logs
%dir %nginx_prefix/ssl
%dir %nginx_prefix/cache
%dir %nginx_prefix/sites-available
%dir %nginx_prefix/sites-enabled

# append --define 'noclean 1' to rpmbuild if desired to keep the buildroot directory
# shamelessly nabbed from
# http://stackoverflow.com/questions/13830262/rpmbuild-clean-phase-without-removing-files
%clean
%if "%noclean" == ""
   rm -rf $RPM_BUILD_ROOT
%endif

