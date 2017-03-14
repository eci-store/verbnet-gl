"""verbnetparser.py

This program takes in VerbNet XML files and creates several classes for easy
manipulation of the data, for eventual inclusion of GL features to individual
verb frames.

"""

__author__  =  ["Todd Curcuru & Marc Verhagen"]
__date__    =  "3/15/2016"
__email__   =  ["tcurcuru@brandeis.edu, marc@cs.brandeis.edu"]

import os, bs4


def get_verbnet_directory():
    for line in open('config.txt'):
        if line.startswith('VERBNET_PATH'):
            return line.split('=')[1].strip()
    exit('WARNING: could not find a value for VERBNET_PATH')


VERBNET_PATH = get_verbnet_directory()


def read_verbnet(max_count=None, file_list=None):
    """Parse verbnet files and return a list of VerbClasses. Read all the verbnet
    files, but just take the first max_count files if max_count is used, or read
    filenames from a file if file_list is used."""
    fnames = [f for f in os.listdir(VERBNET_PATH) if f.endswith(".xml")]
    if max_count is not None:
        fnames = fnames[:max_count]
    if file_list is not None:
        fnames = ["%s.xml" % f for f in open(file_list).read().split()]
    filenames = [os.path.join(VERBNET_PATH, fname) for fname in fnames]
    soups = [bs4.BeautifulSoup(open(fname), "lxml-xml") for fname in filenames]
    return [VerbClass(fname, s) for fname, s in zip(filenames, soups)]


class VerbClass(object):

    """Represents a single class of verbs in VerbNet (all verbs from the same 
    XML file)."""

    # TODO: Check if nested subclasses have issues

    def __init__(self, fname, soup):
        self.fname = fname
        #print '\n',fname
        self.soup = soup
        vnclass = self.soup.VNCLASS
        if vnclass is not None:
            # see if you have a VNCLASS tag and get the ID from there
            self.ID = vnclass.get("ID")
        else:
            # else self.soup is a VNSUBCLASS tag and get the ID from there
            self.ID = self.soup.get("ID")
        self.members = self.members()
        self.frames = self.frames()
        self.names = [mem.name for mem in self.members]
        self.themroles = self.themroles()
        self.subclasses = self.subclass()

    def __str__(self):
        return "<GLVerbClass \"%s\" roles=%s frames=%s subclasses=%s members=%s>" \
            % (self.ID, len(self.themroles), len(self.frames),
               len(self.subclasses), len(self.members))

    def __repr__(self):
        return str(self.ID) + "\n" + str([mem.__repr__() for mem in self.members]) \
               + "\nThemRoles: " + str(self.themroles) \
               + "\nNames: " + str(self.names) \
               + "\nFrames: " + str(self.frames) \
               + "\nSubclasses: " + str(self.subclasses)

    def members(self):
        """Get all members of a verb class"""
        return [Member(mem_soup)
                for mem_soup in self.soup.MEMBERS.find_all("MEMBER")]

    def frames(self):
        """Get all frames for a verb class, seems to be shared by all members
        of the class."""
        return [Frame(frame_soup, self.ID)
                for frame_soup in self.soup.FRAMES.find_all("FRAME")]
        
    def themroles(self):
        """Get all the thematic roles for a verb class ans their selectional 
        restrictions."""
        return [ThematicRole(them_soup)
                for them_soup in self.soup.THEMROLES.find_all("THEMROLE")]

    def subclass(self):
        """Create a VerbClass instance for every subclass listed."""
        return [VerbClass(self.fname, sub_soup) for sub_soup
                in self.soup.SUBCLASSES.find_all("VNSUBCLASS", recursive=False)]


class Member(object):

    """Represents a single member of a VerbClass, with associated name, WordNet
    category, and PropBank grouping."""
    
    def __init__(self, soup):
        self.soup = soup
        self.name = self.soup.get('name')
        self.wn = self.soup.get('wn')
        self.grouping = self.soup.get('grouping')
                
    def __repr__(self):
        return "<Member %s %s %s>" %  (self.name, self.wn, self.grouping)


class Frame(object):

    """Represents a single verb frame in VerbNet, with a description, examples,
    syntax, and semantics """

    def __init__(self, soup, class_ID):
        self.soup = soup
        self.class_ID = class_ID
        self.description = self.soup.DESCRIPTION.get('primary')
        self.examples = [e.text for e in self.soup.EXAMPLES.find_all("EXAMPLE")]
        self.syntax = self.get_syntax()
        self.predicates = [Predicate(p) for p in self.soup.SEMANTICS.find_all("PRED")]

    def __repr__(self):
        return "\nDescription: " + str(self.description) + \
               "\nExamples: " + str(self.examples) + \
               "\nSyntax: " + str(self.syntax) + \
               "\nPredicates: " + str(self.predicates) + "\n"

    def get_syntax(self):
        syntax_elements = [c for c in self.soup.SYNTAX.children
                           if isinstance(c, bs4.element.Tag)]
        roles = [SyntacticRole(soup) for soup in syntax_elements]
        # there used to be a test for the value of pos, now just write a warning
        # if we find a missing pos
        for role in roles:
            if role.pos is None:
                print "Warning: empty pos in %s" % role
        return roles


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


class Predicate(object):

    """Represents the different predicates assigned to a frame"""
    
    def __init__(self, soup):
        self.soup = soup
        self.value = self.soup.get('value')
        args = self.soup.find_all('ARG')
        self.argtypes = [(arg.get('type'), arg.get('value')) for arg in args]

    def __str__(self):
        return "%s(%s)" % (self.value, ', '.join([at[1] for at in self.argtypes]))

    def __repr__(self):
        return "Value: " + str(self.value) + " -- " + str(self.argtypes)


class SyntacticRole(object):

    """Represents a syntactic role assigned to a frame"""

    def __init__(self, soup):
        self.soup = soup
        self.pos = self.soup.name
        self.value = self.soup.get('value')
        self.restrictions = None
        self.restrictions = SyntacticRestrictions(self.soup.SYNRESTRS)

    def __str__(self):
        return "<SyntacticRole pos=%s value=%s restrictions=%s>" \
            % (self.pos, self.value, self.restrictions)


class Restrictions(object):

    """Abstract class with common functionality for selectional restrictions and
    syntactic restrictions."""

    def __str__(self):
        if self.is_empty():
            return '()'
        op = ' & ' if self.logic == 'and' else ' || '
        return "(%s)" % op.join([str(s) for s in self.restrictions])

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


def psoup(soup):
    """Utility to print the soup xml on one line."""
    print "SOUP - %s" % str(soup).replace("\n",'')
