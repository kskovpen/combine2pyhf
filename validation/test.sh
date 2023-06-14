#!/bin/bash

check() {
  if grep -q "ERROR" $1; then
    exit 1
  fi
}

echo "Setting up environment .."

export CVMFS_HTTP_PROXY=DIRECT
mount -t cvmfs cvmfs-config.cern.ch /cvmfs/cvmfs-config.cern.ch
mount -t cvmfs sft.cern.ch /cvmfs/sft.cern.ch

export WS=$GITHUB_WORKSPACE
mkdir $WS/validation/results
cd /HiggsAnalysis/CombinedLimit
. env_lcg.sh

echo "Done"
echo "Convert datacards .."

python3 $WS/converter/convert.py
check "$WS/validation/cards/combine/convert.log"
python3 $WS/converter/validateCombine.py
check "$WS/validation/cards/combine/validateCombine.log"
python3 $WS/converter/validatePyhf.py
check "$WS/validation/cards/combine/validatePyhf.log"

echo "Done."
echo "Run combine tests .."

#python3 $WS/validation/combine.py

echo "Done."
echo "Run pyhf tests .."

#python3 $WS/validation/pyhf.py

echo "Done."
echo "Run comparisons .."
echo "All done."