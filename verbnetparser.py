"""
This program takes in VerbNet XML files and creates several classes for easy
manipulation of the data, for eventual inclusion of GL features to individual 
verb frames.
"""

import os
from bs4 import BeautifulSoup as soup

__author__ = ["Todd Curcuru"]
__date__ = "3/15/2016"
__email__ = ["tcurcuru@brandeis.edu"]

PROJECT_PATH = os.getcwd()
VERBNET_PATH = os.path.join(PROJECT_PATH, "new_vn")


class VerbNetParser(object):
    """Parse VerbNet XML files, and turn them into a list of BeautifulSoup 
    objects"""
    
    def __init__(self, file_directory=VERBNET_PATH):
        self.filenames = [os.path.join(VERBNET_PATH, fname) for fname in 
                          os.listdir(VERBNET_PATH) if fname.endswith(".xml")]
        self.parsed_files = self.parse_files()
        self.verb_classes = [VerbClass(parse) for parse in self.parsed_files]
        
    def parse_files(self):
        """Parse a list of XML files using BeautifulSoup. Returns list of parsed
        soup objects"""
        parsed_files = []
        for fname in self.filenames:
            parsed_files.append(soup(open(fname), "lxml-xml"))
        return parsed_files

class VerbClass(object):
    """Represents a single class of verbs in VerbNet (all verbs from the same 
    XML file)."""
    
    def __init__(self, soup):
        self.soup = soup
        self.members = self.members()
        self.frames = self.frames()
        self.names = [mem.get_category('name')[0] for mem in self.members]
        
    def members(self):
        """Get all members of a verb class"""
        return [Member(mem_soup) for mem_soup in self.soup.MEMBERS.find_all("MEMBER")]
    
    def frames(self):
        """Get all frames for a verb class, seems to be shared by all members
        of the class."""
        return [Frame(mem_soup) for mem_soup in self.soup.FRAMES.find_all("FRAME")]
    
    def __repr__(self):
        return str([mem.__repr__() for mem in self.members])
        
class AbstractXML(object):
    """Abstract class to be inherited by other classes that share the same 
    features"""
    
    def __init__(self, soup):
        self.soup = soup
        
    def get_category(self, cat, special_soup=None):
        """Extracts the category from a soup, with the option to specify a soup. 
        
        For MEMBERs, we have:
        name (lexeme),
        wn (WordNet category)
        grouping (PropBank grouping)"""
        if not special_soup:
            special_soup = self.soup
        try:
            return special_soup.get(cat).split()
        except AttributeError:
            return []

class Member(AbstractXML):
    """Represents a single member of a VerbClass, with associated name, WordNet
    category, and PropBank grouping"""
    
    def __init__(self, soup):
        self.soup = soup
        self.name = self.get_category('name')
        self.wn = self.get_category('wn')
        self.grouping = self.get_category('grouping')
                
    def __repr__(self):
        return str(self.name + self.wn + self.grouping)
            
class Frame(AbstractXML):
    """Represents a single verb frame in VerbNet, with a description, examples,
    syntax, and semantics """

    def __init__(self, soup):
        self.soup = soup
        self.description_num = self.get_category('descriptionNumber', 
                                                 self.soup.DESCRIPTION)
        self.primary = self.get_category('primary', self.soup.DESCRIPTION)
        self.secondary = self.get_category('secondary', self.soup.DESCRIPTION)
        self.xtag = self.get_category('xtag', self.soup.DESCRIPTION)
        self.examples = [example.text for example in self.soup.EXAMPLES.find_all("EXAMPLE")]
        self.syntax = [SyntacticRole(role) for role in self.soup.SYNTAX.children]
        #self.semantics = SemanticRoles(self.soup.SEMANTICS)
        
    def __repr__(self):
        return "\nDN: " + str(self.description_num) + \
               "\nPrimary: " + str(self.primary) + \
               "\nSecondary: " + str(self.secondary) + \
               "\nXtag: " + str(self.xtag) + \
               "\nExamples: " + str(self.examples) + \
               "\nSyntax: " + str(self.syntax)
    
class ThemeRole(object):
    """Represents an entry in the "Roles" section in VerbNet, which is basically 
    a list of all roles for a given verb class.
    
    TODO - different enough from classes below to warrant a class?"""
    
    def __init__(self):
        pass

class SemanticRoles(AbstractXML):
    """Represents the semantics roles assigned to a frame
    TODO - do syntax first"""
    
    def __init__(self, soup):
        self.soup = soup
        pass
    
class SyntacticRole(object):
    """Represents a syntactic role assigned to a frame"""
    
    def __init__(self, soup):
        self.soup = soup
        self.children = self.children()
        
    def children(self):
        """Check for children/attributes
        TODO: Either make this recursive, or have cases for all kinds of children
        that our nodes can have. 
        NP has value and SYNRESTRS which have Value and type
        PREP has value sometimes and SELRESTRS with Value and type
        SYN/SELRESTRS can be empty
        VERB seems empty"""
        try:
            return [child for child in self.soup.children]
        except AttributeError:
            return None
        
    def __repr__(self):
        return str(self.soup) + "Children " + str(self.children)
            

# Test it out
if __name__ == '__main__':
    
    vnp = VerbNetParser()
    #print vnp.filenames, len(vnp.filenames)
    print len(vnp.parsed_files)
    mems = vnp.parsed_files[0].MEMBERS
    for mem in mems.find_all("MEMBER"):
        print mem.get('name'), mem.get('wn').split(), mem.get('grouping').split()
    #print mems.find_all("MEMBER")
    vc1 = vnp.verb_classes[0]
    print vc1
    print vc1.names
    print vc1.frames