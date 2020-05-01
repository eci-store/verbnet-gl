"""verbnetgl.py

This file contains the classes for the form of Verbnet that has been enhanced
with GL event and qualia structures. The classes themselves do all conversions
necessary given a VerbClass from verbnetparser.py.

To run this you first need to copy config.sample.py into config.py and edit it
if needed by changing the verbnet location. The file config.py is needed so the
VerbNet parser can find the VerbNet directory.

Run this script in one of the following ways:

$ python verbnetgl.py

    Runs the main code on all of VerbNet, which creates VerbnetGL versions of
    Verbnet classes. Results are written to html/index.html.

$ python verbnetgl.py -d

    Runs the main code in debug mode, that is, on just the first 50 verb
    classes. Results are written to html/index.html.

$ python verbnetgl.py -f lists/motion-classes.txt

    Runs the main code, but now only on the classes listed in
    lists/motion-classes.txt. Results are written to html/index.html.

$ python verbnetgl.py -c give-13.1

    Runs the main code, but now only on the one class given as an
    argument. Results are written to html/index.html.

$ python verbnetgl.py -t
$ python verbnetgl.py -td

   Runs a couple of tests, either using all of VerbNet or just the first 50
   classes. You will need to hit return before each test.

The code here is designed to run on Verbnet 3.3.

"""

import os, sys, getopt

from verbnetparser import read_verbnet
from utils.ansi import BOLD, GREY, END
from utils.writer import HtmlWriter
from utils.formula import Pred, At, Have, Holds, Not, Var
from utils import ansi
import utils.tests


VERBNET_VERSION = '3.3'
VERBNET_URL = 'http://verbs.colorado.edu/verb-index/vn3.3/vn/reference.php'

# Dictionary of roles and their abbreviations
ROLES = { 'Agent': 'Ag',
          'Co-Agent': 'CAg',
          'Patient': 'Pt',
          'Co-Patient': 'CPt',
          'Theme': 'Th',
          'Co-Theme': 'CTh',
          'Initial_Location': 'InL',
          'Destination': 'Dest',
          'Trajectory': 'Traj',
          'Location': 'Loc',
          'Result': 'Res',
          'Source': 'Src',
          'Goal': 'Goal',
          'Asset': 'As',
          'Recipient': 'Rec',
          'Beneficiary': 'Ben',
          'Instrument': 'Instr',
          'Experiencer': 'Exp',
          'Material': 'Mat',
          'Product': 'Prod',
          'Attribute': 'Attr',
          'Stimulus': 'Stim',
          'Path': 'Path',
          'Topic': 'Topic' }


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
            print("%-30s\t%s" % (vc.ID, ' '.join([r.role_type for r in vc.roles])))


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

    def __lt__(self, other):
        return self.ID < other.ID

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
        print(bold(str(self)), "\n")
        for frame in self.frames:
            frame.pp()
            print()


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
        # For each frame, we restart unbound variable numbering.
        Var.reset_unbound_variable_count()
        # TODO: need to decide whether the groups of frames we do this for are
        # disjoint or not, for now we assume they are.
        if self.is_motion_frame():
            GLMotionFactory(self).make()
        elif self.is_ch_of_poss_frame():
            GLChangeOfPossessionFactory(self).make()

    def get_moving_objects(self):
        """Return the moving objects as Role instances. The object role typically
        is Agent or Theme. This searches all the motion predicates, finds the
        thematic roles and connects them to variables in the subcat."""
        predicates = self.find_predicates('motion')
        # motion predicates look like "motion(during(E), Agent)"
        # TODO: get rid of the last index, use class with type and value vars
        role_names = [p.args[1][1] for p in predicates]
        return [self.get_role(r) for r in role_names]

    def get_locations(self):
        predicates = self.find_predicates('location')
        # locations have three args: "location(E, Agent, Location)"
        role_names = [(p.args[1][1], p.args[2][1]) for p in predicates]
        #print role_names
        return [(self.get_role(r1), self.get_role(r2)) for r1, r2 in role_names]

    def get_initial_location(self):
        return self.get_role('Initial_Location')

    def get_destination(self):
        return self.get_role('Destination')

    def get_trajectory(self):
        return self.get_role('Trajectory')

    def get_source(self):
        return self.get_role('Source')

    def get_goal(self):
        return self.get_role('Goal')

    def get_role(self, rolename):
        """Returns a Role object of the role and the variable associated with
        it, uses an anonymous variable if the role is not expressed in the
        subcat."""
        var = self.role2var.get(rolename)
        if var is None:
            var = Var.get_unbound_variable()
        return Role(rolename, var)

    def pp_predicates(self, indent=0):
        print("%s%s" % (indent * ' ', ul('predicates')))
        for p in self.vnframe.predicates:
            print("%s   %s" % (indent * ' ', p))

    def pp_subcat(self, indent=0):
        print("%s%s" % (indent * ' ', ul('subcat')))
        for sc in self.subcat:
            print("%s   %s" % (indent * ' ', sc))

    def pp_qualia(self, indent=0):
        print("%s%s" % (indent * ' ', ul('qualia-structure')))
        print("%s   %s" % (indent * ' ', self.qualia))

    def pp_roles(self, indent=0):
        print("%s%s" % (indent * ' ', ul('roles')))
        for role in self.class_roles:
            print("%s   %s" % (indent * ' ', role))

    def pp_variables(self, indent=0):
        print("%svariables = { %s }" \
            % (indent * ' ',
               ', '.join(["%s(%s)" % (r, v) for r, v in list(self.role2var.items())])))

    def pp(self, indent=0):
        name = self.glverbclass.ID + ' -- ' + self.description
        print("%s%s\n" % (indent * ' ', bold(name)))
        for example in self.examples:
            print("   %s\"%s\"" % (indent * ' ', example))
        print(); self.pp_roles(indent+3)
        print(); self.pp_predicates(indent+3)
        print(); self.pp_subcat(indent+3)
        print(); self.pp_qualia(indent+3)
        print(); self.events.pp(indent+3)


class Subcat(object):

    """Class that contains the GL subcategorisation for the frame, which is
    basically taken from the Verbnet frame except that it adds variables to some
    of the subcat elements."""

    def __init__(self, glframe):
        """Creates the subcat frame structure with unique variables assigned to
        different phrases/roles"""
        self.glframe = glframe
        self.members = []
        for synrole in self.glframe.syntax:
            if synrole.pos in ["ADV", "PREP", "ADJ"]:
                self.members.append(SubcatElement(None, synrole))
                continue
            elif synrole.pos == "VERB":
                self.members.append(SubcatElement("e", synrole))
                continue
            elif synrole.pos == "NP":
                # use the abrreviation of the role as the variable name
                var = ROLES.get(synrole.value, synrole.value)
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
            if self.var is not None:
                return "%s(%s)" % (add_class(self.role, 'role'), Var(self.var).html())
            else:
                print("WARNING: unexpected subcat ", self)
        elif self.var == 'e':
            return "%s(%s)" % (add_class('V', 'verb'), self.var)
        elif self.role is not None:
            return "{%s}" % add_class(self.role, 'prep')
        elif not self.restrictions.is_empty():
            return "{%s}" % add_class(self.restrictions, 'prep')
        else:
            return "{%s}" % add_class(self.cat, 'cat')


class EventStructure(object):

    """Defines the event structure for a particular frame of a verb class."""

    def __init__(self, glframe, var='e', formulas=None):
        self.glframe = glframe
        self.var = var
        self.formulas = [] if formulas is None else formulas
        if not self.formulas:
            self.formulas = [Pred('event', [Var(var)])]

    def __str__(self):
        return ', '.join([str(f) for f in self.formulas])

    def add(self, formula):
        self.formulas.append(formula)

    def add_multiple(self, formulas):
        self.formulas.extend(formulas)

    def pp(self, indent=0):
        print("%s%s" % (indent * ' ', ul('event-structure')))
        print("%s   var = %s" % (indent*' ', self.var))
        print("%s   %s" % (indent*' ', self))

    def html(self):
        return '<br>\n'.join([f.html() for f in self.formulas])


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

    def add(self, formula):
        """Add a formula to the qualia."""
        self.formulas.append(formula)

    def add_multiple(self, formulas):
        """Add multiple formulas to the qualia."""
        self.formulas.extend(formulas)

    def html(self):
        return "%s" % '<br>\n'.join([f.html() for f in self.formulas])


class Role(object):

    """A Role is nothing but a thematic role associated with a variable. Mostly
    for clarity so we do not deal with things like ['Theme', 'x1'] and access
    indices, but instead have Role('Theme', 'x1') with the ability to access
    instance variables."""

    def __init__(self, rolename, var):
        self.role = rolename
        self.var = var

    def __str__(self):
        return "%s(%s)" % (self.role, self.var)


class GLFactory(object):

    """Subclasses of GLFactory take a GLFrame and then add qualia and event
    structure to it."""

    @classmethod
    def determine_case(cls, glframe):
        """Determine which of the cases in the cases class variable applies for this
        frame. The first one that matches is returned."""
        # TODO: it is a bit redundant that this is done for each frame while the
        # roles are on the verbclass, refactor this.
        cases = []
        for role_types in cls.cases:
            if glframe.glverbclass.has_roles(role_types):
                return role_types
        return None

    def __init__(self, glframe):
        self.glframe = glframe

    def frame_ID(self):
        return "%s - %s" % (self.glframe.glverbclass.ID,
                            self.glframe.description)

    def frame_description(self):
        return "%s [%s] '%s'" % (self.glframe.glverbclass.ID,
                                 self.glframe.description,
                                 self.glframe.examples[0])

    def pp_cases(self, cases):
        print("\n%s\n" % self.frame_description())
        for c in cases:
            print('  ', '-'.join([str(r) for r in c]))

    def debug(self, roles):
        print("\n%s -- %s\n" % (self.glframe.glverbclass.ID,
                                self.glframe.description))
        self.glframe.pp_variables(3); print()
        for role in roles:
            print("   | %s" % role)


class GLMotionFactory(GLFactory):

    """Add motion oppositions and other motion predicates to the qualia and
    event structure."""

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
        case = self.__class__.determine_case(self.glframe)
        if case is None:
            print("WARNING: no case for", self.frame_description())
        elif case in [('Agent', 'Theme', 'Location'),
                      ('Agent', 'Location')]:
            self.harvest_location()
        elif case in [('Theme', 'Initial_Location', 'Destination'),
                      ('Agent', 'Theme', 'Trajectory'),
                      ('Theme', 'Destination')]:
            self.harvest_obj_source_destination()
        elif case in [('Theme', 'Source', 'Goal'),
                      ('Theme', 'Goal')]:
            self.harvest_obj_source_goal()
        else:
            print("WARNING: no code to deal with this case")
            print("     case  - %s" % (case,))
            print("     frame - %s" % self.frame_ID())

    def harvest_location(self):
        """Deals with the verb classes that have a Location, which are all cases
        of in-place motion. So we simply just add the location if we find it but
        no oppositions."""
        locations = self.glframe.get_locations()
        for location in locations:
            obj = location[0]
            loc = location[1]
            at = At(Var(obj.var), Var(loc.var))
            self.glframe.qualia.add(at)
            self.glframe.events.add(Holds(Var(self.glframe.events.var), at))

    def harvest_obj_source_destination(self):
        """Deals with the regualr case, where initial loacation and desctination
        roles may be expressed."""
        # TODO: add the instrument (adding it to moving objects, but not by
        # changing get_moving_objects())
        moving_objects = self.glframe.get_moving_objects()
        initial_location = self.glframe.get_initial_location()
        destination = self.glframe.get_destination()
        trajectory = self.glframe.get_trajectory()
        trajectory_roles = [trajectory, initial_location, destination]
        qualia = self.glframe.qualia
        events = self.glframe.events
        qualia.add( Pred('motion', [Var('e')]) )
        qualia.add( Pred('trajectory', [Var(r.var) for r in trajectory_roles]) )
        event_var = self.glframe.events.var
        events.add( Pred('initial_state', [Var(event_var), Var('e1')]) )
        events.add( Pred('final_state', [Var(event_var), Var('e2')]) )
        for obj in moving_objects:
            at1 = At(Var(obj.var), Var(initial_location.var))
            at2 = At(Var(obj.var), Var(destination.var))
            path_var = Var(Var.get_unbound_variable())
            qualia.add( Opposition(at1, Not(at1)) )
            qualia.add( Opposition(Not(at2), at2) )
            qualia.add( Pred('path', [path_var, Var(obj.var), Var(trajectory.var)]) )
            events.add( Holds(Var('e1'), at1) )
            events.add( Holds(Var('e2'), at2) )

    def harvest_obj_source_goal(self):
        """Deals with verb classes that have Source and Goal roles instead of
        Initial_Location and Destination. Probably does not require a separate
        case and can be merged with the above method, but for now we keep them
        separate. Not also that in Verbnet 3.3 some goals in motion verbs are
        not spatial, this code screws up on those."""
        moving_objects = self.glframe.get_moving_objects()
        source = self.glframe.get_source()
        goal = self.glframe.get_goal()
        trajectory = self.glframe.get_trajectory()
        trajectory_roles = [trajectory, source, goal]
        qualia = self.glframe.qualia
        events = self.glframe.events
        qualia.add( Pred('motion', [Var('e')]) )
        qualia.add( Pred('trajectory', [Var(r.var) for r in trajectory_roles]) )
        event_var = self.glframe.events.var
        events.add( Pred('initial_state', [Var(event_var), Var('e1')]) )
        events.add( Pred('final_state', [Var(event_var), Var('e2')]) )
        for obj in moving_objects:
            at1 = At(Var(obj.var), Var(source.var))
            at2 = At(Var(obj.var), Var(goal.var))
            path_var = Var(Var.get_unbound_variable())
            qualia.add( Opposition(at1, Not(at1)) )
            qualia.add( Opposition(Not(at2), at2) )
            qualia.add( Pred('path', [path_var, Var(obj.var), Var(trajectory.var)]) )
            events.add( Holds(Var('e1'), at1) )
            events.add( Holds(Var('e2'), at2) )                 


class GLChangeOfPossessionFactory(GLFactory):

    """Add possession oppositions and other possession predicates to the qualia
    and event structure."""

    # TODO: only deals with the most basic case at this point

    cases = [
        ('Agent', 'Recipient', 'Theme'),
    ]

    def make(self):
        case = self.__class__.determine_case(self.glframe)
        # self.pp_cases()
        if case is None:
            pass
            # print "WARNING: no case for", self.frame_description()
        elif case == ('Agent', 'Recipient', 'Theme'):
            # print self.frame_description()
            self.harvest_agent_recipient_theme()

    def harvest_agent_recipient_theme(self):
        owner1 = self.glframe.get_role('Agent')
        owner2 = self.glframe.get_role('Recipient')
        thing = self.glframe.get_role('Theme')
        transfer = Pred('transfer', [Var('e')])
        has1 = Have(Var(owner1.var), Var(thing.var))
        has2 = Have(Var(owner2.var), Var(thing.var))
        qualia = self.glframe.qualia
        events = self.glframe.events
        qualia.add(transfer)
        qualia.add(Opposition(has1, Not(has1)))
        qualia.add(Opposition(Not(has2), has2))
        event_var = self.glframe.events.var
        events.add( Pred('initial_state', [Var(event_var), Var('e1')]) )
        events.add( Pred('final_state', [Var(event_var), Var('e2')]) )
        events.add( Holds(Var('e1'), has1) )
        events.add( Holds(Var('e2'), has2) )


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
        def tag(text): return "<span class=opposition>%s</span>" % text
        return "<nobr>%s(%s, %s)</nobr>" \
            % (tag('Opposition'), self.pred1.html(), self.pred2.html())


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

    #vngl.print_class_roles()
