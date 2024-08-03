#!/bin/bash

check() {
  if grep -q "ERROR" $1; then
    exit 1
  fi
}

pyenvon() {
  unset PYTHONPATH; unset PYTHONHOME
  /usr/bin/virtualenv --python=/usr/bin/python3 pyenv > /dev/null
  source pyenv/bin/activate
  pip install pyhf iminuit deepdiff plotly kaleido pydash jax jaxlib torch torchvision > /dev/null
  source pyenv/bin/activate
}

pyenvoff() {
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
mkdir -p $WS/results/combine
mkdir -p $WS/results/pyhf
cd /HiggsAnalysis/CombinedLimit
. env_lcg.sh
PP=$PYTHONPATH; PH=$PYTHONHOME

echo "Done"
echo "Convert datacards .."

root-config --version
python3 $WS/converter/multibin.py
python3 $WS/converter/convert.py
check "$WS/logs/convert.log"
python3 $WS/converter/validateCombine.py
check "$WS/logs/validateCombine.log"
python3 $WS/converter/validatePyhf.py
check "$WS/logs/validatePyhf.log"

echo "Done."
echo "Run combine fits on combine inputs .."
python3 $WS/validation/fitcombine.py --combine
check "$WS/logs/combine_fitcombine.log"
echo "Done."
echo "Run pyhf fits on combine inputs .."
pyenvon; python3 $WS/validation/fitpyhf.py --combine; pyenvoff
check "$WS/logs/combine_fitpyhf.log"
echo "Done."
echo "Run combine fits on pyhf inputs .."
python3 $WS/validation/fitcombine.py
check "$WS/logs/pyhf_fitcombine.log"
echo "Done."
echo "Run pyhf fits on pyhf inputs .."
pyenvon; python3 $WS/validation/fitpyhf.py; pyenvoff
check "$WS/logs/pyhf_fitpyhf.log"
echo "Done."
echo "Run analytical tests .."
python3 $WS/validation/analytic.py
check "$WS/logs/analytic.log"
echo "Done."

echo "Run plotting .."
pyenvon; python3 $WS/validation/plot.py --input $WS/results/combine --combine; pyenvoff
check "$WS/logs/plot_combine.log"
pyenvon; python3 $WS/validation/plot.py --input $WS/results/pyhf; pyenvoff
check "$WS/logs/plot_pyhf.log"
echo "Done."

python3 $WS/validation/publish.py --output $WS/results

echo "All done."