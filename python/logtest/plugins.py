import logging
import traceback
import os



def loginit():
    try:
        logfile = 'test.log'
        #os.close(os.open(logfile, os.O_CREAT | os.O_EXCL, 0o600))

        hdlr = logging.FileHandler(filename=logfile, mode='w')
        fmts = '%(asctime)s::%(levelname)s::%(module)s::%(lineno)d::%(name)s:: %(message)s'
        dfmt = '%Y-%m-%d %H:%M:%S'
        fmt = logging.Formatter(fmts, dfmt)
        hdlr.setFormatter(fmt)
        logging.root.handlers = []
        logging.root.addHandler(hdlr)
        logging.root.setLevel(logging.DEBUG)
    except:
        logging.error(traceback.format_exc())
        raise Exception("log error")

    return logfile



def running(param):
    logging.debug("hohohoohoho %s"%param)
