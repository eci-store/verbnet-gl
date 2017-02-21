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
from writer import HtmlWriter, HtmlClassWriter
#from writer import pp_image_search_html
#from writer import pp_reverse_image_search_html
#from writer import pp_reverse_image_bins_html
from search import search_by_predicate, search_by_argtype
from search import search_by_ID, search_by_subclass_ID
from search import search_by_themroles, search_by_POS, search_by_cat_and_role
from search import reverse_image_search, image_schema_search, image_schema_search2


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
        
    def __repr__(self):
        return str(self.ID) + " = {\n\nroles = " + str(self.roles) + \
               "\n\nframes = " + str(self.frames) + "\n}" + \
               "\n Subclasses = " + str(self.subclasses)

    def is_motion_class(self):
        """Return True if one of the frames is a motion frame."""
        for f in self.frames:
            if f.is_motion_frame():
                return True
        return False

    def frames(self):
        return [GLFrame(self, frame) for frame in self.verbclass.frames]

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
    

class GLSubclass(GLVerbClass):
    """Represents a subclass to a GLVerbClass. This needs to be different from
    GLVerbClass because VerbNet seems to change the THEMROLES section of the 
    subclass to only include thematic roles that differ from the main class,
    but does not list all the roles that stay the same. Since we need to update 
    self.roles, we can't call __init__ on the superclass because that would call
    self.frames and self.subclasses before we updated our roles properly."""
    
    # TODO: check this for proper nesting
    
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
    
    def __init__(self, glverbclass, frame):
        self.glverbclass = glverbclass
        self.vnframe = frame                    # instance of verbnetparser.Frame
        self.class_roles = glverbclass.roles    # list of verbnetparser.ThematicRoles
        self.pri_description = frame.primary    # list of unicode strings
        self.sec_description = frame.secondary  # list of unicode strings
        self.example = frame.examples           # list of unicode strings
        self.subcat = self.subcat()             # list of SubcatMember
        self.qualia = None
        self.event_structure = EventStructure()
        self.role2var = None                    # auxiliary dictionary
        #self.event_and_opposition_structure2()
        #self.XXX_event_and_opposition_structure()
        self.set_motion_opposition()

    def __str__(self):
        return "<GLFrame %s [%s] '%s'>" % \
            (self.glverbclass.ID, ' '.join(self.pri_description), self.example[0])

    def __repr__(self):
        return "\n\n{ description = " + str(" ".join(self.pri_description)) + \
            "\nexample = " + str(self.example[0]) + \
            "\nsubcat = " + str(self.subcat) + \
            "\nqualia = " + str(self.qualia) + \
            "\nevent_structure = {" + str(self.event_structure) + "\t}\n"

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
    

    def event_and_opposition_structure2(self):
        """Uses the frame information to determine what initial and final states
        should look like, given the variables available in the subcat frame, and
        the roles for the verb class."""

        # TODO: after some refactoring this method is still way too hard to
        # understand and it must be completely changed

        states = []
        type_of_change = None
        member_vars = self._get_variables()  # all subcat members that have a variable
        start = []
        end = []
        pred_type = self._find_opposition_predicate()
        #self._debug0(member_vars, pred_type)

        if pred_type:
            equals = []
            changers = []

            for pred in self.vnframe.predicates:
                if pred.value[0] == 'path_rel': 
                    changer, opposition = self._set_changer_and_opposition(pred, member_vars)
                    #print pred
                    #print '   changer', changer
                    #print '   opposition', opposition
                    type_of_change = self._set_type_of_change(pred)
                    self._update_start_and_end(pred, changer, opposition, start, end)
                if pred.value[0] == 'equals':
                    equals.append(tuple(value for argtype, value in pred.argtypes))
            #self._debug1(equals, start, end, member_vars, pred_type)

            # Go through all objects that change state, and if beginning and end
            # are expressed syntactically, create the opposition. (HUH: if I try
            # to make this one method _add_oppositions_to_states then it chokes
            # on changer not being available, it is fine with the code below
            # though)
            for changer_s, opposition_s in start:
                start_opp = self._get_start_opp(equals, opposition_s)
                self._add_opposition_to_states(end, changers, changer, changer_s,
                                               equals, member_vars, start_opp, states)

            # Check for objects that only appear syntactically as an end        
            for changer, opposition in end:
                self._add_opposition_to_states2(changers, changer, opposition, equals, member_vars, states)

            # No path_rel predicates
            if len(changers) == 0:
                changer = '?'
                for pred in self.vnframe.predicates:
                    if pred.value[0] == pred_type:
                        changer = pred.argtypes[1][1]
                changer_var = member_vars.get(changer, changer)
                start_state = State(changer_var, '?')
                final_state = State(changer_var, '-?')
                states.append(tuple((start_state, final_state)))
                    
        opposition = Opposition(type_of_change, states)
        print self
        self.event_structure = EventStructure(states)
        self.qualia = Qualia(pred_type, opposition)


    def _get_variables(self):
        """Returns a dictionary of roles and variables from all elements of the
        subcategorisation frame. The dictionary is indexed on the roles and
        variables are integers, for example {'Beneficiary': 0, 'Agent': 1}."""
        member_vars = {}
        for submember in self.subcat:
            #print '  ', submember.var, submember.role
            if submember.var not in [None, "e"]:
                member_vars[submember.role[0]] = submember.var
        return member_vars

    def _find_opposition_predicate(self):
        """Check whether one of the predicates in the frame is deemed intersting for
        oppositions.  Returns None if there is no such predicate and returns the
        predicate value of the last one of those predicates if there is one."""
        pred_type = None
        for pred in self.vnframe.predicates:
            #print '  ', pred
            if pred.value[0] in ['motion', 'transfer', 'cause', 'transfer_info', \
                'adjust', 'emotional_state', 'location', 'state', 'wear']:
                pred_type = pred.value[0]
        return pred_type

    def _set_type_of_change(self, pred):
        """Check the argument types of the predicate for certain change predicates, if
        there is one then return 'pos', 'loc', 'info' or 'state', else return None."""
        # TODO: this relies on there being at least 4 argtypes in the predicate,
        # is that kosher?
        type_of_change = None
        if pred.argtypes[3][1] == 'ch_of_poss' or pred.argtypes[3][1] == 'ch_of_pos':
            type_of_change = "pos"
        if pred.argtypes[3][1] == 'ch_of_loc' or pred.argtypes[3][1] == 'ch_of_location':
            type_of_change = "loc"
        if pred.argtypes[3][1] == 'ch_of_info':
            type_of_change = "info"
        if pred.argtypes[3][1] == 'ch_of_state':
            type_of_change = "state"
        return type_of_change

    def _set_changer_and_opposition(self, pred, member_vars):
        """Check to see where the object that changes is, and where that object
        is or who owns it."""
        # TODO: find out why this works
        # NOTE: it does not seem to do the right thing on first glance
        if pred.argtypes[1][1] in member_vars.keys():
            changer = pred.argtypes[1][1]       # object that changes
            opposition = pred.argtypes[2][1]    # where the object is or who owns it
        else:
            changer = pred.argtypes[2][1]       # object that changes
            opposition = pred.argtypes[1][1]
        return changer, opposition

    def _update_start_and_end(self, pred, changer, opposition, start, end):
        """Add (changer, opposition) pair to start and/or end if predicate includes
        start(E) or end(E) argtype."""
        if pred.argtypes[0][1] == 'start(E)':
            start.append(tuple((changer, opposition)))
        if pred.argtypes[0][1] == 'end(E)':
            end.append(tuple((changer, opposition)))

    def _get_start_opp(self, equals, opposition_s):
        start_opp = opposition_s
        if len(equals) > 0:
            for pair in equals:
                if pair[1] == opposition_s:
                    start_opp = pair[0]
        return start_opp

    def _get_end_opp(self, equals, opposition_e):
        end_opp = opposition_e
        if len(equals) > 0:
            for pair in equals:
                if pair[1] == opposition_e:
                    end_opp = pair[0]
        return end_opp

    def _add_opposition_to_states(self, end, changers, changer, changer_s, equals,
                                  member_vars, start_opp, states):
        """Adds opposition to states for those cases where both the initial and the
        final state are expressed."""
        changer_s_var = member_vars.get(changer_s, changer_s)
        opp_s_var = member_vars.get(start_opp, '?')
        is_end = False
        for changer_e, opposition_e in end:
            if changer_s == changer_e:
                is_end = True
                changers.append(changer_s)
                end_opp = self._get_end_opp(equals, opposition_e)
                opp_e_var = member_vars.get(end_opp, '?')
                start_state = State(changer_s_var, opp_s_var)
                final_state = State(changer_s_var, opp_e_var)
                states.append(tuple((start_state, final_state)))
        if not is_end:
            changers.append(changer)
            start_state = State(changer_s_var, opp_s_var)
            final_state = State(changer_s_var, "-" + str(opp_s_var))
            states.append(tuple((start_state, final_state)))

    def _add_opposition_to_states2(self, changers, changer, opposition,
                                   equals, member_vars, states):
        """Adds opposition to states for those cases where only the final state is
        expressed."""
        if changer not in changers:
            changers.append(changer)
            end_opp = opposition
            if len(equals) > 0:
                for pair in equals:
                    if pair[1] == opposition:
                        end_opp = pair[0]
            changer_var = member_vars.get(changer, changer)
            opp_var = member_vars.get(end_opp, '?')
            start_state = State(changer_var, "-" + str(opp_var))
            final_state = State(changer_var, opp_var)
            states.append(tuple((start_state, final_state)))

    def _debug0(self, member_vars, pred_type):
        print "\n", self.glverbclass.ID, ' '.join(self.pri_description)
        print '  ', member_vars
        print '   pred_type =', pred_type

    def _debug1(self, equals, start, end, member_vars, pred_type):
        if equals or start or end:
            print "\n", self.glverbclass.ID, ' '.join(self.pri_description)
            print "   member_vars = %s" % member_vars 
            print "   pred_type   = %s" % pred_type
            print "   equals      = %s" % equals
            print "   start       = [%s]" % ', '.join(["%s-%s" % (x, y) for x, y in start])
            print "   end         = [%s]" % ', '.join(["%s-%s" % (x, y) for x, y in end])


    def find_predicates(self, pred_value):
        """Returns the list of Predicates where the value equals pred_value."""
        return [p for p in self.vnframe.predicates if p.value[0] == pred_value]

    def find_arguments(self, pred, arg):
        """Return all arguments in pred where arg matches one of the argument's elements
        (note that arguments are tuples of two strings, like <Event,during(E)>
        or <ThemRole,Theme>)."""
        # TODO: should be on Predicate
        return [a for a in pred.argtypes if arg in a]

    def is_motion_frame(self):
        """Returns True if one of the predicates is 'motion', returns False otherwise."""
        return True if self.find_predicates('motion') else False

    def set_motion_opposition(self):
        if self.is_motion_frame():
            self.role2var = self._get_variables()
            initial_location, destination = None, None
            moving_object = self._get_moving_object()
            agent = self._get_agent()
            initial_location = self._get_initial_location()
            destination = self._get_destination()
            self._add_default_opposition(initial_location, destination)
            initial_state = State(moving_object[1], initial_location[1])
            final_state = State(moving_object[1], destination[1])
            opposition = Opposition('loc', [[initial_state, final_state]])
            self.event_structure = EventStructure([[initial_state, final_state]])
            self.qualia = Qualia('motion', opposition)
            if self.glverbclass.ID in ('run-51.3.2', 'slide.11.2'):
                return
                print; print self;
                self.pp_predicates(3); self.pp_subcat(3), self.pp_variables(3)
                print '   agent  =', agent
                print '   object =', moving_object
                print '   start  =', initial_location
                print '   end    =', destination
                print '  ', initial_state
                print '  ', final_state

    def _get_moving_object(self):
        """Get the role and the index of the moving object. Assumes that the moving
        object is always the theme."""
        motion_predicates = self.find_predicates('motion')
        if motion_predicates:
            args = self.find_arguments(motion_predicates[0], 'Theme')
            if not args:
                print "WARNING: missing Theme in Motion predicate", self
        else:
            print "WARNING: no Motion predicate found in", self
        return ['Theme', str(self.role2var.get('Theme', '?'))]

    def _get_agent(self):
        """Get the role and index of the agent of the movement. Assumes the
        cause is the agent."""
        cause_predicates = self.find_predicates('cause')
        if cause_predicates:
            args = self.find_arguments(cause_predicates[0], 'Agent')
            if not args:
                print 'WARNING: missing Agent in Cause predicate'
        return ['Agent', str(self.role2var.get('Agent', '?'))]

    def _get_initial_location(self):
        """For now just return the Initial_Location role and the index of it, if any. No
        checking of predicates and no bitchy messages on missing roles."""
        # TODO: using list of string, should perhaps use some class
        return ['Initial_Location', str(self.role2var.get('Initial_Location', '?'))]

    def _get_destination(self):
        """For now just return the Destination role and the index of it, if any. No
        checking of predicates and no bitchy messages on missing roles."""
        return ['Destination', str(self.role2var.get('Destination', '?'))]

    def _add_default_opposition(self, initial_location, destination):
        """Sneaky way of adding in the opposition in case one or both of the locations
        are anonymous. Overgenerates for those cases where motion is in-place."""
        if initial_location[1] == '?' or destination[1] == '?':
            if initial_location[1] == '?' and destination[1] == '?':
                destination[1] = '-?'
            elif initial_location[1] == '?':
                initial_location[1] = '-' + destination[1]
            elif destination[1] == '?':
                destination[1] = '-' + initial_location[1]

    def pp_predicates(self, indent=0):
        print "%spredicates" % (indent * ' ')
        for p in self.vnframe.predicates:
            print "%s   %s" % (indent * ' ', p)

    def pp_subcat(self, indent=0):
        print "%ssubcat" % (indent * ' ')
        for sc in self.subcat:
            print "%s   %s" % (indent * ' ', sc)

    def pp_variables(self, indent=0):
        print "%svariables = { %s }" \
            % (indent * ' ',
               ', '.join(["%s(%s)" % (r, v) for r, v in self.role2var.items()]))


class SubcatMember(object):

    """A combination of SyntacticRole and ThematicRole."""

    def __init__(self, var, synrole, themrole):
        self.var = var
        self.cat = synrole.POS
        self.role = synrole.value   #themrole.role_type won't work
        if themrole is not None:
            self.sel_res = themrole.sel_restrictions
        else:
            self.sel_res = synrole.restrictions

    def __repr__(self):
        return "{ var = %s, cat = %s, role = %s } / %s " \
            % (self.var, self.cat, self.role, self.sel_res)


class State(object):
    
    """Represents a state in the event structure For motion verbs, this gives the
    variable assignment of the mover, and its location. For transfer verbs, this
    gives the variable assignment of the object being transferred, and what
    currently owns the object."""

    # TODO. Should probably have several kinds of states, this one really is the
    # state of an object being at a position (or being owned). Should als make a
    # State a list of assignments rather than just the one.

    # TODO: add frame as an instance variable

    def __init__(self, obj_var, pos_var):
        self.object = obj_var
        self.position = pos_var
        
    def __repr__(self):
        return "{ objects.%s.location = %s }" % (self.object, self.position)


class EventStructure(object):

    """Defines the event structure for a particular frame of a verb"""

    # TODO: adopt a list of states instead of just initial and final.
    # TODO: add frame as an instance variable

    def __init__(self, states=None):
        #if len(states) != 1: print states
        #if states and len(states[0]) != 2: print states
        if states is None:
            states = []
        self.var = "e"
        self.initial_state = [state1 for state1, state2 in states]
        self.final_state = [state2 for state1, state2 in states]

    def __repr__(self):
        return "{ var = %s, initial_state = %s, final_state = %s }" \
            % (self.var, self.initial_state, self.final_state)


class Opposition(object):

    """Represents the opposition structure of the frame. Right now only tailored for
    locations. Technically, an opposition should only have two states, but we
    allow there to be a longer list."""
    
    def __init__(self, type_of_change, states):
        self.type_of_change = type_of_change
        self.states = states
        
    def __repr__(self):
        operator_mappings = { 'pos': 'Has', 'info': 'Knows', 'state': 'State' }
        op = operator_mappings.get(self.type_of_change, 'At')
        return ' '.join(["(%s(%s, %s), %s(%s, %s))" % \
                         (op, start.object, start.position, op, end.object, end.position)
                         for start, end in self.states])
 
 
class Qualia(object):

    """Represents the qualia structure of a verbframe, including opposition
    structure."""
    
    def __init__(self, pred_type, opposition):
        self.formal = pred_type
        self.opposition = opposition
        
    def __repr__(self):
        return "{ formal = " + str(self.formal) + "(e) AND Opposition" + \
               str(self.opposition) + "}"


# The following five functions should be moved to writer.py, but they cannot be
# moved as is because of dependencies to methods in this file. Some refactoring
# is needed.

def pp_image_search_html(verbclasslist, results):
    """Uses a list of [image_search_name, search_results]"""
    INDEX = open('html/image_search_index.html', 'w')
    pp_html_begin(INDEX)
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
                class_writer = HtmlClassWriter(VNCLASS, verbclass)
                frame_numbers = sorted([num for num,type in id_dict[ID]])
                class_writer.write(frames=frame_numbers)
    pp_html_end(INDEX)


def pp_reverse_image_search_html(verbclasslist, frame_list, scheme_list):
    INDEX = open('html/image_search_reverse_index.html', 'w')
    pp_html_begin(INDEX)
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
        class_writer = HtmlClassWriter(VNCLASS, verbclass)
        class_writer.write(frames=[frame_num])
    pp_html_end(INDEX)


def pp_reverse_image_bins_html(verbclasslist, frame_list, scheme_list):
    INDEX = open('html/image_search_bins_index.html', 'w')
    pp_html_begin(INDEX)
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
            class_writer = HtmlClassWriter(VNCLASS, verbclass)
            class_writer.write(frames=[frame_num])
    pp_html_end(INDEX)


def pp_html_begin(fh):
    fh.write("<html>\n")
    fh.write("<head>\n")
    fh.write("<link rel=\"stylesheet\" type=\"text/css\" href=\"style.css\">\n")
    fh.write("</head>\n")
    fh.write("<body>\n")
    fh.write("<table cellpadding=8 cellspacing=0>\n")


def pp_html_end(fh):
    fh.write("</table>\n")
    fh.write("</body>\n")
    fh.write("</html>\n")


# Some test functions, at least test3() and create_schema_to_verbnet_mappings()
# should be promoted to non-test functions and be triggered by command line
# options or from another script.

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


def test_ch_of_searches(vn_classes):
    # find all 'ch_of_' verb classes
    print
    for argtype in ('ch_of_', 'ch_of_info', 'ch_of_pos', 'ch_of_poss',
                    'ch_of_state', 'ch_of_loc', 'ch_of_location'):
        results = search_by_argtype(vn_classes, argtype)
        print "%s %s %s\n" % (len(results), argtype, ' '.join(results))
    path_rel_results = search_by_argtype(vn_classes, "path_rel")
    print 'number of path_rel classes:', len(path_rel_results)
    path_less_ch = [vc.ID for vc in path_rel_results if vc.ID not in ch_of_results]
    print 'path_rel classes with no ch_of:', path_less_ch, "\n"


def test_new_searches(vn_classes):
    for print_string, function, role_list, boolean in [
            ("Verbclasses with Agent and Patient thematic roles:", search_by_themroles, ['Agent', 'Patient'], False),
            ('Agent and Patient only classes:', search_by_themroles, ['Agent', 'Patient'], True),
            ("Verbclasses with frames with NP and VERB syntactic roles:", search_by_POS, ['NP', 'VERB'], False),
            ('NP and VERB only classes:', search_by_POS, ['NP', 'VERB'], True),
            ("Verbclasses with frames with (NP, Agent) subcat members:", search_by_cat_and_role, [('NP', 'Agent')], False),
            ('(NP, Agent) and (PREP, None) classes:', search_by_cat_and_role, [('NP', 'Agent'), ('PREP', 'None')], False),
            ('(NP, Agent) and (VERB, None) only classes:', search_by_cat_and_role, [('NP', 'Agent'), ('VERB', 'None')], True) ]:
        results = function(vn_classes, role_list, boolean)
        ids = []
        if results:
            ids = [vc.ID for vc in results] if isinstance(results[0], GLVerbClass) \
                  else [ID for frame, ID in results]
            ids = sorted(list(set(ids)))
        print "\nThere are %s cases of %s" % (len(ids), print_string)
        print '  ', "\n   ".join([id for id in ids])

    
def test_image_searches(vn_classes):
    # figure out left-of right-of
    # figure out advs of speed
    print
    for print_string, pp_list, sem_list in [
            ("in at on destination:", ['in', 'at', 'on'], ['Destination']),
            ("in at on location:", ['in', 'at', 'on'], ['Location']),
            ("near far:", ['near', 'far'], None),
            ("up-down:", ['up', 'down', 'above', 'below'], None),
            ("Contact No-Contact on in:", ['on', 'in'], None),
            ("Front/Behind:", ['front', 'behind'], None),
            ("Path along on:", ['along', 'on'], None),
            ("Source from:", ['from'], ['Initial_Location']),
            ("End at to:", ['at', 'to'], ['Destination']),
            ("Directional toward away for:", ['toward', 'away', 'for'], ['Source']),
            ("Container in inside:", ['in', 'inside'], None),
            ("Surface over on:", ['over', 'on'], None) ]:
        results = image_schema_search2(vn_classes, pp_list, sem_list)
        print print_string
        print [vcid for frame, vcid in results], len(results), "\n"


def test_search_by_ID(vn_classes):
    print search_by_ID(vn_classes, "swarm-47.5.1").subclasses[1]


def new_image_searches(vn_classes):
    results = []
    for scheme in SCHEME_LIST:
        result = image_schema_search(vn_classes, scheme)
        results.append((scheme, result))
    return results


def reverse_image_frame_list(vn_classes):
    image_results = new_image_searches(vn_classes)
    frame_list = []
    for scheme, results in image_results:
        for vc_id, class_results in results:
            for frame,frame_num,ID in class_results:
                frame_list.append((frame, frame_num, ID))
    return frame_list


def create_schema_to_verbnet_mappings(vn_classes):
    image_results = new_image_searches(vn_classes)
    frames = reverse_image_frame_list(vn_classes)
    pp_image_search_html(vn_classes, image_results)
    pp_reverse_image_search_html(vn_classes, frames, SCHEME_LIST)
    pp_reverse_image_bins_html(vn_classes, frames, SCHEME_LIST)


def print_motion_classes():
    """Print a list of all classes that have a motion frame."""
    vn = VerbNetParser()
    vn_classes = [GLVerbClass(vc) for vc in vn.verb_classes]
    motion_classes = [c for c in vn_classes if c.is_motion_class()]
    print len(motion_classes)
    for c in motion_classes:
        print c.ID


if __name__ == '__main__':

    vn = VerbNetParser(max_count=50)
    vn = VerbNetParser(file_list='list-motion-classes.txt')
    vn = VerbNetParser(file_list='list-random.txt')
    vn = VerbNetParser()
    vn_classes = [GLVerbClass(vc) for vc in vn.verb_classes]

    test1(vn_classes)
    test2(vn_classes)
    test3(vn_classes)

    test_ch_of_searches(vn_classes)
    test_new_searches(vn_classes)
    test_image_searches(vn_classes)
    #test_search_by_ID(vn_classes)

    create_schema_to_verbnet_mappings(vn_classes)
