"""tests.py

This is here to de-clutter the verbnetgl module a bit.

"""

import itertools, textwrap

from .writer import HtmlWriter
from .search import search_by_predicate, search_by_ID, search_by_argtype
from .search import search_by_themroles, search_by_POS, search_by_cat_and_role


def test_all(verb_classes, GLVerbClass):
    """Run all tests in here."""
    test_print_second_class(verb_classes)
    test_print_some_classes(verb_classes)
    test_search_by_ID(verb_classes)
    test_ch_of_searches(verb_classes)
    test_new_searches(verb_classes, GLVerbClass)
    test_predicate_search(verb_classes)


def test_print_second_class(vn_classes):
    """Just print the first class to stdout."""
    prompt('test_print_second_class')
    vn_classes[1].pp()


def test_print_some_classes(vn_classes):
    """Print a list of classes that match a couple of hand-picked predicates. The
    results are written to the html directory."""
    prompt('test_print_some_classes')
    preds = ["motion", "transfer", "adjust", "cause", "transfer_info",
             "emotional_state", "location", "state", "wear", "approve"]
    results = { p: search_by_predicate(vn_classes, p) for p in preds }
    result_classes = [i for i in itertools.chain.from_iterable(list(results.values()))]
    result_classes = sorted(set(result_classes))
    #result_classes = set(result_classes)
    writer = HtmlWriter()
    writer.write(result_classes, "VN Classes")
    print("Results are written to html/index.html")


def test_search_by_ID(vn_classes):
    prompt('test_search_by_ID')
    for idenfifier in ('absorb-39.8', 'accompany-51.7'):
        try:
            print((search_by_ID(vn_classes, idenfifier)))
        except:
            print(("\nWARNING: could not find %s" % idenfifier))
    try:
        print((search_by_ID(vn_classes, "swarm-47.5.1").subclasses[1]))
    except AttributeError:
        print("\nWARNING: could not find swarm-47.5.1")


def test_ch_of_searches(vn_classes):
    # find all 'ch_of_' verb classes
    prompt('test_ch_of_searches')
    for argtype in ('ch_of_', 'ch_of_info', 'ch_of_pos', 'ch_of_poss',
                    'ch_of_state', 'ch_of_loc', 'ch_of_location'):
        results = search_by_argtype(vn_classes, argtype)
        results = [r.ID for r in results]
        print(("%s %s %s\n" % (len(results), argtype, ' '.join(results))))
    path_rel_results = search_by_argtype(vn_classes, "path_rel")
    print(('number of path_rel classes:', len(path_rel_results)))
    path_less_ch = [vc.ID for vc in path_rel_results if vc.ID not in ch_of_results]
    print(('path_rel classes with no ch_of:', path_less_ch, "\n"))


def test_new_searches(vn_classes, GLVerbClass):
    # This one is a bit ugly since we need to either import or hand in the GLVerbClass.
    prompt('test_new_searches')
    sbt = search_by_themroles
    sbp = search_by_POS
    sbcar = search_by_cat_and_role
    for print_string, function, role_list, boolean in [
            ("Verbclasses with Agent and Patient thematic roles:",
             sbt, ['Agent', 'Patient'], False),
            ('Agent and Patient only classes:',
             sbt, ['Agent', 'Patient'], True),
            ("Verbclasses with frames with NP and VERB syntactic roles:",
             sbp, ['NP', 'VERB'], False),
            ('NP and VERB only classes:',
             sbp, ['NP', 'VERB'], True),
            ("Verbclasses with frames with (NP, Agent) subcat members:",
             sbcar, [('NP', 'Agent')], False),
            ('(NP, Agent) and (PREP, None) classes:',
             sbcar, [('NP', 'Agent'), ('PREP', 'None')], False),
            ('(NP, Agent) and (VERB, None) only classes:',
             sbcar, [('NP', 'Agent'), ('VERB', 'None')], True) ]:
        results = function(vn_classes, role_list, boolean)
        ids = []
        if results:
            ids = [vc.ID for vc in results] \
                if isinstance(results[0], GLVerbClass) \
                else [ID for frame, ID in results]
            ids = sorted(list(set(ids)))
        print(("There are %s cases of %s" % (len(ids), print_string)))
        wrapped = textwrap.wrap(' '.join([id for id in ids]), 80)
        print(("\n  ", "\n   ".join(wrapped)))
        print()


def test_predicate_search(vn_classes):
    prompt('test_predicate_search')
    motion_vcs1 = [vc for vc in vn_classes if vc.is_motion_class()]
    motion_vcs2 = search_by_predicate(vn_classes, "motion")
    m1 = sorted([c.ID for c in motion_vcs1])
    m2 = sorted([c.ID for c in motion_vcs2])
    print(("Motion verbs found with is_motion_class()     = %s" % len(m1)))
    print(("Motion verbs found with search_by_predicate() = %s" % len(m2)))
    if m1 != m2:
        print("Warning: lists are not equal")
    print()


def prompt(text):
    print(("\n%s" % (">" * 80)))
    print((">>> RUNNING %s" % text))
    print(">>> Hit return to proceed...")
    input()
    #eval(input())
