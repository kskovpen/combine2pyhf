#!/bin/bash

check() {
  if grep -q "ERROR" $1; then
    exit 1
  fi
}
python3 -m pip list
pyhfon() {
  unset PYTHONPATH; unset PYTHONHOME
  /usr/bin/virtualenv --python=/usr/bin/python3 pyhfenv > /dev/null
  source pyhfenv/bin/activate
  pip install pyhf iminuit deepdiff > /dev/null
  source pyhfenv/bin/activate
}

pyhfoff() {
  deactivate
  export PYTHONPATH=$PP; export PYTHONHOME=$PH
}

pyloc=($(pip show pyhf | grep Location))
export PYTHONPATH=$PYTHONPATH:${pyloc[1]}
echo "Add modules from ${pyloc[1]}"

echo "Setting up environment .."

export CVMFS_HTTP_PROXY=DIRECT
mount -t cvmfs cvmfs-config.cern.ch /cvmfs/cvmfs-config.cern.ch
mount -t cvmfs sft.cern.ch /cvmfs/sft.cern.ch

export WS=$GITHUB_WORKSPACE
mkdir -p $WS/logs
mkdir -p $WS/results
cd /HiggsAnalysis/CombinedLimit
. env_lcg.sh
PP=$PYTHONPATH; PH=$PYTHONHOME

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
python3 $WS/validation/fitcombine.py
check "$WS/logs/combine.log"
echo "Done."
echo "Run pyhf tests .."
pyhfon; python3 $WS/validation/fitpyhf.py; pyhfoff
check "$WS/logs/pyhf.log"
echo "Done."
echo "Run analytical tests .."
python3 $WS/validation/analytic.py
check "$WS/logs/analytic.log"
echo "Done."

pyhfon
python3 -m pip list
echo "Run plotting .."
python3 $WS/validation/plot.py --input $WS/results
check "$WS/logs/plot.log"
echo "Done."

python3 $WS/validation/publish.py

echo "All done."