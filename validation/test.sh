#!/bin/bash

check() {
  if grep -q "ERROR" $1; then
    exit 1
  fi
}

pyhfon() {
  echo "point1"
  virtualenv --python=/usr/bin/python3 pyhfenv
  echo "point2"
  source pyhfenv/bin/activate
  echo "point3"
}

pyhfoff() {
  deactivate
}

pyloc=($(pip show pyhf | grep Location))
echo "Installed python modules (native):"
which python3
which virtualenv

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
which virtualenv
pyhfon; python3 $WS/converter/validatePyhf.py; pyhfoff
sys.exit()
check "$WS/logs/validatePyhf.log"

echo "Done."
echo "Run combine tests .."
python3 $WS/validation/combine.py
check "$WS/logs/combine.log"
echo "Done."
echo "Run pyhf tests .."
pyhfon; python3 $WS/validation/pyhf.py; pyhfoff
check "$WS/logs/pyhf.log"
echo "Done."
echo "Run analytical tests .."
python3 $WS/validation/analytic.py
check "$WS/logs/analytic.log"
echo "Done."

echo "All done."

cd $WS; tar -czf log.tar.gz logs