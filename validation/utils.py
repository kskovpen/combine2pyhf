import subprocess

def setprec(d, prec=1E+2):
    for ik, k in enumerate(d):
        d[ik] = round(k*prec)/prec

def execute(logger, c):
    try:
        r = subprocess.check_output(c, stderr=subprocess.STDOUT, shell=True)
        logger.debug(r)
    except subprocess.CalledProcessError as e:
        logger.error(e.output)
