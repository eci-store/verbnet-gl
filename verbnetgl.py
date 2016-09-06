"""
This file contains the classes for the form of Verbnet that have been enhanced
with GL event structures. The classes themselves do all the conversion necessary
given a VerbClass from verbnetparser.py
"""

from verbnetparser import VerbNetParser
from imageschema import *

class GLVerbClass(object):
    """VerbClass analogue, with an update mostly to frames"""
    
    def __init__(self, verbclass):
        self.verbclass = verbclass
        self.ID = verbclass.ID
        self.members = verbclass.members
        self.names = verbclass.names
        self.roles = verbclass.themroles
        self.frames = self.frames()
        self.subclasses = [GLSubclass(sub, self.roles) for sub in verbclass.subclasses]
        
    def frames(self):
        return [GLFrame(frame, self.roles) for frame in self.verbclass.frames]

    def pp_html(self, fh):
        fh.write("<html>\n")
        fh.write("<head>\n")
        fh.write("<link rel=\"stylesheet\" type=\"text/css\" href=\"style.css\">\n")
        fh.write("</head>\n")
        fh.write("<body>\n")
        fh.write("\n<h1>%s</h1>\n" % str(self.ID))
        for i in range(len(self.frames)):
            vn_frame = self.verbclass.frames[i]
            gl_frame = self.frames[i]
            fh.write("\n<table cellpadding=8 cellspacing=0 border=0 width=1000>\n")
            self.pp_html_description(gl_frame, fh)
            self.pp_html_example(gl_frame, fh)
            self.pp_html_predicate(vn_frame, fh)
            self.pp_html_subcat(gl_frame, fh)
            self.pp_html_qualia(gl_frame, fh)
            self.pp_html_event(gl_frame, fh)
            fh.write("</table>\n\n")

    def pp_html_description(self, gl_frame, fh):
        fh.write("<tr class=description>\n")
        fh.write("  <td colspan=2>%s\n" % ' '.join(gl_frame.pri_description))

    def pp_html_example(self, gl_frame, fh):
        fh.write("<tr class=vn valign=top>\n")
        fh.write("  <td width=180>Example\n")
        fh.write("  <td>\"%s\"" % gl_frame.example[0])

    def pp_html_predicate(self, vn_frame, fh):
        def predicate_str(pred):
            args = ', '.join([argtype[1] for argtype in pred.argtypes])
            return "<span class=pred>%s</span>(%s)" % (pred.value[0], args)
        fh.write("<tr class=vn valign=top>\n")
        fh.write("  <td width=180>VerbNet&nbsp;predicates\n")
        fh.write("  <td>")
        fh.write(', '.join([predicate_str(pred) for pred in vn_frame.predicates]))

    def pp_html_subcat(self, gl_frame, fh):
        fh.write("<tr class=qualia valign=top>\n")
        fh.write("  <td>GL&nbsp;subcategorisation\n")
        fh.write("  <td>\n")
        for element in gl_frame.subcat:
            #fh.write("      { %s } <br>\n" % element)
            fh.write("      {")
            if element.var is not None:
                fh.write(" var=%s" % element.var)
            fh.write(" cat=%s" % element.cat)
            if element.role:
                fh.write(" role=%s" % element.role[0])
            fh.write(" } / [")
            self.pp_html_restriction(element.sel_res, fh)
            fh.write("]<br>\n")

    def pp_html_restriction(self, restriction, fh):
        # print '>>', restriction
        if not restriction:
            pass
        elif restriction[0] in ['+', '-']:
            fh.write("%s%s" % (restriction[0], restriction[1]))
        elif restriction[0] in ['OR', 'AND'] and len(restriction) == 3:
            fh.write("(")
            self.pp_html_restriction(restriction[1], fh)
            fh.write(" %s " % restriction[0])
            self.pp_html_restriction(restriction[2], fh)
            fh.write(")")
        else:
            fh.write("%s" % restriction)

    def pp_html_qualia(self, gl_frame, fh):
        fh.write("<tr class=qualia valign=top>\n")
        fh.write("  <td>GL&nbsp;qualia&nbsp;structure\n")
        fh.write("  <td>%s\n" % gl_frame.qualia)

    def pp_html_event(self, gl_frame, fh):
        fh.write("<tr class=event valign=top>\n")
        fh.write("  <td>GL event structure")
        fh.write("  <td>var = %s<br>\n" % gl_frame.event_structure.var)
        fh.write("      initial_states = %s<br>\n" % gl_frame.event_structure.initial_states)
        fh.write("      final_states = %s\n" % gl_frame.event_structure.final_states)
            
    def __repr__(self):
        return str(self.ID) + " = {\n\nroles = " + str(self.roles) + \
               "\n\nframes = " + str(self.frames) + "\n}" + \
               "\n Subclasses = " + str(self.subclasses)


class GLSubclass(GLVerbClass):
    """Represents a subclass to a GLVerbClass. This needs to be different from
    GLVerbClass because VerbNet seems to change the THEMROLES section of the 
    subclass to only include thematic roles that differ from the main class,
    but does not list all the roles that stay the same. Since we need to update 
    self.roles, we can't call __init__ on the superclass because that would call
    self.frames and self.subclasses before we updated our roles properly.
    
    TODO: check this for proper nesting"""
    
    def __init__(self, verbclass, parent_roles):
        self.verbclass = verbclass
        self.ID = verbclass.ID
        self.members = verbclass.members
        self.names = verbclass.names
        self.parent_roles = parent_roles
        self.subclass_only_roles = verbclass.themroles
        self.roles = self.themroles()
        self.frames = self.frames()
        self.subclasses = [GLSubclass(sub, self.roles) for sub in verbclass.subclasses]   
        
    def themroles(self):
        """Combines the thematic roles of the parent class and the current
        subclass. Replaces any version of the parent class's role with one from
        the subclass."""
        final_roles = self.subclass_only_roles
        for parent_role in self.parent_roles:
            duplicate = False
            for sub_role in self.subclass_only_roles:
                if parent_role.role_type == sub_role.role_type:
                    duplicate = True
            if not duplicate:
                final_roles.append(parent_role)
        return final_roles

class GLFrame(object):
    """GL enhanced VN frame that adds qualia and event structure, and links 
    syn/sem variables in the subcat to those in the event structure
    Event structure should be its own class or method?"""
    
    def __init__(self, frame, roles):
        self.vnframe = frame
        self.class_roles = roles
        self.pri_description = frame.primary
        self.sec_description = frame.secondary
        self.example = frame.examples
        self.subcat = self.subcat()
        self.qualia = None
        self.event_structure = None
        self.event_and_opposition_structure2()
        
    def subcat(self):
        """Creates the subcat frame structure with unique variables assigned to
        different phrases/roles"""
        i = 0
        members = []
        for synrole in self.vnframe.syntax:
            if synrole.POS in ["ADV", "PREP", "ADJ"]:
                members.append(SubcatMember(None, synrole, None))
                continue
            elif synrole.POS == "VERB":
                members.append(SubcatMember("e", synrole, None))
                continue
            added = False
            for themrole in self.class_roles:
                if str(synrole.value[0]).lower() == str(themrole.role_type).lower():
                    if str(synrole.POS) == "NP":
                        members.append(SubcatMember(i, synrole, themrole))
                        i += 1
                        added = True
                    else:
                        members.append(SubcatMember(None, synrole, themrole))
                        added = True
            if not added:
                members.append(SubcatMember(None, synrole, None))
        return members
    
    def event_and_opposition_structure(self):
        """Uses the frame information to determine what initial and final states
        should look like, given the variables available in the subcat frame, and
        the roles for the verb class
        
        TODO: Figure out if path_rel is really necessary. It has start/end, 
        specifies which ThemRole is undergoing the event (Theme/Agent), and 
        whether it is Initial_Location/Destination. But the "motion" predicate
        seems to tell you which ThemRole is undergoing the movement, so what 
        more does path_rel get us?
        
        This is a target for generalization. Right now it only works with motion
        predicates. Ideally you want to compare all of the frame's subcat members
        to all of the class's thematic roles to see what is missing, and then 
        assign ?'s accordingly.
        """
        initial_state = None
        final_state = None
        # Get all the subcat members that have a variable
        members_to_assign = []
        for submember in self.subcat:
            if submember.var not in [None, "e"]:
                members_to_assign.append(submember)
                
        # Get which ThemRole is moving, and its variable in the frame
        mover = None 
        mover_var = None
        initial_loc = None
        destination = None
        for pred in self.vnframe.predicates:
            if pred.value[0] == 'motion':
                for argtype, value in pred.argtypes:
                    if argtype == 'ThemRole':
                        mover = value
        if mover:
            for member in members_to_assign:
                if member.role[0] == mover:
                    mover_var = member.var
                if member.role[0] == "Initial_Location":
                    initial_loc = member.var
                if member.role[0] == "Destination":
                    destination = member.var
                    
        # Instantiate the two states            
        if initial_loc:
            initial_state = State(mover_var, initial_loc)
            if destination:
                final_state = State(mover_var, destination)
            else:
                final_state = State(mover_var, -initial_loc)
        elif destination:
            initial_state = State(mover_var, -destination)
            final_state = State(mover_var, destination)
        else:
            initial_state = State(mover_var, "?")
            final_state = State(mover_var, "-?")
            
        opposition = Opposition(None, initial_state, final_state)
        self.event_structure = EventStructure(initial_state, final_state)
        self.qualia = Qualia(self.vnframe.predicates[0], opposition)
        
    def event_and_opposition_structure2(self):
        """Uses the frame information to determine what initial and final states
        should look like, given the variables available in the subcat frame, and
        the roles for the verb class
        """
        states = []        
        type_of_change = None
        
        # Get all the subcat members that have a variable
        member_vars = {}
        for submember in self.subcat:
            if submember.var not in [None, "e"]:
                member_vars[submember.role[0]] = submember.var
                
        pred_type = None
        start = []
        end = []
        for pred in self.vnframe.predicates:
            if pred.value[0] in ['motion', 'transfer', 'cause', 'transfer_info', \
                'adjust', 'emotional_state', 'location', 'state', 'wear']:
                pred_type = pred.value[0]
                    
        if pred_type:
            equals = []
            for pred in self.vnframe.predicates:
                if pred.value[0] == 'path_rel': 
                    # check to see where the object that changes is,
                    # and where that object is or who owns it
                    if pred.argtypes[1][1] in member_vars.keys():
                        changer = pred.argtypes[1][1]       # object that changes
                        opposition = pred.argtypes[2][1]    # where the object is or who owns it
                    else:
                        changer = pred.argtypes[2][1]       # object that changes
                        opposition = pred.argtypes[1][1]
                    if pred.argtypes[3][1] == 'ch_of_poss' or pred.argtypes[3][1] == 'ch_of_pos':
                        type_of_change = "pos"
                    if pred.argtypes[3][1] == 'ch_of_loc' or pred.argtypes[3][1] == 'ch_of_location':
                        type_of_change = "loc"
                    if pred.argtypes[3][1] == 'ch_of_info':
                        type_of_change = "info"
                    if pred.argtypes[3][1] == 'ch_of_state':
                        type_of_change = "state"
                    if pred.argtypes[0][1] == 'start(E)':
                        start.append(tuple((changer, opposition)))
                    if pred.argtypes[0][1] == 'end(E)':
                        end.append(tuple((changer, opposition)))
                if pred.value[0] == 'equals':
                    equals.append(tuple(value for argtype, value in pred.argtypes))
            # Go through all objects that change state, and if beginning and end
            # are expressed syntactically, create the opposition
            changers = [] 
            for changer_s, opposition_s in start:
                start_opp = opposition_s
                if len(equals) > 0:
                        for pair in equals:
                            if pair[1] == opposition_s:
                                start_opp = pair[0]
                try:
                    changer_s_var = member_vars[changer_s]
                except KeyError:
                    changer_s_var = changer_s
                try: 
                    opp_s_var = member_vars[start_opp]
                except KeyError:
                    #opp_s_var = start_opp
                    opp_s_var = '?'
                is_end = False
                for changer_e, opposition_e in end:
                    if changer_s == changer_e:
                        is_end = True
                        changers.append(changer_s)
                        end_opp = opposition_e
                        if len(equals) > 0:
                            for pair in equals:
                                if pair[1] == opposition_e:
                                    end_opp = pair[0]
                        try: 
                            opp_e_var = member_vars[end_opp]
                        except KeyError:
                            #opp_e_var = end_opp
                            opp_e_var = '?'
                        start_state = State(changer_s_var, opp_s_var)
                        final_state = State(changer_s_var, opp_e_var)
                        states.append(tuple((start_state, final_state)))
                if not is_end:
                    changers.append(changer)
                    start_state = State(changer_s_var, opp_s_var)
                    final_state = State(changer_s_var, "-" + str(opp_s_var))
                    states.append(tuple((start_state, final_state)))
            # Check for objects that only appear syntactically as an end        
            for changer, opposition in end:
                if changer not in changers:
                    changers.append(changer)
                    end_opp = opposition
                    if len(equals) > 0:
                        for pair in equals:
                            if pair[1] == opposition:
                                end_opp = pair[0]
                    try:
                        changer_var = member_vars[changer]
                    except KeyError:
                        changer_var = changer
                    try: 
                        opp_var = member_vars[end_opp]
                    except KeyError:
                        #opp_var = end_opp
                        opp_var = '?'
                    start_state = State(changer_var, "-" + str(opp_var))
                    final_state = State(changer_var, opp_var)
                    states.append(tuple((start_state, final_state)))
            # No path_rel predicates
            if len(changers) == 0:
                changer = '?'
                for pred in self.vnframe.predicates:
                    if pred.value[0] == pred_type:
                        changer = pred.argtypes[1][1]
                try:
                    changer_var = member_vars[changer]
                except KeyError:
                    changer_var = changer
                start_state = State(changer_var, '?')
                final_state = State(changer_var, '-?')
                states.append(tuple((start_state, final_state)))
                    
        opposition = Opposition(type_of_change, states)
        self.event_structure = EventStructure(states)
        self.qualia = Qualia(pred_type, opposition)
    
    def __repr__(self):
        output = "\n\n{ description = " + str(" ".join(self.pri_description)) + \
                 "\nexample = " + str(self.example[0]) + \
                 "\nsubcat = " + str(self.subcat) + \
                 "\nqualia = " + str(self.qualia) + \
                 "\nevent_structure = {" + str(self.event_structure) + "\t}\n"
        return output


class SubcatMember(object):
    """A combination of SyntacticRole and ThematicRole"""
    
    def __init__(self, var, synrole, themrole):
        self.var = var
        self.cat = synrole.POS
        self.role = synrole.value   #themrole.role_type won't work
        if themrole is not None:
            self.sel_res = themrole.sel_restrictions
        else:
            self.sel_res = synrole.restrictions

    def __repr__(self):
        output = "\n\t{ var = " + str(self.var) + \
                 ", cat = " + str(self.cat) + \
                 ", role = " + str(self.role) + \
                 " } / " + str(self.sel_res)
        return output
      

class State(object):
    """Represents a state in the event structure
    For motion verbs, this gives the variable assignment of the mover, and its
    location. For transfer verbs, this gives the variable assignment of the 
    object being transferred, and what currently owns the object"""
    
    def __init__(self, obj_var, pos_var):
        self.object_var = obj_var
        self.position = pos_var
        
    def __repr__(self):
        opp = 'location'
        return "{ objects." + str(self.object_var) + ".location = " + \
                str(self.position) + " }"


class EventStructure(object):
    """Defines the event structure for a particular frame of a verb"""
    
    def __init__(self, states):
        self.var = "e"
        self.states = "To Be Determined"
        self.initial_states = [state1 for state1, state2 in states]
        self.final_states = [state2 for state1, state2 in states]
        self.program = "To Be Determined"
     
    def __repr__(self):
        output = "\n\tvar = " + str(self.var) + "\n\tinitial_state = " + \
                 str(self.initial_states) + "\n\tfinal_ state = " + \
                 str(self.final_states) + "\n\tprogram = " + str(self.program)
        return output


class Opposition(object):
    """Represents the opposition structure of the frame
    Right now only tailored for locations"""
    
    def __init__(self, type_of_change, states):
        self.type_of_change = type_of_change
        self.states = states
        
    def __repr__(self):
        output = ""
        opp = "At"
        if self.type_of_change == 'pos':
            opp = 'Has'
        if self.type_of_change == 'info':
            opp = 'Knows'
        if self.type_of_change == 'state':
            opp = 'State'
        for start, end in self.states:
            output += "(" + opp + "(" + str(start.object_var) + ", " + \
                      str(start.position) + "), " + opp + "(" + \
                      str(end.object_var) + ", " + \
                      str(end.position) + ")) "
        return output
 
 
class Qualia(object):
    """Represents the qualia structure of a verbframe, including opposition
    structure"""
    
    def __init__(self, pred_type, opposition):
        self.formal = pred_type
        self.opposition = opposition
        
    def __repr__(self):
        return "{ formal = " + str(self.formal) + "(e) AND Opposition" + \
               str(self.opposition) + "}"

def search2(verbclasslist, pred_type=None, themroles=None, synroles=None, semroles=None):
    """Returns verbclasses that match search parameters
    TODO: figure out what it means to search for themroles, synroles, and semroles"""
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
    string"""
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
    results = []
    for vc in verbclasslist:
        if not contains:
            if ID == vc.ID:
                results.append(vc)
        else:
            if ID in vc.ID:
                results.append(vc)
    return results

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

def image_schema_search2(verbclasslist, pp_list, sem_list=None):
    """TODO: Try to find verb classes using image schema"""
    round_1 = set()
    for vc in verbclasslist:
        for frame in vc.frames:
            for member in frame.subcat:
                if member.cat == 'PREP':
                    if len(member.role) != 0:
                        for rol in member.role:
                            if rol in pp_list:
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

def image_schema_search(verbclasslist, scheme, second_round=True, inclusive=False):
    """Use an ImageScheme object to find verb frames that match the scheme
    Optionally allows to make thematic roles inclusive (search results can return
    verb classes that only have a thematic role, as opposed to requiring a prep
    or selectional restriction)
    Optional second round to narrow search results to include only those verb
    classes that contain the elements from the list of thematic roles"""
    results = set()
    for vc in verbclasslist:
        frame_and_id_list = [(frame, vc.ID) for frame in vc.frames]
        for subclass in vc.subclasses:
            sub_frames = recursive_frames(subclass)
            frame_and_id_list.extend(sub_frames)
        for frame,ID in frame_and_id_list:
            for member in frame.subcat:
                if member.cat == "PREP":
                    if len(member.role) > 0:
                        if member.role[0] in scheme.pp_list:
                            results.add((frame, ID))
                    if len(member.sel_res) > 0:
                        for res in member.sel_res:
                            if res in scheme.sel_res_list:
                                results.add((frame, ID))
                if inclusive:
                    if len(member.role) > 0:
                        if member.role[0] in scheme.role_list:
                            results.add((frame, ID))
    if len(scheme.role_list) > 0:
        if second_round:
            round_2 = set()
            for frame,ID in results:
                for member in frame.subcat:
                    if len(member.role) > 0:
                        if member.role[0] in scheme.role_list:
                            round_2.add((frame, ID))
            return sorted(round_2)
    return sorted(results)
            
def recursive_frames(subclass):
    frame_and_ids = [(frame, subclass.ID) for frame in subclass.frames]
    if len(subclass.subclasses) == 0:
        return frame_and_ids
    else:
        for subc in subclass.subclasses:
            frame_and_ids.extend(recursive_frames(subc))
        return frame_and_ids
    

def pp_html(results):
    INDEX = open('html/index.html', 'w')
    INDEX.write("<html>\n")
    INDEX.write("<head>\n")
    INDEX.write("<link rel=\"stylesheet\" type=\"text/css\" href=\"style.css\">\n")
    INDEX.write("</head>\n")
    INDEX.write("<body>\n")
    INDEX.write("<table cellpadding=8 cellspacing=0>\n")
    INDEX.write("<tr class=header><td>VN Ch_of_ Classes</a>\n")
    for result in results:
        class_file = "vnclass-%s.html" % result.ID
        INDEX.write("<tr class=vnlink><td><a href=\"%s\">%s</a>\n" % (class_file, result.ID))
        VNCLASS =  open("html/%s" % class_file, 'w')
        result.pp_html(VNCLASS)
    INDEX.write("</table>\n")
    INDEX.write("</body>\n")
    INDEX.write("</html>\n")


if __name__ == '__main__':
    
    vnp = VerbNetParser()
    vngl = [GLVerbClass(vc) for vc in vnp.verb_classes]
    print vngl[269] #slide
    
    motion_results = search2(vngl, "motion")
    transfer_results = search2(vngl, "transfer")
    adjust_results = search2(vngl, "adjust")
    cause_results = search2(vngl, "cause")
    transfer_info_results = search2(vngl, "transfer_info")
    emotional_state_results = search2(vngl, "emotional_state")
    location_results = search2(vngl, "location")
    state_results = search2(vngl, "state")
    wear_results = search2(vngl, "wear")
    print len(motion_results), len(transfer_results)
    results = motion_results + transfer_results
    all_results = results + adjust_results + cause_results + transfer_info_results +\
                  emotional_state_results + location_results + state_results +\
                  wear_results
    pp_html(sorted(set(all_results)))
    possession_results = search2(vngl, "has_possession")
    print len(possession_results)
    for vc in possession_results:
        print vc.ID
    # find all 'ch_of_' verb classes
    def ch_of_searches():
        ch_of_results = search_by_argtype(vngl, 'ch_of_', True)
        print '\nch_of_\n', ch_of_results, len(ch_of_results)
        results = search_by_argtype(vngl, 'ch_of_info')
        print '\nch_of_info\n', results, len(results)
        results = search_by_argtype(vngl, 'ch_of_pos')
        print '\nch_of_pos\n', results, len(results)
        results = search_by_argtype(vngl, 'ch_of_poss')
        print '\nch_of_poss\n', results, len(results)
        results = search_by_argtype(vngl, 'ch_of_state')
        print '\nch_of_state\n', results, len(results)
        results = search_by_argtype(vngl, 'ch_of_loc')
        print '\nch_of_loc\n', results, len(results)
        results = search_by_argtype(vngl, 'ch_of_location')
        print '\nch_of_location\n', results, len(results)
    # give
    #print search_by_ID(vngl, 'give', True)[0]
    # transfer possession verbs
#    transpos = search_by_argtype(transfer_results, 'ch_of_pos', True)
#    print '\nTransfer Possession:\n', transpos, len(transpos)
#    path_rel_results = search2(vngl, "path_rel")
#    print '\nNumber of path_rel classes:\n', len(path_rel_results)
#    path_less_ch = [vc.ID for vc in path_rel_results if vc.ID not in ch_of_results]
#    print '\npath_rel classes with no ch_of\n', path_less_ch
    
    # test new searches
    def new_searches():
        print "\n\nVerbclasses with Agent and Patient thematic roles:"
        them_results = search_by_themroles(vngl, ['Agent', 'Patient'])
        print '\n', [vc.ID for vc in them_results], '\n', len(them_results)
        them_results2 = search_by_themroles(vngl, ['Agent', 'Patient'], True)
        print '\nAgent and Patient only classes:\n\n', [vc.ID for vc in them_results2]
        print len(them_results2)
        print "\n\nVerbclasses with frames with NP and VERB syntactic roles:"
        pos_results = search_by_POS(vngl, ['NP', 'VERB'])
        print '\n', len(pos_results)
        pos_results2 = search_by_POS(vngl, ['NP', 'VERB'], True)
        print '\nNP and VERB only classes:\n\n', [ID for frame,ID in pos_results2]
        print len(pos_results2)
        print "\n\nVerbclasses with frames with (NP, Agent) subcat members:"
        catrole_results = search_by_cat_and_role(vngl, [('NP', 'Agent')] )
        print '\n', len(catrole_results)
        catrole_results2 = search_by_cat_and_role(vngl, [('NP', 'Agent'), ('PREP', 'None')] )
        print '\n(NP, Agent) and (PREP, None) classes:\n\n', [ID for frame,ID in catrole_results2]
        print len(catrole_results2)
        catrole_results3 = search_by_cat_and_role(vngl, [('NP', 'Agent'), ('VERB', 'None')], True )
        print '\n(NP, Agent) and (VERB, None) only classes:\n\n', [ID for frame,ID in catrole_results3]
        print len(catrole_results3)
    
    #test image schema searches
    def image_searches():
        print "\nin at on destination:\n"
        destination_results = image_schema_search2(vngl, ['in', 'at', 'on'], ['Destination'])
        print [vcid for frame,vcid in destination_results], len(destination_results)
        print "\nin at on location:\n"
        location_results = image_schema_search2(vngl, ['in', 'at', 'on'], ['Location'])
        print [vcid for frame,vcid in location_results], len(location_results)
        # figure out left-of right-of
        print "\nnear far:\n"
        nearfar_results = image_schema_search2(vngl, ['near', 'far'])
        print [vcid for frame,vcid in nearfar_results], len(nearfar_results)
        print "\nup-down:\n"
        updown_results = image_schema_search2(vngl, ['up', 'down', 'above', 'below'])
        print [vcid for frame,vcid in updown_results], len(updown_results)
        print "\nContact No-Contact on in:\n"
        contact_results = image_schema_search2(vngl, ['on', 'in'])
        print [vcid for frame,vcid in contact_results], len(contact_results)
        print "\nFront/Behind:\n"
        front_results = image_schema_search2(vngl, ['front', 'behind'])
        print [vcid for frame,vcid in front_results], len(front_results)
        #figure out advs of speed
        print "\nPath along on:\n"
        path_results = image_schema_search2(vngl, ['along', 'on'])
        print [vcid for frame,vcid in path_results], len(path_results)
        print "\nSource from:\n"
        source_results = image_schema_search2(vngl, ['from'], ['Initial_Location'])
        print [vcid for frame,vcid in source_results], len(source_results)
        print "\nEnd at to:\n"
        end_results = image_schema_search2(vngl, ['at', 'to'], ['Destination'])
        print [vcid for frame,vcid in end_results], len(end_results)
        print "\nDirectional toward away for:\n"
        directional_results = image_schema_search2(vngl, ['toward', 'away', 'for'], ['Source'])
        print [vcid for frame,vcid in directional_results], len(directional_results)
        print "\nContainer in inside:\n"
        container_results = image_schema_search2(vngl, ['in', 'inside'])
        print [vcid for frame,vcid in container_results], len(container_results)
        print "\nSurface over on:\n"
        surface_results = image_schema_search2(vngl, ['over', 'on'])
        print [vcid for frame,vcid in surface_results], len(surface_results)
        
    def new_image_searches():
        
        for scheme in SCHEME_LIST:
            results = image_schema_search(vngl, scheme)
            print "\n", scheme, "\nResults - " + str(len(results)) + " Frames:"
            print [vcid for frame,vcid in results]
        
    new_image_searches()