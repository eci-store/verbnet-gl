"""search.py

Module with search functions for Verbnet classes.

"""

def search_by_predicate(verbclasslist, pred_type):
    """Returns verbclasses that exactly match the predicate."""
    successes = []
    for vc in verbclasslist:
        for frame in vc.frames:
            for pred in frame.vnframe.predicates:
                if pred.value[0] == pred_type:
                    if vc not in successes:
                        successes.append(vc)
    return successes


def search_by_argtype(verbclasslist, argtype, contains=False):
    """Returns verbclass IDs that have predicates that contain the argtype.
    Optional variable to allow for searching to see if the argtype contains a
    string."""
    results = []
    for vc in verbclasslist:
        for frame in vc.frames:
            for pred in frame.vnframe.predicates:
                for arg, arg_type in pred.argtypes:
                    if not contains:
                        if argtype == arg_type:
                            if vc.ID not in results:
                                results.append(vc.ID)
                    else:
                        if argtype in arg_type:
                            if vc.ID not in results:
                                results.append(vc.ID)
    return results


def search_by_ID(verbclasslist, ID, contains=False):
    """Returns verbclasses with a given ID name.
    Optional variable to allow for searching to see if the argtype contains a
    string. Returns a list in case multiple classes have that ID/string"""
    for vc in verbclasslist:
        if not contains:
            if ID == vc.ID:
                return vc
            else:
                if len(vc.subclasses) > 0:
                    for subclass in vc.subclasses:
                        result = search_by_subclass_ID(subclass, ID)
                        if result is not None:
                            return result
        else:
            if ID in vc.ID:
                return vc
    return None

def search_by_subclass_ID(subclass, ID):
    """Recursive search through subclasses to see if any match ID specified"""
    if subclass.ID == ID:
        return subclass
    if len(subclass.subclasses) == 0:
        if subclass.ID == ID:
            return subclass
        else:
            return None
    else:
        for subc in subclass.subclasses:
            result = search_by_subclass_ID(subc, ID)
            if result is not None:
                return result
        return None


def search_by_themroles(verbclasslist, themroles, only=False):
    """Returns verbclasses that contain specified thematic roles.
    Only returns classes that contain every role in the list, with the option
    to only return classes that contain all and only those roles."""
    results = []
    nocase_themroles = [themrole.lower() for themrole in themroles]
    for vc in verbclasslist:
        out = False
        for themrole in vc.roles:
            if themrole.role_type.lower() not in nocase_themroles:
                out = True
        if not out:
            if only:
                if len(themroles) == len(vc.roles):
                    results.append(vc)
            else:
                results.append(vc)
    return results


def search_by_POS(verbclasslist, POS_list, only=False):
    """Returns frames (and their verbclass's ID) that contain specified syntactic roles.
    Only returns frames that contain every role in the list, with the option
    to only return frames that contain all and only those roles.

    TODO: consider ordering and differentiating between classes with 1 NP vs 2,
    etc."""
    results = []
    nocase_pos = [POS.lower() for POS in POS_list]
    for vc in verbclasslist:
        for frame in vc.frames:
            out = False
            for member in frame.subcat:
                if member.cat.lower() not in nocase_pos:
                    out = True
            if not out:
                if only:
                    if len(POS_list) == len(frame.subcat):
                        results.append((frame, vc.ID))
                else:
                    results.append((frame, vc.ID))
    return results


def search_by_cat_and_role(verbclasslist, cat_role_tuples, only=False):
    """Returns frames (and their verbclass's ID) that contain specified syntactic
    roles (POS), where those roles have a specific semantic category (Agent, etc.)
    Only returns frames that contain every role in the list, with the option
    to only return frames that contain all and only those cat/roles combinations."""
    results = []
    nocase_tuples = [(unicode(POS.lower(), "utf-8"), unicode(role.lower(), "utf-8"))\
                    for POS,role in cat_role_tuples]
    for vc in verbclasslist:
        for frame in vc.frames:
            out = False
            for targetcat, targetrole in nocase_tuples:
                inner_loop = False
                for member in frame.subcat:
                    cat = unicode(member.cat.lower(), "utf-8")
                    role = unicode('none', "utf-8")
                    if len(member.role) != 0:
                        role = member.role[0].lower().encode('utf-8')
                    if cat == targetcat:
                        if role == targetrole:
                            inner_loop = True
                if not inner_loop:
                    out = True
            if not out:
                if only:
                    if len(cat_role_tuples) == len(frame.subcat):
                        results.append((frame, vc.ID))
                else:
                    results.append((frame, vc.ID))
    return results
