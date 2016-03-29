"""

Analyzing the predicates in VerbNet.

Set VERBNET to the location of VerbNet and PRED to restrict statistics to those
classes that contain that predicate, use None if no restriction is desired.

"""


from verbnet import VerbNet, PredicateStatistics

VERBNET = "/Users/marc/Dropbox/sift/cwc/verbnet/3.2/new_vn"

PRED = None
PRED = 'motion'

vn = VerbNet(directory=VERBNET)
stats = PredicateStatistics(vn, PRED)
stats.print_missing_links('out-missing-roles.html')
stats.print_predicates('out-predicates.txt')
