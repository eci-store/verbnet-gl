"""analyze.py

Some basic analysis of the predicates in VerbNet.

Usage:

   $ python analyze.py [--verbnet VERBNET_FOLDER] [--predicate PRED_NAME]

VERBNET_FOLDER is the location of VerbNet and PRED_NAME is the kind of predicate
to analyze. Both arguments are optional, the defaults are in the VERBNET and
PRED variables. If --predicate is not used than PRED will be None and no
restrictions will be used.

Examples:

   $ python analyze.py
   $ python analyze.py --predicate motion

Results are written to two files:

   out-missing-roles.html
   out-predicates.txt

"""

import sys, getopt
from verbnet import VerbNet, PredicateStatistics


VERBNET = '/DATA/resources/lexicons/verbnet/verbnet-3.3'
PRED = None


if __name__ == '__main__':

    (opts, args) = getopt.getopt(sys.argv[1:], '', ['verbnet=', 'predicate='])
    for opt, arg in opts:
        if opt == '--verbnet':
            VERBNET = arg
        elif opt == '--predicate':
            PRED = arg
    dir = sys.argv[1] if len(sys.argv) > 1 else VERBNET
    vn = VerbNet(directory=VERBNET)
    stats = PredicateStatistics(vn, PRED)
    stats.print_missing_links('out-missing-roles.html')
    stats.print_predicates('out-predicates.txt')
