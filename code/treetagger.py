"""

Borrowed from TTK.

"""

import os, sys, threading
from subprocess import PIPE, Popen

MAC_EXECUTABLE = "tree-tagger"
LINUX_EXECUTABLE = "tree-tagger"
WINDOWS_EXECUTABLE = "tree-tagger.exe"
PARAMETER_FILE = "english-utf8.par"

START_TEXT = "<start-text>"
END_TEXT = "<end-text>"


class TreeTagger(object):

    """Class that wraps the TreeTagger."""

    def __init__(self, treetagger_dir):
        """Set up the pipe to the TreeTagger."""
        self.dir = os.path.abspath(treetagger_dir)
        self.bindir = os.path.join(self.dir, "bin")
        self.libdir = os.path.join(self.dir, "lib")
        executable = self._get_executable()
        parfile = os.path.join(self.libdir, PARAMETER_FILE)
        tagcmd = "%s -token -lemma -sgml %s" % (executable, parfile)
        # when using subprocess, need to use a different close_fds for windows
        close_fds = False if sys.platform == 'win32' else True
        self.process = Popen(tagcmd, shell=True,
                             stdin=PIPE, stdout=PIPE, close_fds=close_fds)

    def _get_executable(self):
        """Get the TreeTagger executable for the platform."""
        if sys.platform == "win32":
            executable = os.path.join(self.bindir, WINDOWS_EXECUTABLE)
        elif sys.platform == "linux2":
            executable = os.path.join(self.bindir, LINUX_EXECUTABLE)
        elif sys.platform == "darwin":
            executable = os.path.join(self.bindir, MAC_EXECUTABLE)
        else:
            print(("No binary for platform %s" % sys.platform))
        if not os.path.isfile(executable):
            print(("TreeTagger binary invalid: %s" % executable))
        return executable

    def __del__(self):
        """When deleting the wrapper, close the TreeTagger process pipes."""
        self.process.stdin.close()
        self.process.stdout.close()

    def tag_text(self, text):
        """Open a thread to the TreeTagger, pipe in the text and return the results."""
        # We add a period as an extra token. This is a hack to deal with a nasty
        # problem where sometimes the TreeTagger will not return a value. It is
        # not clear why this is. Later in this method we pop off the extra tag
        # that we get because of this. TODO: it would be better to deal with
        # this in a more general way, see multiprocessing.Pool with a timeout.
        text += "\n.\n"
        args = (self.process.stdin, text)
        thread = threading.Thread(target=_write_to_stdin, args=args)
        thread.start()
        result = []
        collect = False
        while True:
            line = self.process.stdout.readline().strip()
            if line == START_TEXT:
                collect = True
            elif line == END_TEXT:
                break
            elif line and collect:
                result.append(line)
        thread.join()
        result.pop()
        return result


def _write_to_stdin(pipe, text):
    pipe.write("%s\n" % START_TEXT)
    if text:
        pipe.write("%s\n" % text)
        # NOTE. Without the following the tagger will hang. Do not try to make
        # it shorter, it may need at least a space, but I have no idea why.
        pipe.write("%s\n.\ndummy sentence\n.\n" % END_TEXT)
        pipe.flush()
