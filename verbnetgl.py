"""verbnetgl.py

This file contains the classes for the form of Verbnet that has been enhanced
with GL event and qualia structures. The classes themselves do all conversions
necessary given a VerbClass from verbnetparser.py.

To run this you first need to copy config.sample.txt into config.txt and edit it
if needed by changing the verbnet location. The file config.txt is needed so the
VerbNet parser can find the VerbNet directory.

Run this script in one of the following ways:

$ python verbnetgl.py

    Runs the main code in create_verbnet_gl() on all of VerbNet, which creates
    VerbnetGL versios of Verbnet classes. Results are written to html/index.html.

$ python verbnetgl.py -d

    Runs the main code in create_verbnet_gl() in debug mode, that is, on just
    the first 50 verb classes. Results are written to html/index.html.

$ python verbnetgl.py -f lists/motion-classes.txt

    Runs the main code in create_verbnet_gl(), but now only on the classes
    listed in lists/motion-classes.txt. Results are written to html/index.html.

$ python verbnetgl.py -c give-13.1

    Runs the main code in create_verbnet_gl(), but now only on the one class
    given as an argument. Results are written to html/index.html.

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
from utils.formula import Pred, At, Has, Holds, Not, Var
from utils import ansi
import utils.tests

DEBUG = True
DEBUG = False

VERBNET_VERSION = '3.3'
VERBNET_URL = 'http://verbs.colorado.edu/verb-index/vn3.3/vn/reference.php'


class VerbnetGL(object):

    """Class for enriching Verbnet with GL qualia and event structure."""

    def __init__(self, debug_mode, filelist, vnclass):
        """First read Verbnet, then transform all Verbnet classes into classes
        enriched with GL notions."""
        if debug_mode:
            verb_classes = read_verbnet(max_count=50)
        elif filelist is not None:
            verb_classes = read_verbnet(file_list=filelist)
        elif vnclass is not None:
            verb_classes = read_verbnet(vnclass=vnclass)
        else:
            verb_classes = read_verbnet()
        self.verb_classes = [GLVerbClass(vc) for vc in verb_classes]

    def __str__(self):
        return "<VerbnetGL classes=%s>" % len(self.verb_classes)

    def get_motion_classes(self):
        return [vc for vc in self.verb_classes if vc.is_motion_class()]

    def get_ch_of_poss_classes(self):
        return [vc for vc in self.verb_classes if vc.is_ch_of_poss_class()]

    def get_tr_of_info_classes(self):
        return [vc for vc in self.verb_classes if vc.is_tr_of_info_class()]

    def get_ch_of_state_classes(self):
        return [vc for vc in self.verb_classes if vc.is_ch_of_state_class()]

    def test(self):
        """Run the informal tests from the test module."""
        utils.tests.test_all(self.verb_classes, GLVerbClass)

    def write(self):
        """This is what produces the output with motion classes, possession classes,
        change of state classes and change of info classes."""
        motion_vcs = self.get_motion_classes()
        ch_of_poss_vcs = self.get_ch_of_poss_classes()
        tr_of_info_vcs = self.get_tr_of_info_classes()
        ch_of_state_vcs = self.get_ch_of_state_classes()
        writer = HtmlWriter(url=VERBNET_URL, version=VERBNET_VERSION)
        writer.write(motion_vcs, 'Motion', 'motion')
        writer.write(ch_of_poss_vcs, 'Change of Possession', 'ch_of_poss')
        writer.write(tr_of_info_vcs, 'Change of Info', 'ch_of_info')
        writer.write(ch_of_state_vcs, 'Change of State', 'ch_of_state')
        writer.finish()

    def print_class_roles(self):
        for vc in self.verb_classes:
            print "%-30s\t%s" % (vc.ID, ' '.join([r.role_type for r in vc.roles]))


class GLVerbClass(object):

    """VerbClass analogue, with an update mostly to frames"""

    def __init__(self, verbclass):
        self.verbclass = verbclass
        self.ID = verbclass.ID
        self.members = verbclass.members
        self.names = verbclass.names
        self.roles = verbclass.themroles
        self.frames = self.frames()
        self.subclasses = [GLSubclass(sub, self.roles)
                           for sub in verbclass.subclasses]

    def __str__(self):
        return "<GLVerbClass \"%s\" roles=%s frames=%s subclasses=%s members=%s>" \
            % (self.ID, len(self.roles), len(self.frames),
               len(self.subclasses), len(self.members))

    def is_motion_class(self):
        """Return True if one of the frames is a motion frame."""
        return len([f for f in self.frames if f.is_motion_frame()]) > 0

    def is_ch_of_poss_class(self):
        """Return True if one of the frames is a ch_of_poss frame."""
        return len([f for f in self.frames
                    if f.is_ch_of_poss_frame()]) > 0

    def is_tr_of_info_class(self):
        """Return True if one of the frames is a tr_of_info frame."""
        return len([f for f in self.frames
                    if f.is_tr_of_info_frame()]) > 0

    def is_ch_of_state_class(self):
        """Return True if one of the frames is a ch_of_state frame."""
        return len([f for f in self.frames
                    if f.is_ch_of_state_frame()]) > 0

    def has_roles(self, role_types):
        """Returns True if the role_types are all in the roles on the verb class,
        returns False otherwise."""
        class_roles = [r.role_type for r in self.roles]
        return set(role_types) <= set(class_roles)

    def frames(self):
        return [GLFrame(self, frame) for frame in self.verbclass.frames]

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
        self.subclasses = [GLSubclass(sub, self.roles)
                           for sub in verbclass.subclasses]

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

    """GL enhanced VN frame that adds qualia and event structure, and links syn/sem
    variables in the subcat to those in the event structure. Some parts of the
    GLFrame are copied straight from the Frame it is created from, others are
    adjusted somewhat (subcat) or built from scratch (qualia, events)."""

    def __init__(self, glverbclass, frame):
        self.glverbclass = glverbclass          # instance of GLVerbClass
        self.vnframe = frame                    # instance of verbnetparser.Frame
        self.class_roles = glverbclass.roles    # list of verbnetparser.ThematicRoles
        self.description = frame.description    # unicode string, primary description
        self.examples = frame.examples          # list of unicode strings
        self.predicates = frame.predicates      # list of verbnetparser.Predicate
        self.syntax = frame.syntax              # list of verbnetparser.SyntacticRole
        self.subcat = Subcat(self)
        self.qualia = Qualia(self)
        self.events = EventStructure(self)
        self.add_oppositions()

    def __str__(self):
        return "<GLFrame %s [%s] '%s'>" % \
            (self.glverbclass.ID, self.description, self.examples[0])

    def find_predicates(self, pred_value):
        """Returns the list of Predicates where the value equals pred_value."""
        return [p for p in self.predicates if p.value == pred_value]

    def find_predicates_with_argval(self, argvalue):
        """Returns all those predicates that have an argument value equal to
        argvalue. Note that arguments are pairs like <Event,during(E)> or
        <ThemRole,Theme>. Does not just return the predicate but a pair of
        predicate and argument which means that in some cases the same predicate
        could be returned more than once, but with different arguments."""
        answer = []
        for pred in self.predicates:
            for argument in pred.args:
                if argument[1] == argvalue:
                    answer.append([pred, argument])
        return answer

    def is_motion_frame(self):
        """Returns True if one of the predicates' value is 'motion', returns False
        otherwise."""
        return True if self.find_predicates('motion') else False

    def is_ch_of_poss_frame(self):
        """Returns True if one of the predicates has a 'ch_of_poss' argument value,
        returns False otherwise."""
        return True if self.find_predicates_with_argval('ch_of_poss') else False

    def is_tr_of_info_frame(self):
        """Returns True if one of the predicates has a 'tr_of_info' argument value,
        returns False otherwise."""
        return True if self.find_predicates_with_argval('tr_of_info') else False

    def is_ch_of_state_frame(self):
        """Returns True if one of the predicates has a 'ch_of_state' argument value,
        returns False otherwise."""
        return True if self.find_predicates_with_argval('ch_of_state') else False

    def add_oppositions(self):
        """Add oppositions for each frame to event and qualia structure."""
        # Use an auxiliary dictionary that has mappings from role names to
        # variables, taken from the subcat frame.
        self.role2var = self.subcat.get_variables()
        # We restart numbering variables for each frame.
        Var.reset_unbound_variable_count()
        # TODO: need to decide whether the groups of classes we do this for are
        # disjoint or not.
        if self.is_motion_frame():
            GLMotionFactory(self).make()
        if self.is_ch_of_poss_frame():
            GLChangeOfPossessionFactory(self).make()

    def get_role(self, rolename):
        """Returns a pair of the role and the variable associated with it, use
        an anonymous variable if the role is not expressed in the subcat."""
        var = self.role2var.get(rolename)
        if var is None:
            var = Var.get_unbound_variable()
        return [rolename, var]

    def _get_moving_object(self):
        """The moving object is expressed by the Theme role."""
        return self.get_role('Theme')

    def _get_initial_location(self):
        """The initial location is expressed by the Initial_Location role."""
        return self.get_role('Initial_Location')

    def _get_destination(self):
        """The destination is expressed by the Destination role."""
        return self.get_role('Destination')

    def pp_predicates(self, indent=0):
        print "%s%s" % (indent * ' ', ul('predicates'))
        for p in self.vnframe.predicates:
            print "%s   %s" % (indent * ' ', p)

    def pp_subcat(self, indent=0):
        print "%s%s" % (indent * ' ', ul('subcat'))
        for sc in self.subcat:
            print "%s   %s" % (indent * ' ', sc)

    def pp_qualia(self, indent=0):
        print "%s%s" % (indent * ' ', ul('qualia-structure'))
        print "%s   %s" % (indent * ' ', self.qualia)

    def pp_roles(self, indent=0):
        print "%s%s" % (indent * ' ', ul('roles'))
        for role in self.class_roles:
            print "%s   %s" % (indent * ' ', role)

    def pp_variables(self, indent=0):
        print "%svariables = { %s }" \
            % (indent * ' ',
               ', '.join(["%s(%s)" % (r, v) for r, v in self.role2var.items()]))

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
        def add_class(text, classname):
            return "<span class=%s>%s</span>" % (classname, text)
        if self.role is not None and self.cat in ('NP', 'PP'):
            return "%s(%s)" % (add_class(self.role, 'role'), html_var(self.var))
        elif self.var == 'e':
            return "%s(%s)" % (add_class('V', 'verb'), self.var)
        elif self.role is not None:
            return "{%s}" % add_class(self.role, 'prep')
        elif not self.restrictions.is_empty():
            return "{%s}" % add_class(self.restrictions, 'prep')
        else:
            return "{%s}" % add_class(self.cat, 'cat')


class State(object):

    """Represents a state in the event structure where a state is nothing more or
    less than a list of predicates."""

    def __init__(self, glframe, formulas):
        self.glframe = glframe
        self.formulas = formulas

    def __str__(self):
        return "[ %s ]" % ', '.join([str(f) for f in self.formulas])

    def html(self):
        return "[ %s ]" % ', '.join([f.html() for f in self.formulas])


class EventStructure(object):

    """Defines the event structure for a particular frame of a verb"""

    def __init__(self, glframe, var='e', states=None, formulas=None):
        # TODO: for now we keep two ways of doing this, one with initial and
        # final states and one with a list of formulas, probably remove the
        # first (requires updating __str__() and pp() as well as removing
        # initial_state() and final_state())
        self.glframe = glframe
        self.var = var
        self.states = [] if states is None else states
        self.formulas = [] if formulas is None else formulas
        if not self.states and not self.formulas:
            self.formulas = [Pred('event', [Var('e')])]

    def __str__(self):
        return "{ var = %s, initial_state = %s, final_state = %s }" \
            % (self.var, self.initial_state, self.final_state)

    def initial_state(self):
        try:
            return self.states[0]
        except IndexError:
            return State(None, [])

    def final_state(self):
        try:
            return self.states[-1]
        except IndexError:
            return State(None, [])

    def pp(self, indent=0):
        print "%s%s" % (indent * ' ', ul('event-structure'))
        print "%s   var = %s" % (indent*' ', self.var)
        print "%s   initial_state = %s" % (indent*' ', self.initial_state())
        print "%s   final_state   = %s }" % (indent*' ', self.final_state())

    def html(self):
        return ', '.join([f.html() for f in self.formulas])


class Qualia(object):

    """Represents the verbframe's qualia structure, which is a list of formulas
    (actually, it is a list of predicates and oppositions, the latter technically
    not being a formula)."""

    def __init__(self, glframe, formulas=None):
        self.glframe = glframe
        self.formulas = formulas
        if formulas is None:
            verb = self.glframe.glverbclass.ID.split('-')[0]
            self.formulas = [Pred(verb, [Var('e')])]

    def __str__(self):
        return "%s" % ' & '.join([str(f) for f in self.formulas])

    def add(self, formulas):
        """Add formulas to the qualia."""
        self.formulas.extend(formulas)

    def html(self):
        return "%s" % ' & '.join([f.html() for f in self.formulas])


class GLFactory(object):

    """Subclasses of GLFactory take a GLFrame and then add qualia and event
    structure to it."""

    @classmethod
    def determine_cases(cls, glframe):
        # TODO: it is a bit redundant that this is done for each frame while the
        # roles are on the verbclass, refactor this.
        cases = []
        for role_types in cls.cases:
            if glframe.glverbclass.has_roles(role_types):
                cases.append(role_types)
        return cases

    def __init__(self, glframe):
        self.glframe = glframe

    def frame_description(self):
        return "%s [%s] '%s'" % (self.glframe.glverbclass.ID,
                                 self.glframe.description,
                                 self.glframe.examples[0])

    def pp_cases(self, cases):
        print "\n%s\n" % self.frame_description()
        for c in cases:
            print '  ', '-'.join([str(r) for r in c])

    def debug(self, roles):
        if not DEBUG:
            return
        print; self.glframe.pp(); print; self.glframe.pp_variables(3); print
        for role in roles:
            print "   | %-16s  =  %s" % (role[0], role[1])


class GLMotionFactory(GLFactory):

    """Add motion oppositions and other motion predicates to the qualia and event
    structure. Preliminary version that deals with only one basic case."""

    cases = [
        ('Theme', 'Initial_Location', 'Destination'),
        ('Theme', 'Destination'),
        ('Agent', 'Theme', 'Trajectory'),
        ('Agent', 'Theme', 'Location'),
        ('Theme', 'Source', 'Goal'),
        ('Theme', 'Goal'),
        ('Agent', 'Location'),
    ]

    def make(self):
        cases = self.__class__.determine_cases(self.glframe)
        # self.pp_cases()
        if not cases:
            print "WARNING: no case for", self.frame_description()
        elif cases[0] == ('Theme', 'Initial_Location', 'Destination'):
            self.harvest_obj_source_destination()
        elif cases[0] == ('Theme', 'Destination'):
            self.harvest_obj_source_destination()
        elif cases[0] == ('Agent', 'Theme', 'Trajectory'):
            pass
        elif cases[0] == ('Theme', 'Source', 'Goal'):
            pass
        elif cases[0] == ('Agent', 'Theme', 'Location'):
            pass
        elif cases[0] == ('Theme', 'Goal'):
            pass

    def harvest_obj_source_destination(self):
        moving_object = self.glframe._get_moving_object()
        initial_location = self.glframe._get_initial_location()
        destination = self.glframe._get_destination()
        motion = Pred('motion', [Var('e')])
        at1 = At(Var(moving_object[1]), Var(initial_location[1]))
        at2 = At(Var(moving_object[1]), Var(destination[1]))
        self.glframe.qualia.add([motion,
                         Opposition(at1, Not(at1)),
                         Opposition(Not(at2), at2)])
        event = Pred('event', [Var('e')])
        istate = Pred('initial_state', [Var('e'), Var('e1')])
        fstate = Pred('final_state', [Var('e'), Var('e2')])
        holds1 = Holds(Var('e1'), at1)
        holds2 = Holds(Var('e2'), at2)
        self.glframe.events = EventStructure(self, 'e',
                                     states=[State(self, [holds1]), State(self, [holds2])],
                                     formulas=[event, istate, holds1, fstate, holds2])
        self.debug([('moving_object', moving_object),
                    ('initial_location', initial_location),
                    ('destination', destination)])


class GLChangeOfPossessionFactory(GLFactory):

    """Add possession oppositions and other possession predicates to the qualia and event
    structure. Even more preliminary than GLMotionFactory."""

    cases = [
        ('Agent', 'Recipient', 'Theme'),
    ]

    def make(self):
        cases = self.__class__.determine_cases(self.glframe)
        # self.pp_cases()
        if not cases:
            print "WARNING: no case for", self.frame_description()
        elif cases[0] == ('Agent', 'Recipient', 'Theme'):
            self.harvest_agent_recipient_theme()

    def harvest_agent_recipient_theme(self):
        owner1 = self.glframe.get_role('Agent')
        owner2 = self.glframe.get_role('Recipient')
        thing = self.glframe.get_role('Theme')
        transfer = Pred('transfer', [Var('e')])
        has1 = Has(Var(owner1[1]), Var(thing[1]))
        has2 = Has(Var(owner2[1]), Var(thing[1]))
        self.glframe.qualia.add([transfer, has1, Not(has1), has2, Not(has2)])
        event = Pred('event', [Var('e')])
        istate = Pred('initial_state', [Var('e'), Var('e1')])
        fstate = Pred('final_state', [Var('e'), Var('e2')])
        holds1 = Holds(Var('e1'), has1)
        holds2 = Holds(Var('e2'), has2)
        self.glframe.events = EventStructure(self, 'e',
                                     states=[State(self, [holds1]), State(self, [holds2])],
                                     formulas=[event, istate, holds1, fstate, holds2])
        self.debug([('thing',thing), ('original_owner', owner1), ('new_owner', owner2)])


class Opposition(object):

    """An opposition is simply a pair of two predicates where one is the negation
    of the other. The first element of the pair is required to be indexed to an
    earlier time than the second."""

    def __init__(self, pred1, pred2):
        self.pred1 = pred1
        self.pred2 = pred2

    def __str__(self):
        return "Opposition(%s, %s)" % (self.pred1, self.pred2)

    def html(self):
        return "<nobr><span class=opposition>Opposition</span>(%s, %s)</nobr>" \
            % (self.pred1.html(), self.pred2.html())


# UTILITIES

def read_options():
    debug_mode = False
    filelist = None
    vnclass = None
    run_tests = False
    opts, arg = getopt.getopt(sys.argv[1:], 'dtf:c:', [])
    for opt, arg in opts:
        if opt == '-t':
            run_tests = True
        if opt == '-d':
            debug_mode = True
        if opt == '-f':
            filelist = arg
        if opt == '-c':
            vnclass = arg
    return debug_mode, filelist, vnclass, run_tests


def bold(text):
    if sys.platform in ('linux2', 'darwin'):
        text = ansi.BOLD + text + ansi.END
    return text


def ul(text):
    if sys.platform in ('linux2', 'darwin'):
        text = ansi.LINE + text + ansi.END
    return text


if __name__ == '__main__':

    debug_mode, filelist, vnclass, run_tests = read_options()
    vngl = VerbnetGL(debug_mode, filelist, vnclass)

    if run_tests:
        vngl.test()
    else:
        vngl.write()

    vngl.print_class_roles()
