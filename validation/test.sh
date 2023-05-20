#!/bin/bash

echo "Setting up environment .."
export CVMFS_HTTP_PROXY=DIRECT
mount -t cvmfs cvmfs-config.cern.ch /cvmfs/cvmfs-config.cern.ch
mount -t cvmfs sft.cern.ch /cvmfs/sft.cern.ch
cd /HiggsAnalysis/CombinedLimit
. env_lcg.sh
echo "Ready. Starting combine tests .."
cp validation/combine.py .
python3 combine.py
echo "Done."

