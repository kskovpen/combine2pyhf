#!/bin/bash

echo "Setting up environment .."

export CVMFS_HTTP_PROXY=DIRECT
mount -t cvmfs cvmfs-config.cern.ch /cvmfs/cvmfs-config.cern.ch
mount -t cvmfs sft.cern.ch /cvmfs/sft.cern.ch

export WS=$GITHUB_WORKSPACE
cd /HiggsAnalysis/CombinedLimit
. env_lcg.sh

echo "Done. Convert datacards .."

python3 $WS/converter/convert.py
python3 $WS/converter/validateCombine.py
python3 $WS/converter/validatePyhf.py

echo "Done. Run combine tests .."

#python3 $WS/validation/combine.py

echo "Done. Run pyhf tests .."

#python3 $WS/validation/pyhf.py

echo "Done. Run comparisons .."
echo "All done."