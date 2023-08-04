import subprocess
from decimal import Decimal

def setprec(d, prec=2):
    for ik, k in enumerate(d):
        k = Decimal(str(k))
        d[ik] = float(round(k, prec))

def execute(logger, c):
    try:
        r = subprocess.check_output(c, stderr=subprocess.STDOUT)
        logger.debug(r)
    except subprocess.CalledProcessError as e:
        logger.error(e.output)
