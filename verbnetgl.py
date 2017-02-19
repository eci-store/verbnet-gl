"""verbnetgl.py

This file contains the classes for the form of Verbnet that have been enhanced
with GL event structures. The classes themselves do all the conversion necessary
given a VerbClass from verbnetparser.py.

To run this do the following:

1. Copy config.sample.txt into config.txt
2. Edit config.txt by changing the verbnet location
3. Run this script without arguments

"""

import os, itertools

from verbnetparser import VerbNetParser
from imageschema import SCHEME_LIST
from search import search_by_predicate, search_by_argtype
from search import search_by_ID, search_by_subclass_ID
from search import search_by_themroles, search_by_POS, search_by_cat_and_role


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

    def argtypes(self):
        """Return a set of all the argtypes found in all frames."""
        argtypes = set()
        for frame in self.frames:
            for pred in frame.vnframe.predicates:
                for arg, arg_type in pred.argtypes:
                    argtypes.add(arg_type)
        return list(argtypes)

    def is_change_of_state_class(self):
        """Return True if the class is a change-of-state class, which is defined as
        having an argtype that contains ch_of in one of the frames."""
        return True if [t for t in self.argtypes() if 'ch_of_' in t] else False

    def is_change_of_info_class(self):
        """Return True if the class is a change-of-info class, which is defined as
        having an argtype that contains ch_of_info in one of the frames."""
        return True if [t for t in self.argtypes() if 'ch_of_info' in t] else False

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
            fh.write("\n<table class=frame cellpadding=8 cellspacing=0 border=0 width=1000>\n")
            self.pp_html_description(gl_frame, fh)
            self.pp_html_example(gl_frame, fh)
            self.pp_html_predicate(vn_frame, fh)
            self.pp_html_subcat(gl_frame, fh)
            self.pp_html_qualia(gl_frame, fh)
            self.pp_html_event(gl_frame, fh)
            fh.write("</table>\n\n")

    def pp_html_description(self, gl_frame, fh):
        #fh.write("<tr class=description>\n")
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
    
    def pp_image_html(self, fh, frame_numbers):
        fh.write("<html>\n")
        fh.write("<head>\n")
        fh.write("<link rel=\"stylesheet\" type=\"text/css\" href=\"style.css\">\n")
        fh.write("</head>\n")
        fh.write("<body>\n")
        fh.write("\n<h1>%s</h1>\n" % str(self.ID))
        for i in frame_numbers:
            vn_frame = self.verbclass.frames[i]
            gl_frame = self.frames[i]
            fh.write("\n<table cellpadding=8 cellspacing=0 border=0 width=1000>\n")
            fh.write("<tr class=header><td>Frame %s: " % i)
            self.pp_html_description(gl_frame, fh)
            self.pp_html_example(gl_frame, fh)
            self.pp_html_predicate(vn_frame, fh)
            self.pp_html_subcat(gl_frame, fh)
            self.pp_html_qualia(gl_frame, fh)
            self.pp_html_event(gl_frame, fh)
            fh.write("</table>\n\n")
            
    def pp_reverse_image_html(self, fh, frame_number):
        fh.write("<html>\n")
        fh.write("<head>\n")
        fh.write("<link rel=\"stylesheet\" type=\"text/css\" href=\"style.css\">\n")
        fh.write("</head>\n")
        fh.write("<body>\n")
        fh.write("\n<h1>%s</h1>\n" % str(self.ID))
        vn_frame = self.verbclass.frames[frame_number]
        gl_frame = self.frames[frame_number]
        fh.write("\n<table cellpadding=8 cellspacing=0 border=0 width=1000>\n")
        fh.write("<tr class=header><td>Frame %s: " % frame_number)
        self.pp_html_description(gl_frame, fh)
        self.pp_html_example(gl_frame, fh)
        self.pp_html_predicate(vn_frame, fh)
        self.pp_html_subcat(gl_frame, fh)
        self.pp_html_qualia(gl_frame, fh)
        self.pp_html_event(gl_frame, fh)
        fh.write("</table>\n\n")
    
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



class HtmlWriter(object):

    def __init__(self, directory='html'):
        self.directory = directory
        self.index = open(os.path.join(self.directory, 'index.html'), 'w')
        self._write_begin()

    def _write_begin(self):
        self.index.write("<html>\n")
        self.index.write("<head>\n")
        self.index.write("<link rel=\"stylesheet\" type=\"text/css\" href=\"style.css\">\n")
        self.index.write("</head>\n")
        self.index.write("<body>\n")
        self.index.write("<table class=noborder >\n")
        self.index.write("<tr valign=top>\n")

    def write(self, results, header, group=''):
        self.index.write("<td>\n")
        self.index.write("<table cellpadding=8 cellspacing=0>\n")
        self.index.write("<tr class=header><td>%s</a>\n" % header)
        for result in results:
            infix = group + '-' if group else ''
            class_file = "vnclass-%s%s.html" % (infix, result.ID)
            self.index.write("<tr class=vnlink><td><a href=\"%s\">%s</a>\n" % (class_file, result.ID))
            fh =  open(os.path.join(self.directory, class_file), 'w')
            result.pp_html(fh)
        self.index.write("</table>\n")
        self.index.write("</td>\n")

    def finish(self):
        self.index.write("</tr>\n")
        self.index.write("</table>\n")
        self.index.write("</body>\n")
        self.index.write("</html>\n")


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


def pp_image_search_html(verbclasslist, results):
    """Uses a list of [image_search_name, search_results]"""
    INDEX = open('html/image_search_index.html', 'w')
    INDEX.write("<html>\n")
    INDEX.write("<head>\n")
    INDEX.write("<link rel=\"stylesheet\" type=\"text/css\" href=\"style.css\">\n")
    INDEX.write("</head>\n")
    INDEX.write("<body>\n")
    INDEX.write("<table cellpadding=8 cellspacing=0>\n")
    for result in results:
        scheme = result[0]
        INDEX.write("<tr class=header><td>%s</a>\n" % scheme.name)
        INDEX.write("<tr class=header><td>PP List: %s</a>\n" % scheme.pp_list)
        INDEX.write("<tr class=header><td>Selectional Restrictions: %s</a>\n" % scheme.sel_res_list)
        INDEX.write("<tr class=header><td>Thematic Roles: %s</a>\n" % scheme.role_list)
        if len(results[1]) == 0:
            INDEX.write("<tr class=body><td>No Results\n")
        for vc_id, class_results in result[1]:
            id_dict = {}
            for frame,frame_num,ID in class_results:
                results_type = []
                for member in frame.subcat:
                    if member.cat == "PREP":
                        if len(member.role) > 0:
                            if member.role[0] in scheme.pp_list:
                                results_type.append("PP")
                        if len(member.sel_res) > 0:
                            for res in member.sel_res:
                                if res in scheme.sel_res_list:
                                    results_type.append("SR")
                    if len(member.role) > 0:
                        if member.role[0] in scheme.role_list:
                            results_type.append("TR")
                if ID in id_dict:
                    id_dict[ID].append((frame_num, results_type))
                else:
                    id_dict[ID] = [(frame_num, results_type)]
            for ID in id_dict.keys():
                class_file = "imageresult-%s.html" % ID
                INDEX.write("<tr class=body><td><a href=\"%s\">%s</a>\n" % (class_file, ID))
                INDEX.write("  <td>")
                for frame_num,results_type in sorted(id_dict[ID]):
                    INDEX.write("Frame %s" % frame_num)
                    for result in results_type:
                        INDEX.write("<sup>%s</sup> " % result)
                    INDEX.write("&emsp;")
                VNCLASS = open("html/%s" % class_file, 'w')
                verbclass = search_by_ID(verbclasslist, ID)
                verbclass.pp_image_html(VNCLASS, sorted([num for num,type in id_dict[ID]]))
    INDEX.write("</table>\n")
    INDEX.write("</body>\n")
    INDEX.write("</html>\n")


def pp_reverse_image_search_html(verbclasslist, frame_list, scheme_list):
    INDEX = open('html/image_search_reverse_index.html', 'w')
    INDEX.write("<html>\n")
    INDEX.write("<head>\n")
    INDEX.write("<link rel=\"stylesheet\" type=\"text/css\" href=\"style.css\">\n")
    INDEX.write("</head>\n")
    INDEX.write("<body>\n")
    INDEX.write("<table cellpadding=8 cellspacing=0>\n")
    INDEX.write("<tr class=header><td>Reverse Image Search Results:\n</a>")
    for frame,frame_num,ID in sorted(set(frame_list)):
        results = []
        for scheme in scheme_list:
            if reverse_image_search(frame, scheme):
                results.append(scheme.name)
        INDEX.write("<tr class=body><td>%s</a>" % ID)
        class_file = "imageresultreverse-%s_frame%s.html" % (ID, frame_num)
        INDEX.write("<a href=\"%s\"> - Frame %s</a>" % (class_file, frame_num))
        INDEX.write("  <td>")
        if len(results) == 0:
            INDEX.write("-\n")
        for i in range(len(results)):
            if i < len(results) - 1:
                INDEX.write("%s, " % results[i])
            else:
                INDEX.write("%s\n" % results[i])
        VNCLASS = open("html/%s" % class_file, 'w')
        verbclass = search_by_ID(verbclasslist, ID)
        verbclass.pp_reverse_image_html(VNCLASS, frame_num)
    INDEX.write("</table>\n")
    INDEX.write("</body>\n")
    INDEX.write("</html>\n")


def pp_reverse_image_bins_html(verbclasslist, frame_list, scheme_list):
    INDEX = open('html/image_search_bins_index.html', 'w')
    INDEX.write("<html>\n")
    INDEX.write("<head>\n")
    INDEX.write("<link rel=\"stylesheet\" type=\"text/css\" href=\"style.css\">\n")
    INDEX.write("</head>\n")
    INDEX.write("<body>\n")
    INDEX.write("<table cellpadding=8 cellspacing=0>\n")
    image_bins = dict()
    for frame,frame_num,ID in sorted(set(frame_list)):
        results = set()
        for scheme in scheme_list:
            if reverse_image_search(frame, scheme):
                results.add(scheme.name)
        if frozenset(results) in image_bins.keys():
            image_bins[frozenset(results)].append((frame, frame_num, ID))
        else:
            image_bins[frozenset(results)] = [(frame, frame_num, ID)]
    for bin in image_bins.keys():
        INDEX.write("<tr class=header><td></a>")
        if len(bin) == 0:
            INDEX.write("PP Only Frames:")
        for scheme in bin:
            INDEX.write("%s&emsp;" % scheme)
        INDEX.write("<tr class=body><td></a>")
        for frame, frame_num, ID in image_bins[bin]:
            class_file = "imageresultbins-%s_frame%s.html" % (ID, frame_num)
            INDEX.write("<a href=\"%s\">%s<sup>%s&emsp;</sup></a>" % (class_file, ID, frame_num))
            VNCLASS = open("html/%s" % class_file, 'w')
            verbclass = search_by_ID(verbclasslist, ID)
            verbclass.pp_reverse_image_html(VNCLASS, frame_num)
    INDEX.write("</table>\n")
    INDEX.write("</body>\n")
    INDEX.write("</html>\n")


def test1(vn_classes):
    """Just print the first class."""
    print vn_classes[0]


def test2(vn_classes):
    """Print a list of classes that match a couple of hand-picked predicates."""
    preds = ["motion", "transfer", "adjust", "cause", "transfer_info",
             "emotional_state", "location", "state", "wear"]
    results = { p: search_by_predicate(vn_classes, p) for p in preds }
    result_classes = [i for i in itertools.chain.from_iterable(results.values())]
    result_classes = sorted(set(result_classes))
    writer = HtmlWriter()
    writer.write(result_classes, "VN Classes")


def test3(vn_classes):
    """This is what produces the output with motion classes, possession classes,
    change of state classes and chango of info classes."""
    # TODO. We have three ways of finding classes: doing a search, setting a
    # list manually, and checking a test method on the classes. Should probably
    # use only one way of doing this.

    motion_vcs = search_by_predicate(vn_classes, "motion")
    transfer_vcs = search_by_predicate(vn_classes, "transfer")

    # possession_results = search(vn_classes, "has_possession")
    # print len(possession_results), [vc.ID for vc in possession_results]

    # we only find three with the above so define them manually
    possession = ['berry-13.7', 'cheat-10.6', 'contribute-13.2', 'equip-13.4.2',
                 'exchange-13.6.1', 'fulfilling-13.4.1', 'get-13.5.1', 'give-13.1',
                 'obtain-13.5.2', 'steal-10.5']
    possession_vcs = [vc for vc in vn_classes if vc.ID in possession]

    ch_of_state_vcs = [vc for vc in vn_classes if vc.is_change_of_state_class()]
    ch_of_info_vcs = [vc for vc in vn_classes if vc.is_change_of_info_class()]

    writer = HtmlWriter()
    writer.write(motion_vcs + transfer_vcs, 'VN Motion Classes', 'motion')
    writer.write(possession_vcs, 'VN Posession Classes', 'poss')
    writer.write(ch_of_state_vcs, 'VN Change of State Classes', 'ch_of_x')
    writer.write(ch_of_info_vcs, 'VN Change of Info Classes', 'ch_of_info')
    writer.finish()



def test_ch_of_searches():
    # find all 'ch_of_' verb classes
    ch_of_results = search_by_argtype(vn_classes, 'ch_of_', True)
    print '\nch_of_\n', ch_of_results, len(ch_of_results)
    results = search_by_argtype(vn_classes, 'ch_of_info')
    print '\nch_of_info\n', results, len(results)
    results = search_by_argtype(vn_classes, 'ch_of_pos')
    print '\nch_of_pos\n', results, len(results)
    results = search_by_argtype(vn_classes, 'ch_of_poss')
    print '\nch_of_poss\n', results, len(results)
    results = search_by_argtype(vn_classes, 'ch_of_state')
    print '\nch_of_state\n', results, len(results)
    results = search_by_argtype(vn_classes, 'ch_of_loc')
    print '\nch_of_loc\n', results, len(results)
    results = search_by_argtype(vn_classes, 'ch_of_location')
    print '\nch_of_location\n', results, len(results)
    # print search_by_ID(vn_classes, 'give', True)[0]
    # transfer possession verbs
    # transpos = search_by_argtype(transfer_results, 'ch_of_pos', True)
    # print '\nTransfer Possession:\n', transpos, len(transpos)
    # path_rel_results = search(vn_classes, "path_rel")
    # print '\nNumber of path_rel classes:\n', len(path_rel_results)
    # path_less_ch = [vc.ID for vc in path_rel_results if vc.ID not in ch_of_results]
    # print '\npath_rel classes with no ch_of\n', path_less_ch
    

def test_new_searches():
    print "\n\nVerbclasses with Agent and Patient thematic roles:"
    them_results = search_by_themroles(vn_classes, ['Agent', 'Patient'])
    print '\n', [vc.ID for vc in them_results], '\n', len(them_results)
    them_results2 = search_by_themroles(vn_classes, ['Agent', 'Patient'], True)
    print '\nAgent and Patient only classes:\n\n', [vc.ID for vc in them_results2]
    print len(them_results2)
    print "\n\nVerbclasses with frames with NP and VERB syntactic roles:"
    pos_results = search_by_POS(vn_classes, ['NP', 'VERB'])
    print '\n', len(pos_results)
    pos_results2 = search_by_POS(vn_classes, ['NP', 'VERB'], True)
    print '\nNP and VERB only classes:\n\n', [ID for frame,ID in pos_results2]
    print len(pos_results2)
    print "\n\nVerbclasses with frames with (NP, Agent) subcat members:"
    catrole_results = search_by_cat_and_role(vn_classes, [('NP', 'Agent')] )
    print '\n', len(catrole_results)
    catrole_results2 = search_by_cat_and_role(vn_classes, [('NP', 'Agent'), ('PREP', 'None')] )
    print '\n(NP, Agent) and (PREP, None) classes:\n\n', [ID for frame,ID in catrole_results2]
    print len(catrole_results2)
    catrole_results3 = search_by_cat_and_role(vn_classes, [('NP', 'Agent'), ('VERB', 'None')], True )
    print '\n(NP, Agent) and (VERB, None) only classes:\n\n', [ID for frame,ID in catrole_results3]
    print len(catrole_results3)
    
    
def test_image_searches():
    print "\nin at on destination:\n"
    destination_results = image_schema_search2(vn_classes, ['in', 'at', 'on'], ['Destination'])
    print [vcid for frame,vcid in destination_results], len(destination_results)
    print "\nin at on location:\n"
    location_results = image_schema_search2(vn_classes, ['in', 'at', 'on'], ['Location'])
    print [vcid for frame,vcid in location_results], len(location_results)
    # figure out left-of right-of
    print "\nnear far:\n"
    nearfar_results = image_schema_search2(vn_classes, ['near', 'far'])
    print [vcid for frame,vcid in nearfar_results], len(nearfar_results)
    print "\nup-down:\n"
    updown_results = image_schema_search2(vn_classes, ['up', 'down', 'above', 'below'])
    print [vcid for frame,vcid in updown_results], len(updown_results)
    print "\nContact No-Contact on in:\n"
    contact_results = image_schema_search2(vn_classes, ['on', 'in'])
    print [vcid for frame,vcid in contact_results], len(contact_results)
    print "\nFront/Behind:\n"
    front_results = image_schema_search2(vn_classes, ['front', 'behind'])
    print [vcid for frame,vcid in front_results], len(front_results)
    #figure out advs of speed
    print "\nPath along on:\n"
    path_results = image_schema_search2(vn_classes, ['along', 'on'])
    print [vcid for frame,vcid in path_results], len(path_results)
    print "\nSource from:\n"
    source_results = image_schema_search2(vn_classes, ['from'], ['Initial_Location'])
    print [vcid for frame,vcid in source_results], len(source_results)
    print "\nEnd at to:\n"
    end_results = image_schema_search2(vn_classes, ['at', 'to'], ['Destination'])
    print [vcid for frame,vcid in end_results], len(end_results)
    print "\nDirectional toward away for:\n"
    directional_results = image_schema_search2(vn_classes, ['toward', 'away', 'for'], ['Source'])
    print [vcid for frame,vcid in directional_results], len(directional_results)
    print "\nContainer in inside:\n"
    container_results = image_schema_search2(vn_classes, ['in', 'inside'])
    print [vcid for frame,vcid in container_results], len(container_results)
    print "\nSurface over on:\n"
    surface_results = image_schema_search2(vn_classes, ['over', 'on'])
    print [vcid for frame,vcid in surface_results], len(surface_results)

    
def test_search_by_ID():
    print search_by_ID(vn_classes, "swarm-47.5.1").subclasses[1]

    
def new_image_searches():
    results = []
    for scheme in SCHEME_LIST:
        result = image_schema_search(vn_classes, scheme)
        results.append((scheme, result))
    return results


def reverse_image_frame_list():
    image_results = new_image_searches()
    frame_list = []
    for scheme, results in image_results:
        for vc_id, class_results in results:
            for frame,frame_num,ID in class_results:
                frame_list.append((frame, frame_num, ID))
    return frame_list


def create_schema_to_verbnet_mappings():
    image_results = new_image_searches()
    frames = reverse_image_frame_list()
    pp_image_search_html(vn_classes, image_results)
    pp_reverse_image_search_html(vn_classes, frames, SCHEME_LIST)
    pp_reverse_image_bins_html(vn_classes, frames, SCHEME_LIST)



if __name__ == '__main__':

    vn = VerbNetParser()
    vn_classes = [GLVerbClass(vc) for vc in vn.verb_classes]

    #test1(vn_classes)
    #test2(vn_classes)
    test3(vn_classes)

    #test_ch_of_searches()
    #test_new_searches()
    #test_image_searches()
    #test_search_by_ID()

    #create_schema_to_verbnet_mappings()
