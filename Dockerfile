from ubuntu:12.04

run apt-get update && apt-get install -y \
        build-essential \
        git-svn bison \
        flex \
        gfortran \
        libatlas-base-dev \
        python-dev \
        pkg-config \
        cmake \
        python-virtualenv \
        python-zc.buildout


