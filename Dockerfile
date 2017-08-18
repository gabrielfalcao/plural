FROM ubuntu:latest

ENV DEBIAN_FRONTEND  noninteractive
ENV PYTHONUNBUFFERED true
ENV VIRTUAL_ENV      /usr/local/virtualenv
ENV PATH             $VIRTUAL_ENV/bin:$PATH
ENV PYTHONPATH       $PYTHONPATH:$VIRTUAL_ENV/lib/python2.7/site-packages
ENV HOME             /plural
RUN echo 'source /usr/local/virtualenv/bin/activate' >> /etc/bash.bashrc

RUN apt-get update \
  && apt-get --yes dist-upgrade \
  && apt-get --yes install \
    apt-transport-https \
    aptitude \
    bash \
    bash-completion \
    build-essential \
    ca-certificates \
    curl \
    git \
    gnupg2 \
    htop \
    cmake \
    less \
    libc6-dev \
    libevent-dev \
    iputils-ping \
    libffi-dev \
    libgit2-dev \
    libmysqlclient-dev \
    libnacl-dev \
    libnacl-dev \
    libssl-dev \
    libxml2-dev \
    libxslt1-dev \
    libzmq3-dev \
    openssl \
    pkg-config \
    python-pip \
    python2.7 \
    python2.7-dev \
    redis-tools \
    rng-tools \
    rsync \
    software-properties-common \
    telnet \
    unrar \
    vim \
    virtualenvwrapper \
    wget \
    zip \
  && rm -rf /var/lib/apt/lists/*


ENV LIBGIT2_VERSION 0.26.0
RUN pip install -U pip
RUN cd /tmp && \
    wget -q https://github.com/libgit2/libgit2/archive/v${LIBGIT2_VERSION}.tar.gz && \
    tar xzvf v${LIBGIT2_VERSION}.tar.gz && \
    cd libgit2-${LIBGIT2_VERSION} && \
    mkdir -p build/install && cd build && \
    cmake -DCMAKE_INSTALL_PREFIX:PATH=/usr .. \
    cmake -DCMAKE_INSTALL_PREFIX:PATH=/usr --build . \
    make install

RUN pip install virtualenv \
  && mkdir -p "${VIRTUAL_ENV}" \
  && virtualenv "${VIRTUAL_ENV}"


RUN pip install -U ipdb twine

COPY . /plural

WORKDIR /plural

RUN pip install -U -r /plural/development.txt
