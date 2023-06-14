#!/bin/bash

check() {
  if grep -q "ERROR" $1; then
    exit 1
  fi
}

pyloc=($(pip show pyhf | grep Location))

echo "Setting up environment .."

export CVMFS_HTTP_PROXY=DIRECT
mount -t cvmfs cvmfs-config.cern.ch /cvmfs/cvmfs-config.cern.ch
mount -t cvmfs sft.cern.ch /cvmfs/sft.cern.ch

export WS=$GITHUB_WORKSPACE
mkdir $WS/logs
mkdir $WS/validation/results
cd /HiggsAnalysis/CombinedLimit
. env_lcg.sh
export PYTHONPATH=$PYTHONPATH:${pyloc[1]} # include additional modules from image

echo "Done"
echo "Convert datacards .."

python3 $WS/converter/convert.py
check "$WS/logs/convert.log"
python3 $WS/converter/validateCombine.py
check "$WS/logs/validateCombine.log"
python3 $WS/converter/validatePyhf.py
check "$WS/logs/validatePyhf.log"

echo "Done."
echo "Run combine tests .."
python3 $WS/validation/combine.py

echo "Done."
echo "Run pyhf tests .."
python3 $WS/validation/pyhf.py

echo "Done."
echo "Run comparisons .."
echo "All done."

cd $WS; tar -czf log.tar.gz logs