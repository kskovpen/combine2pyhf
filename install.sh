#/bin/bash

. /HiggsAnalysis/CombinedLimit/env_lcg.sh
root-config --version
uname -a
gcc --version
cd HiggsAnalysis/CombinedLimit
/usr/bin/make LCG=1 -j 8