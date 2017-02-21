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


# Four function to perform image schema related searches, can probably be
# somewhat simplified

def image_schema_search(verbclasslist, scheme, second_round=True, inclusive=False):
    """Use an ImageScheme object to find verb frames that match the scheme
    Optionally allows to make thematic roles inclusive (search results can return
    verb classes that only have a thematic role, as opposed to requiring a prep
    or selectional restriction)
    Optional second round to narrow search results to include only those verb
    classes that contain the elements from the list of thematic roles"""
    results = []
    for vc in verbclasslist:
        result = set()
        frame_and_id_list = []
        for i in range(len(vc.frames)):
            frame_and_id_list.append((vc.frames[i], i, vc.ID))
        for subclass in vc.subclasses:
            sub_frames = recursive_frames(subclass)
            frame_and_id_list.extend(sub_frames)
        for frame,frame_num,ID in frame_and_id_list:
            for member in frame.subcat:
                if member.cat == "PREP":
                    if len(member.role) > 0:
                        if member.role[0] in scheme.pp_list:
                            result.add((frame, frame_num, ID))
                    if len(member.sel_res) > 0:
                        for res in member.sel_res:
                            if res in scheme.sel_res_list:
                                result.add((frame, frame_num, ID))
                if inclusive:
                    if len(member.role) > 0:
                        if member.role[0] in scheme.role_list:
                            result.add((frame, frame_num, ID))
        if len(result) > 0:
            results.append((vc.ID, result))
    if len(scheme.role_list) > 0:
        if second_round:
            round_2 = []
            for vc_id, class_results in results:
                result = set()
                for frame,frame_num,ID in class_results:
                    for member in frame.subcat:
                        if len(member.role) > 0:
                            if member.role[0] in scheme.role_list:
                                result.add((frame, frame_num, ID))
                if len(result) > 0:
                    round_2.append((vc_id, result))
            return sorted(round_2)
    return sorted(results)


def image_schema_search2(verbclasslist, pp_list, sem_list=None):
    """TODO: Try to find verb classes using image schema"""
    round_1 = set()
    for vc in verbclasslist:
        for frame in vc.frames:
            for member in frame.subcat:
                if member.cat == 'PREP':
                    if len(member.role) != 0:
                        for role in member.role:
                            if role in pp_list:
                                round_1.add((frame, vc.ID))
    if not sem_list:
        return sorted(round_1)
    else:
        round_2 = set()
        for frame,vc_id in round_1:
            for member in frame.subcat:
                if len(member.role) != 0:
                    for rol in member.role:
                        if rol in sem_list:
                            round_2.add((frame, vc_id))
    return sorted(round_2)


def recursive_frames(subclass):
    frame_and_ids = []
    for i in range(len(subclass.frames)):
        frame_and_ids.append((subclass.frames[i], i, subclass.ID))
    if len(subclass.subclasses) == 0:
        return frame_and_ids
    else:
        for subc in subclass.subclasses:
            frame_and_ids.extend(recursive_frames(subc))
        return frame_and_ids


def reverse_image_search(frame, scheme, obligatory_theme=True, theme_only=False):
    """Checks to see if a particular frame belongs to an image schema
    Optionally allows to make the check for agreement on thematic roles
    obligatory.
    Also optionally allows for the search to return true if the frame only matches
    a thematic role"""
    pp = False
    sr = False
    tr = False
    for member in frame.subcat:
        if member.cat == "PREP":
            if len(member.role) > 0:
                if member.role[0] in scheme.pp_list:
                    pp = True
            if len(member.sel_res) > 0:
                for res in member.sel_res:
                    if res in scheme.sel_res_list:
                        sr = True
        if len(member.role) > 0:
            if member.role[0] in scheme.role_list:
                tr = True
    if theme_only:
        return tr
    if obligatory_theme:
        return (pp or sr) and tr
    else:
        return (pp or sr)
