"""verbnet.py

This program takes in VerbNet XML files and creates several classes for easy
access to the data.

"""

import os
import bs4

from config import VERBNET_PATH


class VerbNet(object):

    def __init__(self, limit=None, file_list=None):
        """Parse verbnet files and create instances of VerbClass. Read all verbnet
        files, but restrict the number of files to read if limit is not None, or
        read filenames from a file if file_list is given."""
        if file_list is None:
            fnames = [f for f in os.listdir(VERBNET_PATH) if f.endswith(".xml")]
            if limit is not None:
                fnames = fnames[:limit]
        else:
            fnames = ["%s.xml" % f.strip() for f in open(file_list).read().split()]
        fnames = [os.path.join(VERBNET_PATH, fname) for fname in fnames]
        self.classes = []
        self.classes_idx = {}
        for fname in fnames:
            vc = VerbClass(fname)
            self.classes.append(vc)
            self.classes_idx[vc.ID] = vc
        count = len(self.classes)
        print("Loaded %s class%s" % (count, '' if count == 1 else 'es'))


class VerbClass(object):

    """Represents a verb class or subclass from VerbNet. This could be created from
    a Verbnet XML file in which case there may be a list of subclasses included or
    it could represent a subclass from one of the files."""

    def __init__(self, fname, soup=None):
        """Initialize a VerbClass from either a Verbnet XML file or a soup object that
        represents a subclass."""
        self.fname = fname
        self.soup = soup
        if soup is None:
            self.soup = bs4.BeautifulSoup(open(fname), "lxml-xml").VNCLASS
        self.ID = self.soup.get("ID")
        self.name = self.soup.name
        self._initialize_members()
        self._initialize_frames()
        self._initialize_roles()
        self._initialize_subclasses()

    def __str__(self):
        return "<VerbClass \"%s\" roles=%s frames=%s subclasses=%s members=%s>" \
            % (self.ID, len(self.roles), len(self.frames),
               len(self.subclasses), len(self.members))

    def _initialize_members(self):
        """Get all members of a verb class"""
        self.members = [Member(mem_soup)
                        for mem_soup in self.soup.MEMBERS.find_all("MEMBER")]
        self.member_names = [mem.name for mem in self.members]

    def _initialize_frames(self):
        """Get all frames for a verb class, seems to be shared by all members
        of the class."""
        self.frames = [Frame(frame_soup, self, self.ID)
                       for frame_soup in self.soup.FRAMES.find_all("FRAME")]

    def _initialize_roles(self):
        """Get all the thematic roles for a verb class and their selectional
        restrictions."""
        self.roles = [ThematicRole(them_soup)
                      for them_soup in self.soup.THEMROLES.find_all("THEMROLE")]

    def _initialize_subclasses(self):
        """Create a VerbClass instance for every subclass listed."""
        subs = self.soup.SUBCLASSES.find_all("VNSUBCLASS", recursive=False)
        self.subclasses = [VerbClass(self.fname, soup=sub) for sub in subs]

    def is_motion(self):
        """Return True if one of the frames is a motion frame."""
        return len([f for f in self.frames if f.is_motion()]) > 0

    def is_change_of_possession(self):
        """Return True if one of the frames is a ch_of_poss frame."""
        return len([f for f in self.frames if f.is_change_of_possession()]) > 0

    def is_transfer_of_info(self):
        """Return True if one of the frames is a tr_of_info frame."""
        return len([f for f in self.frames if f.is_transfer_of_info()]) > 0

    def is_change_of_state(self):
        """Return True if one of the frames is a ch_of_state frame."""
        return len([f for f in self.frames if f.is_change_of_state()]) > 0


class Member(object):

    """Represents a single member of a VerbClass, with associated name, WordNet
    category and PropBank grouping."""

    def __init__(self, soup):
        self.soup = soup
        self.name = self.soup.get('name')
        self.wn = self.soup.get('wn')
        self.grouping = self.soup.get('grouping')

    def __str__(self):
        return "<Member %s %s %s>" % (self.name, self.wn, self.grouping)


class Frame(object):

    """Represents a single verb frame in VerbNet, with a description, examples,
    syntax, and semantics """

    def __init__(self, soup, vnclass, class_ID):
        self.soup = soup
        self.vnclass = vnclass
        self.class_ID = class_ID
        self.description = self.soup.DESCRIPTION.get('primary')
        self.examples = [e.text for e in self.soup.EXAMPLES.find_all("EXAMPLE")]
        self.syntax = self.get_syntax()
        self.predicates = [Predicate(p)
                           for p in self.soup.SEMANTICS.find_all("PRED")]

    def __str__(self):
        return "<Frame %s [%s]>" % (self.class_ID, self.description)

    def get_syntax(self):
        syntax_elements = [c for c in self.soup.SYNTAX.children
                           if isinstance(c, bs4.element.Tag)]
        roles = [SyntacticRole(soup, self) for soup in syntax_elements]
        # there used to be a test for the value of pos, now just write a warning
        # if we find a missing pos
        for role in roles:
            if role.pos is None:
                print("Warning: empty pos in %s" % role)
        return roles

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

    def is_motion(self):
        """Return True if one of the predicates is a motion predicate."""
        return True if self.find_predicates('motion') else False

    def is_change_of_possession(self):
        """Return True if one of the predicates is a ch_of_poss predicate."""
        return True if self.find_predicates_with_argval('ch_of_poss') else False

    def is_transfer_of_info(self):
        """Returns True if one of the predicates has a tr_of_info predicate."""
        return True if self.find_predicates_with_argval('tr_of_info') else False

    def is_change_of_state(self):
        """Returns True if one of the predicates is a ch_of_state predicate."""
        return True if self.find_predicates_with_argval('ch_of_state') else False


class ThematicRole(object):

    """Represents an entry in the "Roles" section in VerbNet, which is basically
    a list of all roles for a given verb class, with possible selectional
    restrictions"""

    def __init__(self, soup):
        self.soup = soup
        self.role_type = self.soup.get('type')
        self.sel_restrictions = SelectionalRestrictions(self.soup.SELRESTRS)

    def __str__(self):
        if self.sel_restrictions.is_empty():
            return self.role_type
        else:
            return "%s / %s" % (self.role_type, self.sel_restrictions)

    def html(self):
        def role(text):
            return "<span class=role>%s</span>" % text
        if self.sel_restrictions.is_empty():
            return role(self.role_type)
        else:
            return "%s / %s" % (role(self.role_type), self.sel_restrictions)


class Predicate(object):

    """Represents the different predicates assigned to a frame"""

    def __init__(self, soup):
        self.soup = soup
        self.value = self.soup.get('value')
        args = self.soup.find_all('ARG')
        self.args = [(arg.get('type'), arg.get('value')) for arg in args]

    def __str__(self):
        return "%s(%s)" % (self.value, ', '.join([a[1] for a in self.args]))

    def find_arguments(self, arg):
        """Return all arguments in self.args where the arg paramter matches one of
        the argument's elements. Note that an argument is a pair of an argument type
        and an argument value, as in <Event,during(E)> or <ThemRole,Theme>."""
        return [a for a in self.args if arg in a]

    def html(self):
        args = ', '.join([arg[1] for arg in self.args])
        return "<span class=pred>%s</span>(%s)" % (self.value, args)


class SyntacticRole(object):

    """Represents a syntactic role assigned to a frame"""

    def __init__(self, soup, frame):
        self.soup = soup
        self.frame = frame
        self.pos = self.soup.name
        self.value = self.soup.get('value')
        self.restrictions = None
        self.restrictions = SyntacticRestrictions(self.soup.SYNRESTRS)
        # some syntactic roles have semantic selection restrictions on them, try
        # to collect them when there are no syntactic restrictions
        # TODO: must check where all restrictions occur
        if self.restrictions.is_empty():
            if self.soup.SELRESTRS is not None:
                self.restrictions = SelectionalRestrictions(self.soup.SELRESTRS)

    def __str__(self):
        return "<SyntacticRole pos=%s value=%s restrictions=%s>" \
            % (self.pos, self.value, self.restrictions)

    def get_restrictions(self):
        """Returns the restrictions for the role as defined on the thematic role
        that the syntactic role fullfills."""
        for role in self.frame.vnclass.roles:
            if role.role_type == self.value:
                return role.sel_restrictions
        return None


class Restrictions(object):

    """Abstract class with common functionality for selectional restrictions and
    syntactic restrictions."""

    def __str__(self):
        operator = ' & ' if self.logic == 'and' else ' | '
        return "(%s)" % operator.join([str(s) for s in self.restrictions])

    def is_empty(self):
        return self.restrictions == []

    def set_restrictions(self, tagname):
        """Set the restrictions given the tagname. Make sure that self.logic is set to
        None if there are no restrictions."""
        soups = self.soup.find_all(tagname)
        self.restrictions = [Restriction(soup) for soup in soups]
        if not self.restrictions:
            self.logic = None


class SelectionalRestrictions(Restrictions):

    """Stores information in the SELRESTRS tag. The list of SELREST tags inside will
    be put in self.selections. The SELRESTRS tag has an optional attribute named
    'logic', if it is expressed its value is always 'or'. If not expressed and
    the list of SELRESTR is not empty, then it is assumed to be 'and', if the
    list is empty than 'logic' will be set to None."""

    # TODO: check whether absence of 'or' indeed means 'and'

    def __init__(self, soup):
        self.soup = soup
        self.name = self.soup.name
        self.logic = self.soup.get('logic', 'and')
        self.set_restrictions('SELRESTR')


class SyntacticRestrictions(Restrictions):

    """Stores information in the SYNRESTRS tag. The list of SYNREST tags inside will
    be put in self.selections. This class is slightly simpler than its counterpart
    SelectionalRestrictions since it never has the 'logic' attribute. However, it
    is assumed to be 'and'."""

    # TODO: check whether absence of 'logic' attribute indeed means 'and'

    def __init__(self, soup):
        self.soup = soup
        if self.soup is None:
            self.logic = None
            self.restrictions = []
        else:
            self.name = self.soup.name
            self.logic = 'and'
            self.set_restrictions('SYNRESTR')


class Restriction(object):

    """Stores the content of SELRESTR or SYNRESTR, which has 'Value' and 'type'
    attributes, for example <SELRESTR Value="+" type="animate"/>."""

    def __init__(self, soup):
        self.soup = soup
        self.name = self.soup.name
        self.srvalue = self.soup.get('Value')
        self.srtype = self.soup.get('type')

    def __str__(self):
        return "%s%s" % (self.srvalue, self.srtype)


class PrettyPrinter(object):

    """Pretty printer for verb classes.

    >>> PrettyPrinter().pp(verbclass)

    """

    def __init__(self, step='    '):
        self.step = step

    def pp(self, verbclass, indent=0, nl=False):
        print("%s<VerbClass %s>" % (indent * self.step, verbclass.ID))
        print("%s%s%s" % (indent * self.step,
                          self.step,
                          ' '.join(verbclass.member_names)))
        for role in verbclass.roles:
            self.pp_role(role, indent + 1)
        for frame in verbclass.frames:
            self.pp_frame(frame, indent + 1)
        for subclass in verbclass.subclasses:
            self.pp(subclass, indent + 1)
        if nl:
            print()

    def pp_role(self, role, indent=0):
        print("%s<%s %s>" % (self.step * indent, '\u03b8', role))

    def pp_frame(self, frame, indent=0):
        print("%s<Frame %s>" % (indent * self.step, frame.description))
        for example in frame.examples:
            print('%s  "%s"' % (indent * self.step, example))
        for role in frame.syntax:
            print("%s  %s" % (indent * self.step, role))
        for pred in frame.predicates:
            print("%s  %s" % (indent * self.step, pred))


if __name__ == '__main__':

    vn = VerbNet(limit=5)
    for vclass in vn.classes:
        print(vclass)
        # PrettyPrinter().pp(vclass, nl=True)
