#FROM ubuntu:latest as base
FROM ubuntu:22.04 as base
FROM base as builder

RUN apt-get update -y
RUN apt-get upgrade -y
#RUN apt-get install -y git make wget lsb-release libncurses5-dev python3-full python3-pip python3-setuptools virtualenv dpkg gcc-11 fuse libgfortran5 cpio
#RUN apt-get install -y git make wget lsb-release libncurses5 python3 python3-pip python3-distutils virtualenv dpkg gcc-11 fuse libgfortran5 cpio
RUN apt-get install -y git make wget lsb-release libncurses5 python3 python3-pip python3-distutils virtualenv dpkg gcc-12 fuse libgfortran5 cpio
RUN gcc --version

RUN python3 -m pip install --upgrade pip
RUN python3 -m pip install pyhf deepdiff kaleido plotly matplotlib pydash jax jaxlib torch torchvision --break-system-packages
RUN python3 -m pip install --upgrade jax jaxlib --break-system-packages

RUN git clone --single-branch --branch combine2pyhf https://github.com/kskovpen/HiggsAnalysis-CombinedLimit.git HiggsAnalysis/CombinedLimit

RUN wget https://ecsft.cern.ch/dist/cvmfs/cvmfs-release/cvmfs-release-latest_all.deb
RUN dpkg -i cvmfs-release-latest_all.deb
RUN rm -f cvmfs-release-latest_all.deb
RUN apt-get update
RUN apt-get install -y cvmfs

COPY install.sh .

ENTRYPOINT ["/bin/bash", "install.sh"]
