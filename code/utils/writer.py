"""writer.py

Utilities to write HTML files.

"""


import os


class HtmlWriter(object):

    """Class that knows how to create html files for a set of GLVerbClass
    instances. This class is responsible for writing the index file and for
    invoking HtmlClassWriter on individual classes."""

    def __init__(self, directory='html', url=None, version=None):
        self.verbnet_version = version
        self.verbnet_url = url
        self.directory = directory
        self.index = open(os.path.join(self.directory, 'index.html'), 'w')
        self.start()

    def write(self, gl_verb_classes, header):
        group = header.lower().replace(' ', '-')
        self.index.write("<td>\n")
        self.index.write("<table class=bordered cellpadding=8 cellspacing=0>\n")
        self.index.write("<tr class=header><td>%s</a>\n" % header)
        for verbclass in gl_verb_classes:
            infix = group + '-' if group else ''
            class_file = "vnclass-%s%s.html" % (infix, verbclass.ID)
            self.index.write("<tr class=vnlink><td><a href=\"%s\">%s</a>\n"
                             % (class_file, verbclass.ID))
            fh = open(os.path.join(self.directory, class_file), 'w')
            url = os.path.join(self.verbnet_url, verbclass.ID + '.php')
            HtmlClassWriter(fh, verbclass, url).write()
        self.index.write("</table>\n")
        self.index.write("</td>\n")

    def start(self):
        self.index.write("<html>\n")
        self.index.write("<head>\n")
        self.index.write("<link rel=\"stylesheet\" " +
                         "type=\"text/css\" href=\"style.css\">\n")
        self.index.write("<style>\n")
        self.index.write("body, table { width: unset; }\n")
        self.index.write("</style>\n")
        self.index.write("</head>\n")
        self.index.write("<body>\n")
        if self.verbnet_version is not None:
            vn = "Verbnet %s" % self.verbnet_version
            href = "href=%s" % self.verbnet_url
            self.index.write("<p class=header_link>Verbnet-GL," +
                             " based on <a %s>%s</a></p>\n" % (href, vn))
        self.index.write("<table class=noborder cellspacing=5>\n")
        self.index.write("<tr valign=top>\n")

    def finish(self):
        self.index.write("</tr>\n")
        self.index.write("</table>\n")
        self.index.write("</body>\n")
        self.index.write("</html>\n")


class HtmlClassWriter(object):

    """Class that knows how to write the HTML representation for a GLVerbClass
    to a file handle."""

    def __init__(self, fh, glverbclass, verbnet_url=None):
        self.fh = fh
        self.glverbclass = glverbclass
        self.verbnet_url = verbnet_url

    def write(self, frames=None):
        self._write_start()
        self._write_class()
        self._write_end()

    def _write_start(self):
        self.fh.write("<html>\n")
        self.fh.write("<head>\n")
        self.fh.write("<link rel=\"stylesheet\" type=\"text/css\" href=\"style.css\">\n")
        self.fh.write("</head>\n")
        self.fh.write("<body>\n")

    def _write_end(self):
        self.fh.write("</body>\n")
        self.fh.write("</html>\n")

    def _write_class(self, subclass=False):
        if subclass:
            self._write_subheader()
        else:
            self._write_header()
            self._write_verbnet_source()
        self._write_members()
        self._write_roles()
        for gl_frame in self.glverbclass.frames:
            self.fh.write("\n<!-- FRAME -->\n\n")
            self.fh.write("<table class=frame cellpadding=8 cellspacing=0 border=0>\n")
            self._write_description(gl_frame)
            self._write_example(gl_frame)
            self._write_syntax(gl_frame)
            self._write_semantics(gl_frame)
            self.fh.write("</table>\n\n")
        for subclass in self.glverbclass.subclasses:
            self.glverbclass = subclass
            self._write_class(subclass=True)

    def _write_header(self):
        self.fh.write("\n<h1>VerbnetGL &mdash; %s</h1>\n" % str(self.glverbclass.ID))

    def _write_subheader(self):
        self.fh.write("\n<h2>%s</h2>\n" % str(self.glverbclass.ID))

    def _write_verbnet_source(self):
        if self.verbnet_url is not None:
            href = "<a href=%s>%s</a>" % (self.verbnet_url, self.verbnet_url)
            self.fh.write("\n<table class=frame cellpadding=8 cellspacing=0 border=0>\n")
            self.fh.write("<tr class=vn valign=top>\n")
            self.fh.write("  <td>Verbnet source: %s\n" % href)
            self.fh.write("</table>\n")

    def _write_members(self):
        self.fh.write("\n<!-- MEMBERS -->\n\n")
        self.fh.write("<table class=frame cellpadding=8 cellspacing=0 border=0>\n")
        self.fh.write("<tr class=roles valign=top>\n")
        self.fh.write("  <td>Members\n")
        self.fh.write("<tr class=vn valign=top>\n")
        self.fh.write("  <td>\n")
        for name in self.glverbclass.names:
            self.fh.write("      %s\n" % name)
        self.fh.write("  </td>\n")
        self.fh.write("</tr>\n")
        self.fh.write("</table>\n")

    def _write_roles(self):
        self.fh.write("\n<!--ROLES -->\n\n")
        self.fh.write("<table class=frame cellpadding=8 cellspacing=0 border=0>\n")
        self.fh.write("<tr class=roles valign=top>\n")
        self.fh.write("  <td>Roles\n")
        self.fh.write("<tr class=vn valign=top>\n")
        self.fh.write("  <td>\n")
        self.fh.write("     <ul>\n")
        for role in self.glverbclass.roles:
            self.fh.write("      <li>%s</li>\n" % role.html())
        self.fh.write("     </ul>\n")
        self.fh.write("   </td>\n")
        self.fh.write("</tr>\n")
        self.fh.write("</table>\n")

    def _write_description(self, gl_frame, frame_number=None):
        self.fh.write("\n<!-- DESCRIPTION -->\n\n")
        self.fh.write("<tr class=description>\n")
        self.fh.write("  <td colspan=2>Frame &mdash; %s\n"
                      % (gl_frame.vnframe.description))
        self.fh.write("</tr>\n")

    def _write_example(self, gl_frame):
        self.fh.write("\n<!-- EXAMPLE -->\n\n")
        self.fh.write("<tr class=vn valign=top>\n")
        self.fh.write("  <td width=80>Example\n")
        self.fh.write("  <td>\"%s\"\n" % gl_frame.vnframe.examples[0])
        self.fh.write("</tr>\n")

    def _write_syntax(self, gl_frame):
        self.fh.write("\n<!-- SYNTAX -->\n\n")
        self.fh.write("<tr class=vn valign=top>\n")
        self.fh.write("  <td>Syntax\n")
        self.fh.write("  <td>\n")
        for element in gl_frame.subcat:
            self.fh.write("    %s \n" % element.html())
        self.fh.write("</tr>\n")

    def _write_semantics(self, gl_frame):
        vn_frame = gl_frame.vnframe
        self.fh.write("\n<!-- SEMANTICS -->\n\n")
        self.fh.write("<tr class=vn>\n")
        self.fh.write("  <td valign=top>Semantics\n")
        self.fh.write("  <td>\n")
        self.fh.write("    <table class=inner cellspacing=0 cellpadding=0>\n")
        self.fh.write("    <tr class=vn>\n")
        self.fh.write("      <td class=bordered valign=top>\n")
        self.fh.write("        <div class=semheader>Verbnet Predicates</div>\n")
        for pred in vn_frame.predicates:
            self.fh.write("       %s<br/>\n" % pred.html())
        self.fh.write("      </td>\n")
        self.fh.write("      <td width=20>&nbsp;\n")
        self._write_qualia(gl_frame)
        self.fh.write("      <td width=20>&nbsp;\n")
        self._write_event(gl_frame)
        self.fh.write("    </tr>\n")
        self.fh.write("    </table>\n\n")
        self.fh.write("  </td>\n\n")
        self.fh.write("</tr>\n\n")

    def _write_qualia(self, gl_frame):
        self.fh.write("      <td class=bordered valign=top>\n")
        self.fh.write("        <div class=semheader>Qualia&nbsp;structure</div>\n")
        for formula in gl_frame.qualia.formulas:
            self.fh.write("        %s<br/>\n" % formula.html())
        self.fh.write("      </td>\n")

    def _write_event(self, gl_frame):
        self.fh.write("      <td class=bordered valign=top>\n")
        self.fh.write("        <div class=semheader>Event structure</div>\n")
        for formula in gl_frame.events.formulas:
            self.fh.write("        %s<br/>\n" % (formula.html()))
        self.fh.write("      </td>\n")
