"""verbnetgl.py

This file contains the classes for the form of Verbnet that has been enhanced
with GL event and qualia structures. The classes themselves do all conversions
necessary given a VerbClass from verbnetparser.py.

To run this do the following:

1. Copy config.sample.txt into config.txt and edit it if needed by changing the
verbnet location. The file config.txt is needed so the VerbNet parser can find
the VerbNet directory.

2. Run this script in one of the following ways:

$ python verbnetgl.py

    Runs the main code in create_verbnet_gl() on all of VerbNet. Results are
    written to html/index.html.

$ python verbnetgl.py -d

    Runs the main code in create_verbnet_gl() in debug mode, that is, on just
    the first 50 verb classes. Results are written to html/index.html.

$ python verbnetgl.py -f lists/motion-classes.txt

    Runs the main code in create_verbnet_gl(), but now only on the classes
    listed in lists/motion-classes.txt. Results are written to html/index.html.

$ python verbnetgl.py -t
$ python verbnetgl.py -td

   Runs a couple of tests, either using all of VerbNet or just the first 50
   classes. You will need to hit return before each test.

The code here is designed to run on Verbnet 3.3.

"""

import os, sys, getopt

from verbnetparser import read_verbnet
from utils.ansi import BOLD, GREY, END
from utils.writer import HtmlWriter, html_var
from utils.search import search_by_predicate, search_by_argtype, search_by_ID
from utils import ansi
import utils.tests

DEBUG = True
DEBUG = False

VERBNET_VERSION = '3.3'
VERBNET_URL = 'http://verbs.colorado.edu/verb-index/vn3.3/vn/reference.php'


class VerbnetGL(object):

    """Class for enriching Verbnet with GL qualia and event structure."""

    def __init__(self, debug_mode, filelist):
        """First read Verbnet, then transform all Verbnet classes into classes
        enriched with GL notions."""
        if debug_mode:
            verb_classes = read_verbnet(max_count=50)
        elif filelist is not None:
            verb_classes = read_verbnet(file_list=filelist)
        else:
            verb_classes = read_verbnet()
        self.verb_classes = [GLVerbClass(vc) for vc in verb_classes]

    def __str__(self):
        return "<VerbnetGL classes=%s>" % len(self.verb_classes)

    def test(self):
        """Run a couple of tests."""
        utils.tests.test_print_second_class(self.verb_classes)
        utils.tests.test_print_some_classes(self.verb_classes)
        utils.tests.test_search_by_ID(self.verb_classes)
        utils.tests.test_ch_of_searches(self.verb_classes)
        utils.tests.test_new_searches(self.verb_classes, GLVerbClass)
        utils.tests.test_predicate_search(self.verb_classes)

    def write(self):
        """This is what produces the output with motion classes, possession classes,
        change of state classes and change of info classes. Only the first class is
        currently properly implemented."""
        # TODO. We have three ways of finding classes: doing a search, setting a
        # list manually, and checking a test method on the classes. Should probably
        # use only one way of doing this and for this method that should probably be
        # using the is_motion_class() method.
        motion_vcs = [vc for vc in self.verb_classes if vc.is_motion_class()]
        transfer_vcs = search_by_predicate(self.verb_classes, "transfer")
        possession_vcs = search_by_argtype(self.verb_classes, "ch_of_poss")
        ch_of_state_vcs = [vc for vc in self.verb_classes if vc.is_change_of_state_class()]
        ch_of_info_vcs = [vc for vc in self.verb_classes if vc.is_change_of_info_class()]
        writer = HtmlWriter(url=VERBNET_URL, version=VERBNET_VERSION)
        # transfer may also bring in many verbs that are not true motion verbs
        writer.write(motion_vcs + transfer_vcs, 'Motion Classes', 'motion')
        writer.write(possession_vcs, 'Change of Possession Classes', 'poss')
        writer.write(ch_of_info_vcs, 'Change of Info Classes', 'ch_of_info')
        writer.write(ch_of_state_vcs, 'Change of State Classes', 'ch_of_x')
        writer.finish()


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

    def __str__(self):
        return "<GLVerbClass \"%s\" roles=%s frames=%s subclasses=%s members=%s>" \
            % (self.ID, len(self.roles), len(self.frames), len(self.subclasses), len(self.members))

    def is_motion_class(self):
        """Return True if one of the frames is a motion frame."""
        for f in self.frames:
            if f.is_motion_frame():
                return True
        return False

    def is_change_of_state_class(self):
        """Return True if the class is a change-of-state class, which is defined as
        having an argtype that contains ch_of in one of the frames."""
        return True if [t for t in self.argtypes() if 'ch_of_' in t] else False

    def is_change_of_info_class(self):
        """Return True if the class is a change-of-info class, which is defined as
        having an argtype that contains ch_of_info in one of the frames."""
        return True if [t for t in self.argtypes() if 'ch_of_info' in t] else False

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

    def pp(self):
        print bold(str(self)), "\n"
        for frame in self.frames:
            frame.pp()
            print


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
    syn/sem variables in the subcat to those in the event structure."""

    def __init__(self, glverbclass, frame):
        self.glverbclass = glverbclass          # instance of GLVerbClass
        self.vnframe = frame                    # instance of verbnetparser.Frame
        self.class_roles = glverbclass.roles    # list of verbnetparser.ThematicRoles
        self.description = frame.description    # unicode string, primary description
        self.examples = frame.examples          # list of unicode strings
        self.syntax = frame.syntax              # list of verbnetparser.SyntacticRole
        self.subcat = Subcat(self)
        self.qualia = Qualia(self, None, None)
        self.events = EventStructure(self)
        self.add_oppositions()

    def __str__(self):
        return "<GLFrame %s [%s] '%s'>" % \
            (self.glverbclass.ID, self.description, self.examples[0])

    def find_predicates(self, pred_value):
        """Returns the list of Predicates where the value equals pred_value."""
        # TODO: should forward to self.vnframe
        return [p for p in self.vnframe.predicates if p.value == pred_value]

    def find_arguments(self, pred, arg):
        """Return all arguments in pred where arg matches one of the argument's elements
        (note that arguments are tuples of two strings, like <Event,during(E)>
        or <ThemRole,Theme>)."""
        # TODO: should be defined on Predicate
        return [a for a in pred.argtypes if arg in a]

    def is_motion_frame(self):
        """Returns True if one of the predicates is 'motion', returns False otherwise."""
        return True if self.find_predicates('motion') else False

    def add_oppositions(self):
        """Add oppositions for each frame to event and qualia structure. Note
        that this method may be pulled out and instead be put in a dedicated
        OppositionFactory class."""
        # Use an auxiliary dictionary that has mappings from role names to
        # variables, taken from the subcat frame.
        self.role2var = self.subcat.get_variables()
        # So for now we just do motion verbs, will add more, but need to decide
        # whether the groups of classes we do this for are disjoint or not.
        if self.is_motion_frame():
            self._add_motion_opposition()

    def _add_motion_opposition(self):
        """Add motion opposition to qualia and event structure of motion frames."""
        initial_location, destination = None, None
        moving_object = self._get_moving_object()
        agent = self._get_agent()
        initial_location = self._get_initial_location()
        destination = self._get_destination()
        self._add_default_opposition(initial_location, destination)
        initial_state = State(self, moving_object[1], initial_location[1])
        final_state = State(self, moving_object[1], destination[1])
        opposition = Opposition(self, 'loc', [[initial_state, final_state]])
        self.events = EventStructure(self, [[initial_state, final_state]])
        self.qualia = Qualia(self, 'motion', opposition)
        self._debug1(agent, moving_object, initial_location, destination,
                     initial_state, final_state)

    def _get_moving_object(self):
        """Get the role and the index of the moving object. Assumes that the moving
        object is always the theme."""
        # check whether there actually is a motion predicate
        if not self.find_predicates('motion'):
            print "WARNING: no Motion predicate found in", self
        return ['Theme', str(self.role2var.get('Theme', '?'))]

    def _get_agent(self):
        """Get the role and index of the agent of the movement. Assumes the
        cause is the agent."""
        # check whether there is an agent if there is a cause predicate
        cause_predicates = self.find_predicates('cause')
        if cause_predicates:
            args = self.find_arguments(cause_predicates[0], 'Agent')
            if not args:
                print 'WARNING: missing Agent in Cause predicate'
        return ['Agent', str(self.role2var.get('Agent', '?'))]

    def _get_initial_location(self):
        """For now just return the Initial_Location role and the index of it, if any. No
        checking of predicates and no bitchy messages on missing roles."""
        # TODO: we are using list of strings, should perhaps use some class, this
        # same issue holds for the three other _get_X methods.
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
        print "%s%s" % (indent * ' ', ul('predicates'))
        for p in self.vnframe.predicates:
            print "%s   %s" % (indent * ' ', p)

    def pp_subcat(self, indent=0):
        print "%s%s" % (indent * ' ', ul('subcat'))
        for sc in self.subcat:
            print "%s   %s" % (indent * ' ', sc)

    def pp_qualia(self, indent=0):
        print "%s%s" % (indent * ' ', ul('qualia'))
        print "%s   %s" % (indent * ' ', self.qualia)

    def pp_roles(self, indent=0):
        print "%s%s" % (indent * ' ', ul('roles'))
        for role in self.class_roles:
            print "%s   %s" % (indent * ' ', role)

    def pp_variables(self, indent=0):
        print "%svariables = { %s }" \
            % (indent * ' ',
               ', '.join(["%s(%s)" % (r, v) for r, v in self.role2var.items()]))

    def _debug1(self, agent, moving_object, initial_location, destination,
                initial_state, final_state):
        if not DEBUG:
            return
        if self.glverbclass.ID in ('run-51.3.2', 'slide.11.2', 'snooze-40.4', 'accompany-51.7'):
            print; self.pp(); print; self.pp_variables(3); print
            print "   | agent             =  %s" % agent
            print "   | moving_object     =  %s" % moving_object
            print "   | initial_Location  =  %s" % initial_location
            print "   | destination       =  %s" % destination
            print "   | initial_state     =  %s" % initial_state
            print "   | final_state       =  %s" % final_state, '\n'

    def pp(self, indent=0):
        name = self.glverbclass.ID + ' -- ' + self.description
        print "%s%s\n" % (indent * ' ', bold(name))
        for example in self.examples:
            print "   %s\"%s\"" % (indent * ' ', example)
        print; self.pp_roles(indent+3)
        print; self.pp_predicates(indent+3)
        print; self.pp_subcat(indent+3)
        print; self.pp_qualia(indent+3)
        print; self.events.pp(indent+3)


class Subcat(object):

    """Class that contains the GL subcategorisation for the frame, which is
    basically taken from the Verbnet frame except that it adds variables to some
    of the subcat elements."""

    def __init__(self, glframe):
        """Creates the subcat frame structure with unique variables assigned to
        different phrases/roles"""
        self.glframe = glframe
        self.members = []
        i = 0
        for synrole in self.glframe.syntax:
            if synrole.pos in ["ADV", "PREP", "ADJ"]:
                self.members.append(SubcatElement(None, synrole))
                continue
            elif synrole.pos == "VERB":
                self.members.append(SubcatElement("e", synrole))
                continue
            elif synrole.pos == "NP":
                i += 1
                var = "x%d" % i
                self.members.append(SubcatElement(var, synrole))

    def __iter__(self):
        return iter(self.members)

    def __len__(self):
        return len(self.members)

    def get_variables(self):
        """Returns a dictionary of roles and variables from all elements of the
        subcategorisation frame. The dictionary is indexed on the roles and
        variables are integers, for example {'Beneficiary': 0, 'Agent': 1}."""
        variables = {}
        for subcat_element in self:
            # skip the event and skip prepositions
            if subcat_element.var not in [None, "e"]:
                variables[subcat_element.role] = subcat_element.var
        return variables


class SubcatElement(object):

    """Stores the variable, category, role and restrictions of a subcat element.
    Note that self.role is a string, usually with one role like 'Agent', but
    also a list of prepositions like 'from out_of'."""

    def __init__(self, var, synrole, themrole=None):
        self.var = var
        self.cat = synrole.pos
        self.role = synrole.value
        self.restrictions = synrole.restrictions

    def __repr__(self):
        restrictions = ''
        if not self.restrictions.is_empty():
            restrictions = " / %s" % self.restrictions
        return "{ var = %s, cat = %s, role = %s }%s" \
            % (self.var, self.cat, self.role, restrictions)

    def html(self):
        def verb(text): return "<span class=verb>%s</span>" % text
        def role(text): return "<span class=role>%s</span>" % text
        def prep(text): return "<span class=prep>%s</span>" % text
        def cat(text): return "<span class=cat>%s</span>" % text
        if self.role is not None and self.cat in ('NP', 'PP'):
            return "%s(%s)" % (role(self.role), html_var(self.var))
        elif self.var == 'e':
            return "%s(%s)" % (verb('V'), self.var)
        elif self.role is not None:
            return "{%s}" % prep(self.role)
        elif not self.restrictions.is_empty():
            return "{%s}" % prep(self.restrictions)
        else:
            return "{%s}" % cat(self.cat)


class State(object):
    
    """Represents a state in the event structure For motion verbs, this gives the
    variable assignment of the mover, and its location. For transfer verbs, this
    gives the variable assignment of the object being transferred, and what
    currently owns the object."""

    # TODO. Should probably have several kinds of states, this one really is the
    # state of an object being at a position (or being owned). Should als make a
    # State a list of assignments rather than just the one.

    def __init__(self, glframe, obj_var, pos_var):
        self.glframe = glframe
        self.object = obj_var
        self.position = pos_var
        
    def __repr__(self):
        return "{ objects.%s.location = %s }" % (self.object, self.position)

    def html(self):
        return "{ objects.%s.location = %s }" % (html_var(self.object),
                                                 html_var(self.position))


class EventStructure(object):

    """Defines the event structure for a particular frame of a verb"""

    # TODO: adopt a list of states instead of just initial and final.

    def __init__(self, glframe, states=None):
        self.glframe = glframe
        if states is None:
            states = []
        self.var = "e"
        self.initial_state = [state1 for state1, state2 in states]
        self.final_state = [state2 for state1, state2 in states]

    def __repr__(self):
        return "{ var = %s, initial_state = %s, final_state = %s }" \
            % (self.var, self.initial_state, self.final_state)

    def pp(self, indent=0):
        print "%s%s" % (indent * ' ', ul('events'))
        print "%s   var = %s" % (indent*' ', self.var)
        print "%s   initial_state = %s" % (indent*' ', self.initial_state)
        print "%s   final_state   = %s }" % (indent*' ', self.final_state)


class Opposition(object):

    """Represents the opposition structure of the frame. Right now only tailored for
    locations. Technically, an opposition should perhaps only have two states,
    but we allow there to be a longer list."""

    # define opposition operator used give the type of change predicate
    operator_mappings = { 'loc': 'At', 'pos': 'Has', 'info': 'Knows', 'state': 'State' }

    def __init__(self, glframe, type_of_change, states):
        self.glframe = glframe
        self.type_of_change = type_of_change
        self.states = states
        
    def __repr__(self):
        op = Opposition.operator_mappings.get(self.type_of_change, 'Op')
        return ' '.join(["(%s(%s, %s), %s(%s, %s))" % \
                         (op, start.object, start.position, op, end.object, end.position)
                         for start, end in self.states])

    def html(self):
        op = Opposition.operator_mappings.get(self.type_of_change, 'Op')
        return ' '.join(["(%s(%s, %s), %s(%s, %s))" % \
                         (op, html_var(start.object), html_var(start.position),
                          op, html_var(end.object), html_var(end.position))
                         for start, end in self.states])

 
class Qualia(object):

    """Represents the qualia structure of a verbframe, including opposition
    structure."""

    def __init__(self, glframe, pred_type, opposition):
        self.glframe = glframe
        self.formal = pred_type
        self.opposition = opposition

    def __repr__(self):
        formal = "%s(e)" % self.formal if self.formal is not None else None
        opposition = '' if self.opposition is None else " AND %s" % self.opposition
        return "{ formal = %s%s }" % (formal, opposition)

    def html(self):
        formal = "%s(e)" % self.formal if self.formal is not None else None
        opposition = '' if self.opposition is None else " AND %s" % self.opposition.html()
        return "{ formal = %s%s }" % (formal, opposition)


## UTILITIES

def read_options():
    debug_mode = False
    filelist = None
    run_tests = False
    opts, arg = getopt.getopt(sys.argv[1:], 'dtf:', [])
    for opt, arg in opts:
        if opt == '-t':
            run_tests = True
        if opt == '-d':
            debug_mode = True
        if opt == '-f':
            filelist = arg
    return debug_mode, filelist, run_tests


def bold(text):
    if sys.platform in ('linux2', 'darwin'):
        text = ansi.BOLD + text + ansi.END
    return text

def ul(text):
    if sys.platform in ('linux2', 'darwin'):
        text = ansi.LINE + text + ansi.END
    return text



if __name__ == '__main__':

    debug_mode, filelist, run_tests = read_options()
    vngl = VerbnetGL(debug_mode, filelist)

    if run_tests:
        vngl.test()
    else:
        vngl.write()
