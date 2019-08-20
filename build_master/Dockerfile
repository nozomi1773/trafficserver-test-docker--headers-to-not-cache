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

# Install Origin (Nginx)
USER root
RUN apt-get update \
 &&  apt-get install -y nginx apache2-utils
COPY nginx_config/default /etc/nginx/sites-available/default
RUN htpasswd -b -c /etc/nginx/.htpasswd test test \
 && nginx \
 && mkdir /var/www/html/test_a && echo "test" > /var/www/html/test_a/index.html \
 && mkdir /var/www/html/test_b && echo "test" > /var/www/html/test_b/index.html \
 && mkdir /var/www/html/test_c && echo "test" > /var/www/html/test_c/index.html \
 && mkdir /var/www/html/test_d && echo "test" > /var/www/html/test_d/index.html \
 && mkdir /var/www/html/test_e && echo "test" > /var/www/html/test_e/index.html \
 && mkdir /var/www/html/test_f && echo "test" > /var/www/html/test_f/index.html \
 && mkdir /var/www/html/test_g && echo "test" > /var/www/html/test_g/index.html \
 && mkdir /var/www/html/test_h && echo "test" > /var/www/html/test_h/index.html
 && nginx -s reload

#USER build
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
