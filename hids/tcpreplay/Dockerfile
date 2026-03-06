FROM ubuntu:22.04

# Install build dependencies
RUN apt-get update && apt-get install -y \
    build-essential \
    git \
    autoconf \
    automake \
    libtool \
    autogen \
    libpcap-dev \
    tcpdump \
    iproute2 \
    iputils-ping \
    && rm -rf /var/lib/apt/lists/*

# Build tcpreplay from source
WORKDIR /tmp
RUN git clone https://github.com/appneta/tcpreplay.git && \
    cd tcpreplay && \
    ./autogen.sh && \
    ./configure && \
    make && \
    make install && \
    ldconfig && \
    cd / && \
    rm -rf /tmp/tcpreplay

WORKDIR /pcaps

ENTRYPOINT ["tcpreplay"]
CMD ["--version"]
