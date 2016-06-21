import logging
import plugins
import sys

logging.root.setLevel(logging.DEBUG)

"""
we use logging in both plugins and main
after call plugins.loginit(), all logging will write to our saved logfile
"""

#plugins.loginit()

def test():
    logging.debug("now testing")

    #OPTION
    plugins.loginit()
    plugins.running(sys.argv[1])



if __name__ == '__main__':
    test()
