FROM ubuntu:18.04

# This dockerfile follows the setup in
# https://github.com/apache/trafficserver/blob/master/tests/bootstrap.py

# Install packages to build trafficserver
RUN ln -fs /usr/share/zoneinfo/Etc/UTC /etc/localtime \
 && sed -i 's/^# deb-src/deb-src/' /etc/apt/sources.list \
 && apt-get update \
 && DEBIAN_FRONTEND=noninteractive apt-get build-dep -y trafficserver \
 && apt-get install -y git \
 && apt-get install -y python3 python3-virtualenv virtualenv python3-dev curl netcat net-tools \
 && useradd -r -m -s /bin/bash build

# Install Origin (Nginx with lua-nginx-module)
USER root
RUN apt-get update \
 && apt-get install -y apache2-utils wget \
 && mkdir ~/build \
 && cd ~/build \o && wget https://github.com/openresty/luajit2/archive/v2.1-20190626.tar.gz \
 && tar zxvf v2.1-20190626.tar.gz \
 && cd luajit2-2.1-20190626 \
 && make PREFIX=/usr/local/luajit \
 && make install PREFIX=/usr/local/luajit \
 && cd ~/build \
 && wget https://github.com/simplresty/ngx_devel_kit/archive/v0.3.1.tar.gz \
 && tar zxvf v0.3.1.tar.gz \
 && wget https://github.com/openresty/lua-nginx-module/archive/v0.10.15.tar.gz \
 && tar zxvf v0.10.15.tar.gz \
 && wget https://nginx.org/download/nginx-1.17.3.tar.gz \
 && tar zxvf nginx-1.17.3.tar.gz
RUN cd nginx-1.17.3 \
 && export LUAJIT_LIB=/usr/local/luajit/lib \
 && export LUAJIT_INC=/usr/local/luajit/include/luajit-2.1
 && ./configure --prefix=/etc/nginx --sbin-path=/usr/sbin/nginx  --conf-path=/etc/nginx/nginx.conf --error-log-path=/var/log/nginx/error.log --http-log-path=/var/log/nginx/access.log --pid-path=/var/run/nginx.pid --lock-path=/var/run/nginx.lock --http-client-body-temp-path=/var/cache/nginx/client_temp --http-proxy-temp-path=/var/cache/nginx/proxy_temp --http-fastcgi-temp-path=/var/cache/nginx/fastcgi_temp --http-uwsgi-temp-path=/var/cache/nginx/uwsgi_temp --http-scgi-temp-path=/var/cache/nginx/scgi_temp --user=nginx --group=nginx --with-ld-opt="-Wl,-rpath,/usr/local/luajit/lib" --add-module=../ngx_devel_kit-0.3.1/ --add-module=../lua-nginx-module-0.10.15/ \\
 && make -j2 \
 && make install \
 && groupadd nginx \
 && useradd -g nginx nginx \
 && usermod -s /bin/false nginx \
 && mkdir /var/cache/nginx \
 && nginx
COPY nginx_config/nginx.conf /etc/nginx/nginx.conf
RUN htpasswd -b -c /etc/nginx/.htpasswd test test \
 && mkdir -p /var/www/html \
 && echo "test" > /var/www/html/index.html \
 && mkdir /var/www/html/test_a && echo "test" > /var/www/html/test_a/index.html \
 && mkdir /var/www/html/test_b && echo "test" > /var/www/html/test_b/index.html \
 && mkdir /var/www/html/test_c && echo "test" > /var/www/html/test_c/index.html \
 && mkdir /var/www/html/test_d && echo "test" > /var/www/html/test_d/index.html \
 && mkdir /var/www/html/test_e && echo "test" > /var/www/html/test_e/index.html \
 && mkdir /var/www/html/test_a_public && echo "test" > /var/www/html/test_a_public/index.html \
 && mkdir /var/www/html/test_b_public && echo "test" > /var/www/html/test_b_public/index.html \
 && mkdir /var/www/html/test_c_public && echo "test" > /var/www/html/test_c_public/index.html \
 && mkdir /var/www/html/test_d_public && echo "test" > /var/www/html/test_d_public/index.html \
 && mkdir /var/www/html/test_e_public && echo "test" > /var/www/html/test_e_public/index.html \
 && mkdir /var/www/html/test_f && echo "test" > /var/www/html/test_f/index.html \
 && mkdir /var/www/html/test_g && echo "test" > /var/www/html/test_g/index.html \
 && mkdir /var/www/html/test_h && echo "test" > /var/www/html/test_h/index.html \
 && mkdir /var/www/html/test_h_public && echo "test" > /var/www/html/test_h_public/index.html \
 && mkdir /var/www/html/test_i && echo "test" > /var/www/html/test_i/index.html \
 && mkdir /var/www/html/test_j && echo "test" > /var/www/html/test_j/index.html \
 && mkdir /var/www/html/test_k && echo "test" > /var/www/html/test_k/index.html \
 && mkdir /var/www/html/test_200_auth && echo "test" > /var/www/html/test_200_auth/index.html \
 && nginx -s reload

USER build
# Get the source and configure trafficserver
RUN mkdir -p ~/dev \
 && cd ~/dev \
 && git clone --depth 1 https://github.com/apache/trafficserver \
 && cd trafficserver \
 && git log -1 \
 && autoreconf -if

# NOTE: Add patches here if available

# Build trafficserver
RUN cd ~/dev/trafficserver \
 && ./configure --enable-experimental-plugins \
 && make

USER root
RUN cd ~build/dev/trafficserver \
 && make install \
 && echo /usr/local/lib > /etc/ld.so.conf.d/trafficserver.conf \
 && ldconfig

USER build

# Set up test environment
RUN cd ~/dev/trafficserver/tests \
 && virtualenv --python=python3 env-test \
 && env-test/bin/pip install pip --upgrade \
 && env-test/bin/pip install autest==1.7.2 hyper hyper requests dnslib httpbin traffic-replay

# Run trafficserver existing gold_tests
COPY run-trafficserver-tests.sh /usr/local/bin/

USER root
RUN chmod 777 /usr/local/bin/run-trafficserver-tests.sh

USER build
RUN /usr/local/bin/run-trafficserver-tests.sh

# Run headers to not cache gold_tests
COPY --chown=build:build tests/gold_tests/headers-to-not-cache/ /tmp/headers-to-not-cache/
RUN mkdir ~/tmp
RUN cd ~/dev/trafficserver/tests/gold_tests/ \
 && mv * ~/tmp/ \
 && mv ~/tmp/autest-site ~/dev/trafficserver/tests/gold_tests/
RUN mv /tmp/headers-to-not-cache ~/dev/trafficserver/tests/gold_tests/
RUN /usr/local/bin/run-trafficserver-tests.sh

ENTRYPOINT ["/bin/bash"]
