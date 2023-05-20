#/bin/bash

. /HiggsAnalysis/CombinedLimit/env_lcg.sh
root-config --version
uname -a
gcc --version
/usr/bin/make LCG=1 -j 8