"""verbnet.py

NOTE. This module is deprecated and most of its role has been usurped by modules
in the parent directory. However, it may still have some value and some of the
code here may be ported so let's not delete it for now.

This module contains the VerbNet class which interfaces to the contents of
VerbNet. In addition it has a couple of classes that are wrappers around a
couple of VerbNet elements, these classes include VerbClass, Frame, Predicate,
Argument and Role. Finally, PredicateStatistics is a class that generates
statistics for predicates.

You can open a VerbNet instance using a list of XML files with verb classes:

>>> fnames = ('data/slide-11.2.xml', 'data/tell-37.2.xml')
>>> vn = VerbNet(fnames=fnames)
>>> print(vn)
<VerbNet on 2 classes>

Alternatively you can open an instance on all XML files in a directory:

>>> vn = VerbNet(directory='data')
>>> print(vn)
<VerbNet on 3 classes>

You can get all classes:

>>> for cl in sorted(vn.get_classes()):
...      print(cl)
<VerbClass slide-11.2>
<VerbClass swat-18.2>
<VerbClass tell-37.2>

Or just look up one class using its full name including the class version:

>>> print(vn['slide-11.2'])
<VerbClass slide-11.2>

Frames can be accessed easily:

>>> for frame in  vn['slide-11.2'].frames[:3]:
...     print(frame)
<Frame slide-11.2  0.1 'NP V'>
<Frame slide-11.2  0.1 'NP V PP.initial_location'>
<Frame slide-11.2  0.1 'NP V PP.destination'>

The PredicateStatistics class produces some html files with statistics:

>>> stats = PredicateStatistics(vn, pred='motion')
>>> stats.print_missing_links('out-missing-roles.html')
>>> stats.print_predicates('out-predicates.txt')

In the case above, the results are written to two files and the statistics are
limited to classes that contain a motion predicate.

"""


import os
import sys
import glob
import collections
from xml.dom import minidom


# This is a hard-wired link to the online version at colorado of 3.2.4
VERBNET_URL = 'http://verbs.colorado.edu/vn3.2.4-test-uvi/vn/'


TEXT_HEAD = """
<head>
<style>
dt { margin-top: 12pt; margin-bottom: 5pt; }
dd { margin-bottom: 8pt; }
.classname { font-size: 120% }
.pred { color: darkred; font-weight: bold; font-variant: small-caps; font-size: 125%; }
.role { color: darkblue; font-weight: bold; }
.example { font-style: italic; }
.synsem { display: block; margin-left: 20pt; margin-top: 3pt; }
.boxed { border: thin dotted grey; padding: 3pt; }
</style>
</head>
"""

TEXT_MISSING_LINKS = """
<p>This lists all occurrences where the thematic roles expressed in the syntax
of a frame are not the same as those in the semantics. The links lead to pages
at <a href="http://verbs.colorado.edu/vn3.2.4-test-uvi/vn/"
>http://verbs.colorado.edu/vn3.2.4-test-uvi/vn/</a>. Those pages are not always
based on the same XML files as used by these diagnostics. This is for example
the case for the admit verb class. The XML files for these diagnostics have
admit-65.xml for this class, but online we have admit-64.3.php, a slightly
earlier version. As a result, clicking the admit-65 link will give a
page-not-found error.</p>
"""


# A few abbreviations of dom methods

def get_attr(node, attr):
    return node.getAttribute(attr)


def get_type(node):
    return node.getAttribute('type')


def get_value(node):
    return node.getAttribute('value')


def get_elements(node, tagname):
    return node.getElementsByTagName(tagname)


def is_role(role):
    return role and (role[0].isupper() or role[0] == '?')


def remove_role_suffix(role):
    """Map things like Theme_i and Theme_j to Theme, which makes role mapping a
    bit more tolerant."""
    return role[:-2] if role[-2:] in ('_i', '_j') else role


def spanned(text, css_class):
    """Wrap text in a span tag using css_class for the class."""
    return "<span class=%s>%s</span>" % (css_class, text)


class VerbNet(object):

    """Object that contains all VerbNet classes or a subset of those classes,
    taken from a directory with xml files or a list of filenames. Contains a
    dictionary of VerbClasses indexed on class name.

    directory  -  directory with verbnet files
    fnames     -  list of files to use, often taken from the directory variable
    url        -  UR of the online verbnet version at verbs.colorado.edu
    classes    -  dictionary of VerbClass instances for each VN file

    """

    def __init__(self, fnames=None, directory=None, url=VERBNET_URL):
        self.directory = directory
        self.fnames = fnames
        self.url = url
        if directory is None and fnames is None:
            exit('ERROR: VebNet instance needs fnames or directory argument')
        if self.fnames is None:
            self.fnames = glob.glob("%s/*.xml" % self.directory)
        self.classes = {}
        for fname in self.fnames:
            vc = VerbClass(fname)
            self.classes[vc.classname] = vc

    def __str__(self):
        return "<VerbNet on %d classes>" % len(self.fnames)

    def __getitem__(self, classname):
        """Return None or the VerbClass instance for classname."""
        return self.classes.get(classname)

    def get_classes(self):
        """Return a list of all classes."""
        return list(self.classes.values())


class VerbNetObject(object):

    """Abstract class. Instances of subclasses are all wrappers around DOM elements
    and they all have a node instance variable that contains the DOM Element."""

    def get(self, tagname):
        """Return all elements from the DOM node that match tagname."""
        return get_elements(self.node, tagname)


class VerbClass(VerbNetObject):

    """A VerbClass object is generated from an xml file, the class name is taken
    from the file name and the node object is the DOM object for the file. in
    addition, there is a list of roles and a list of frames, implemented as Role
    objects and Frame objects respectively."""

    def __init__(self, fname):
        self.fname = fname
        self.classname = os.path.basename(fname)[:-4]
        self.node = minidom.parse(open(fname))
        self.roles = [Role(role) for role in self.get('THEMROLE')]
        self.frames = [Frame(self, frame) for frame in self.get('FRAME')]

    def __str__(self):
        return "<VerbClass %s>" % self.classname

    def __cmp__(self, other):
        return cmp(self.classname, other.classname)

    def __lt__(self, other):
        return self.classname < other.classname

    def predicates(self):
        """Return Predicate instances for all the frames of the verb class."""
        return [Predicate(n) for n in get_elements(self.node, 'PRED')]

    def contains_predicate(self, predname):
        """Return True if one of the predicates used in frames of the verb class
        is equal to predname."""
        for p in self.predicates():
            if p.value == predname:
                return True
        return False

    def pp(self):
        print(self.classname)

    def print_html(self, fh=None):
        if fh is None:
            fh = sys.stdout
        fh.write("<html>\n")
        fh.write(TEXT_HEAD)
        fh.write("<body>\n\n")
        fh.write("<h2>%s</h2>\n\n" % self.classname)
        for frame in self.frames:
            frame.print_html()
            fh.write("\n")
        fh.write("</body>\n")
        fh.write("</html>\n")


class Role(VerbNetObject):

    """This is created from a THEMROLE element. It has a rolename instance variable
    which stores the type attribute (Agent, Theme and so forth). The selectional
    restriction live in a subelement SELRESTR on the DOM node element."""

    # TODO: perhaps create restrictions instance variable

    def __init__(self, role_node):
        self.node = role_node
        self.rolename = self.node.getAttribute('type')

    def __str__(self):
        return "<%s %s>" % (self.node.tagName, self.rolename)


class Frame(VerbNetObject):

    """Implements one frame element from a VerbClass. Frame elements are mostly
    defined by their number and description, but there are cases where we need
    the secondary description to get full uniquencess, we are ignoring it here
    though.

    vc           -  instance of VerbClass
    node         -  the full DOM element
    number       -  description number of the frame
    description  -  primary description, strings like "NP V PP.initial_location"
    example      -  example sentence
    syntax       -  SYNTAX DOM element
    semantics    -  SEMANTICS DOM element

    """

    def __init__(self, verb_class, frame_node):
        self.vc = verb_class
        self.node = frame_node
        description = self.get('DESCRIPTION')[0]
        self.number = description.getAttribute('descriptionNumber')
        self.description = description.getAttribute('primary')
        self.example = self.get('EXAMPLE')[0].firstChild.data
        self.syntax = self.get('SYNTAX')[0]
        self.semantics = self.get('SEMANTICS')[0]

    def __str__(self):
        return "<Frame %s  %s '%s'>" \
            % (self.vc.classname, self.number, self.description)

    def predicates(self):
        """Returns a list of Predicate instances for all the predicates in the
        semantics of the frame."""
        return [Predicate(pred) for pred in get_elements(self.semantics, 'PRED')]

    def syntax_roles(self):
        """Return a set with all roles expressed in the syntax, these are in the
        value attribute of elements like NP."""
        # Example return value: {'Agent', 'Theme'}.
        roles = set()
        for child in self.syntax.childNodes:
            if child.nodeType == minidom.Node.ELEMENT_NODE:
                role = get_value(child)
                if is_role(role):
                    roles.add(get_value(child))
        return roles

    def semantics_roles(self):
        """Return a set with all roles expressed in the semantics, these are in
        the value attribute of ARG elemengts with type=ThemRole. These roles are
        often the same as those returned by syntax_roles(), but not always."""
        # Example return value: {'Recipient', 'Agent', '?Topic'}
        roles = set()
        for pred in self.predicates():
            for arg in pred.args:
                t = arg.arg_type
                v = arg.arg_value
                if t == 'ThemRole' and is_role(v):
                    role = remove_role_suffix(v)
                    roles.add(role)
        return roles

    def _syntax_html_string(self):
        elements = []
        for child in self.syntax.childNodes:
            if child.nodeType == minidom.Node.ELEMENT_NODE:
                tag = child.tagName
                role = get_value(child)
                elements.append("%s-%s" % (tag, spanned(role, 'role')) if role else tag)
        return ' '.join(elements)

    def _semantics_html_string(self):
        return ' &amp; '.join([pred.as_html_string() for pred in self.predicates()])

    def print_html(self, description=True, fh=None):
        if fh is None:
            fh = sys.stdout
        if description:
            fh.write("<p>%s</p>\n\n" % self.description)
        fh.write("<table class=synsem>\n")
        fh.write("  <tr><td class=example>%s</td></tr>\n" % self.example)
        fh.write("  <tr><td>SYN: %s</td></tr>\n" % self._syntax_html_string())
        fh.write("  <tr><td>SEM: %s</td></tr>\n" % self._semantics_html_string())
        fh.write("</table>\n")


class Predicate(VerbNetObject):

    """Implements a predicate from the semantics. Each predicate has a value (which
    is possibly negated) and a list of arguments.

    node      -  DOM node
    value     -  name of the predicate ("motion", "direction", "cause" etcetera)
    negated   -  boolean to indicate negation of value
    args      -  list of Argument instances, one for each ARG element

    """

    def __init__(self, pred_node):
        self.vc = None
        self.node = pred_node
        self.value = get_value(pred_node)
        self.negated = False
        if get_attr(self.node, 'bool') == '!':
            # bool="!" as a property on PRED indicates not(self.value)
            self.negated = True
        self.args = [Argument(arg, self) for arg in get_elements(pred_node, 'ARG')]

    def __str__(self):
        negated = '!' if self.negated else ''
        return "<Predicate %s%s>" % (negated, self.value)

    def argtypes(self):
        return [(a.arg_type, a.arg_value) for a in self.args]

    def as_html_string(self):
        args = ["%s" % spanned(at[1], 'role') for at in self.argtypes()]
        pred = "<span class=pred>%s</span>(%s)" % (self.value, ', '.join(args))
        if self.negated:
            pred = "<span class=pred>not</span>(%s)" % pred
        return pred


class Argument(VerbNetObject):

    """Implements an argument, which has a type and a value."""

    def __init__(self, arg_node, predicate):
        self.predicate = predicate
        self.arg_type = get_type(arg_node)
        self.arg_value = get_value(arg_node)

    def __str__(self):
        return "<Argument type=%s value=%s>" % (self.arg_type, self.arg_value)


class PredicateStatistics(object):

    """Create statistics on predicates in a set of VerbNet classes."""

    def __init__(self, vn, pred=None):
        self.vnclasses = vn.get_classes()
        if pred is not None:
            self.vnclasses = [c for c in self.vnclasses if c.contains_predicate(pred)]
        self.predicates = {}
        self.statistics = {}
        self.missing_links = {}
        self._collect_predicates()
        self._collect_statistics()
        self._collect_missing_links()

    def _collect_predicates(self):
        for vc in self.vnclasses:
            for predicate in vc.predicates():
                predicate.vc = vc
                self.predicates.setdefault(predicate.value, []).append(predicate)

    def _collect_statistics(self):
        for pvalue, predicates in list(self.predicates.items()):
            self.statistics[pvalue] = {'classes': {},
                                       'arguments': collections.Counter()}
            for pred in predicates:
                self.statistics[pvalue]['classes'][pred.vc.classname] = True
                self.statistics[pvalue]['arguments'].update(pred.argtypes())

    def _collect_missing_links(self):
        for vnclass in self.vnclasses:
            classname = vnclass.classname
            for frame in vnclass.frames:
                syn_roles = frame.syntax_roles()
                sem_roles = frame.semantics_roles()
                for role in sem_roles.difference(syn_roles):
                    # the ? indicates that the role does not need to be expressed in
                    # the syntax
                    if not role.startswith('?'):
                        lst = ['syntax', role, frame]
                        self.missing_links.setdefault(classname, []).append(lst)
                for role in syn_roles.difference(sem_roles):
                    lst = ['semantics', role, frame]
                    self.missing_links.setdefault(classname, []).append(lst)

    def print_missing_links(self, fname=None):
        fh = sys.stdout if fname is None else open(fname, 'w')
        fh.write("<html>\n")
        fh.write(TEXT_HEAD)
        fh.write("<body>\n\n")
        fh.write("<h2>Role mismatches</h2>\n\n")
        fh.write(TEXT_MISSING_LINKS)
        fh.write("\n<div class=boxed>Verb classes with missing roles\n" +
                 "<blockquote>\n")
        for classname in sorted(self.missing_links.keys()):
            fh.write("  <a href=\"#%s\">%s</a>\n" % (classname, classname.split('-')[0]))
        fh.write("</blockquote>\n</div>\n\n")
        fh.write("<dl>\n")
        for classname in sorted(self.missing_links.keys()):
            href = "%s%s.php" % (VERBNET_URL, classname)
            link = "<a href=\"%s\" class=classname>%s</a>" % (href, classname)
            fh.write("\n<a name=\"%s\"></a>\n<dt>\n  %s\n</dt>\n" % (classname, link))
            for (level, role, frame) in self.missing_links[classname]:
                fh.write("<dd>\n<span class=role>%s</span> is not expressed in %s of frame [%s]"
                         % (role, level, frame.description))
                fh.write("\n")
                frame.print_html(description=False, fh=fh)
                fh.write("</dd>\n")
        fh.write("\n</dl>\n\n")
        fh.write("</body>\n")
        fh.write("</html>\n")

    def print_predicates(self, fname=None):
        fh = sys.stdout if fname is None else open(fname, 'w')
        fh.write("\nFound %d predicates in %d verb classes\n\n"
                 % (len(self.predicates), len(self.vnclasses)))
        for pvalue in sorted(self.predicates):
            fh.write("\nPRED: %s\n" % pvalue)
            stats = self.statistics[pvalue]
            fh.write("\n   VN-CLASSES: %s\n" % ' '.join(sorted(stats['classes'])))
            fh.write("\n   ARGS:\n")
            for pair, count in sorted(stats['arguments'].items()):
                fh.write("   %3d  %s - %s\n" % (count, pair[0], pair[1]))


if __name__ == '__main__':

    import doctest
    doctest.testmod()

    if False:
        vn = VerbNet(directory='data')
        slide = vn.classes['slide-11.2']
        slide = vn.classes['swat-18.2']
        for f in slide.frames:
            print(f)
            f.predicates()
            #for p in f.predicates():
            #    print(p.node.toxml())
        stats = PredicateStatistics(vn, pred='motion')
        stats.print_missing_links('out-missing-roles.html')
        stats.print_predicates('out-predicates.txt')
