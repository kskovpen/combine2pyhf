#!/bin/bash

check() {
  if grep -q "ERROR" $1; then
    exit 1
  fi
}

pyloc=($(pip show pyhf | grep Location))
echo "Installed python modules (native):"
pip list
which python3

echo "Setting up environment .."

export CVMFS_HTTP_PROXY=DIRECT
mount -t cvmfs cvmfs-config.cern.ch /cvmfs/cvmfs-config.cern.ch
mount -t cvmfs sft.cern.ch /cvmfs/sft.cern.ch

export WS=$GITHUB_WORKSPACE
mkdir $WS/logs
mkdir $WS/validation/results
cd /HiggsAnalysis/CombinedLimit
. env_lcg.sh
which python3

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
check "$WS/logs/combine.log"
echo "Done."
echo "Run pyhf tests .."
alias python3=python3.10
export PYTHONPATH=${pyloc[1]} # include additional modules from image
python3 $WS/validation/pyhf.py
check "$WS/logs/pyhf.log"
echo "Done."
echo "Run analytical tests .."
python3 $WS/validation/analytic.py
check "$WS/logs/analytic.log"
echo "Done."

echo "All done."

cd $WS; tar -czf log.tar.gz logs