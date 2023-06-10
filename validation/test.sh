#!/bin/bash

check() {
  res=$?
  if [ $res -ne 0 ]; then
    echo $1
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
check "Conversion failed!"
python3 $WS/converter/validateCombine.py
check "Validation of combine cards failed!"
python3 $WS/converter/validatePyhf.py
check "Validation of pyhf cards failed!"

echo "Done."
echo "Run combine tests .."

#python3 $WS/validation/combine.py

echo "Done."
echo "Run pyhf tests .."

#python3 $WS/validation/pyhf.py

echo "Done."
echo "Run comparisons .."
echo "All done."