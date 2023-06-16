FROM ubuntu:latest as base
FROM base as builder

RUN apt-get update -y
RUN apt-get upgrade -y
RUN apt-get install -y git make wget lsb-release libncurses5 python3 python3-pip python3-distutils virtualenv dpkg gcc-11 fuse libgfortran5
RUN gcc --version

RUN python3 -m pip install --upgrade pip
RUN python3 -m pip install pyhf deepdiff kaleido plotly

RUN git clone --single-branch --branch combine2pyhf https://github.com/kskovpen/HiggsAnalysis-CombinedLimit.git HiggsAnalysis/CombinedLimit

RUN wget https://ecsft.cern.ch/dist/cvmfs/cvmfs-release/cvmfs-release-latest_all.deb
RUN dpkg -i cvmfs-release-latest_all.deb
RUN rm -f cvmfs-release-latest_all.deb
RUN apt-get update
RUN apt-get install -y cvmfs

COPY install.sh .

ENTRYPOINT ["/bin/bash", "install.sh"]
