import subprocess

def setprec(d):
    for k in d.keys():
        if k not in ['r']: prec = 1E+6
        else: prec = 1E+2
        d[k] = [round(v*prec)/prec for v in d[k]]

def execute(logger, c):
    try:
        r = subprocess.check_output(c, stderr=subprocess.STDOUT, shell=True)
        logger.debug(r)
    except subprocess.CalledProcessError as e:
        logger.error(e.output)
