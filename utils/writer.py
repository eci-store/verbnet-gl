"""writer.py

Utilities to write HTML files.

"""


import os


class HtmlWriter(object):

    """Class that knows how to create html files for set of GLVerbClass
    instances. This class is responsible for writing the index file and for
    invoking HtmlClassWriter on individual classes."""
    
    def __init__(self, directory='html', url=None, version=None):
        self.verbnet_version = version
        self.verbnet_url = url
        self.directory = directory
        self.index = open(os.path.join(self.directory, 'index.html'), 'w')
        self._write_begin()

    def _write_begin(self):
        self.index.write("<html>\n")
        self.index.write("<head>\n")
        self.index.write("<link rel=\"stylesheet\" type=\"text/css\" href=\"style.css\">\n")
        self.index.write("<style>\n")
        self.index.write("body, table { width: unset; }\n")
        self.index.write("</style>\n")
        self.index.write("</head>\n")
        self.index.write("<body>\n")
        if self.verbnet_version is not None:
            vn = "Verbnet %s" % self.verbnet_version
            href = "href=%s" % self.verbnet_url
            self.index.write("<p class=header_link>Verbnet-GL, based on <a %s>%s</a></p>\n" % (href, vn))
        self.index.write("<table class=noborder >\n")
        self.index.write("<tr valign=top>\n")

    def write(self, gl_verb_classes, header, group=''):
        self.index.write("<td>\n")
        self.index.write("<table cellpadding=8 cellspacing=0>\n")
        self.index.write("<tr class=header><td>%s</a>\n" % header)
        for verbclass in gl_verb_classes:
            infix = group + '-' if group else ''
            class_file = "vnclass-%s%s.html" % (infix, verbclass.ID)
            self.index.write("<tr class=vnlink><td><a href=\"%s\">%s</a>\n" % (class_file, verbclass.ID))
            fh =  open(os.path.join(self.directory, class_file), 'w')
            HtmlClassWriter(fh, verbclass, self.verbnet_url).write()
        self.index.write("</table>\n")
        self.index.write("</td>\n")

    def finish(self):
        self.index.write("</tr>\n")
        self.index.write("</table>\n")
        self.index.write("</body>\n")
        self.index.write("</html>\n")


class HtmlClassWriter(object):

    """Class that knows how to write the HTML representation for a GLVerbClass to a
    file handle."""

    def __init__(self, fh, glverbclass, verbnet_url):
        self.fh = fh
        self.glverbclass = glverbclass
        self.verbnet_url = verbnet_url

    def write(self, frames=None):
        self.fh.write("<html>\n")
        self.fh.write("<head>\n")
        self.fh.write("<link rel=\"stylesheet\" type=\"text/css\" href=\"style.css\">\n")
        self.fh.write("</head>\n")
        self.fh.write("<body>\n")
        self.fh.write("\n<h1>%s</h1>\n" % str(self.glverbclass.ID))
        self.pp_html_verbnet_source()
        self.pp_html_roles()
        frames_to_print = range(len(self.glverbclass.frames))
        if frames is not None:
            frames_to_print = frames
        for i in frames_to_print:
            vn_frame = self.glverbclass.verbclass.frames[i]
            gl_frame = self.glverbclass.frames[i]
            self.fh.write("\n<table class=frame cellpadding=8 cellspacing=0 border=0>\n")
            self.pp_html_description(gl_frame)
            self.pp_html_example(gl_frame)
            self.pp_html_predicate(vn_frame)
            self.pp_html_subcat(gl_frame)
            self.pp_html_qualia(gl_frame)
            self.pp_html_event(gl_frame)
            self.fh.write("</table>\n\n")

    def pp_html_verbnet_source(self):
        if self.verbnet_url is not None:
            url = os.path.dirname(self.verbnet_url) + os.sep + self.glverbclass.ID + '.php'
            href = "<a href=%s>%s</a>" % (url, url)
            self.fh.write("\n<table class=frame cellpadding=8 cellspacing=0 border=0>\n")
            self.fh.write("<tr class=vn valign=top>\n")
            self.fh.write("  <td colspan=2>Verbnet source: %s\n" % href)
            self.fh.write("</table>\n")

    def pp_html_roles(self):
        self.fh.write("\n<table class=frame cellpadding=8 cellspacing=0 border=0>\n")
        self.fh.write("<tr class=roles valign=top>\n")
        self.fh.write("  <td colspan=2>Roles\n")
        self.fh.write("<tr class=vn valign=top>\n")
        self.fh.write("  <td colspan=2>\n    <ul>\n")
        for role in self.glverbclass.roles:
            self.fh.write("      <li>%s</li>\n" % role.html())
        self.fh.write("    </ul>\n</tr>\n</table>\n")

    def pp_html_description(self, gl_frame, frame_number=None):
        self.fh.write("\n<tr class=description>\n")
        frame_number = '' if frame_number is None else "Frame %s: " % frame_number
        self.fh.write("  <td colspan=2>%s%s\n" % (frame_number, gl_frame.description))
        self.fh.write("</tr>\n")

    def pp_html_example(self, gl_frame):
        self.fh.write("\n<tr class=vn valign=top>\n")
        self.fh.write("  <td width=180>Example\n")
        self.fh.write("  <td>\"%s\"\n" % gl_frame.examples[0])
        self.fh.write("</tr>\n")

    def pp_html_predicate(self, vn_frame):
        def predicate_str(pred):
            args = ', '.join([arg[1] for arg in pred.args])
            return "<span class=pred>%s</span>(%s)" % (pred.value, args)
        self.fh.write("\n<tr class=vn valign=top>\n")
        self.fh.write("  <td>Predicates\n")
        self.fh.write("  <td>\n")
        for pred in vn_frame.predicates:
            self.fh.write("     %s<br/>\n" % predicate_str(pred))
        self.fh.write("</tr>\n")

    def pp_html_subcat(self, gl_frame):
        self.fh.write("\n<tr class=vn valign=top>\n")
        self.fh.write("  <td>Subcategorisation\n")
        self.fh.write("  <td>\n")
        for element in gl_frame.subcat:
            self.fh.write("    %s \n" % element.html())
        #self.fh.write("  <br/>\n")
        #for element in gl_frame.subcat:
        #    self.fh.write("    %s<br/>\n" % element)
        self.fh.write("</tr>\n")

    def pp_html_qualia(self, gl_frame):
        self.fh.write("\n<tr class=qualia valign=top>\n")
        self.fh.write("  <td>Qualia&nbsp;structure\n")
        self.fh.write("  <td>%s\n" % gl_frame.qualia.html())
        self.fh.write("</tr>\n")

    def pp_html_event(self, gl_frame):
        if True:
            # use new way of printing this
            self.pp_html_event_new(gl_frame)
        else:
            # ... but keep the old one around for now
            self.fh.write("\n<tr class=event valign=top>\n")
            self.fh.write("  <td>Event structure")
            self.fh.write("  <td>var = %s<br>\n" % gl_frame.events.var)
            self.fh.write("      initial_state = %s<br>\n"
                          % gl_frame.events.initial_state().html())
            self.fh.write("      final_state = %s\n"
                          % gl_frame.events.final_state().html())
            self.fh.write("</tr>\n")

    def pp_html_event_new(self, gl_frame):
        self.fh.write("\n<tr class=event valign=top>\n")
        self.fh.write("  <td>Event structure")
        self.fh.write("  <td>%s\n" % (gl_frame.events.html()))
        self.fh.write("</tr>\n")


def html_var(var):
    """Takes a variable like "x1" and turns it into "x<sub>1</sub>". Works as long
    as the variable starts with one letter followed by some integers."""
    if var in ('?', '-?'):
        return var
    prefix = ''
    if var[0] == '-':
        prefix = '-'
        var = var[1:]
    return "%s%s<sub>%s</sub>" % (prefix, var[0], var[1:])
