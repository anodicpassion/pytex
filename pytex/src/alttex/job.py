if __name__ == '__main__' and __package__ is None:
    import pytex.alttex; __package__ = 'pytex.alttex'  # @UnusedImport @ReservedAssignment

import os
from pytex.util.files import readfile
from .altsource import AltSource

class Job:
    def __init__(self, file, filename=None):
        self.children, self.filename = readfile(file, filename)
        if self.filename.endswith('.lyx'):
            self.read_lyx()
        self.altsource = AltSource(self.children, self.filename)
        print(self.children)

        # Private attributes
        self._sections = list(self.altsource.get_section_names())
        self._output_name = os.path.splitext(self.filename)[0]
        self._exts = []
        self._texfiles = set()
        self._num_templates = 1

    def set_sections(self, sections):
        '''Set the sections that shall be used in the final document'''
        self._sections = list(sections)

    def set_output(self, output_name):
        '''Sets the name for the output file'''
        name, ext = os.path.splitext(output_name)
        self._output_name = name
        self._exts.append(ext[1:])

    def set_numdocs(self, value):
        self._num_templates = value

    def read_lyx(self):
        self.system('lyx -e latex %s' % self.filename)
        filename = self.filename[:-4] + '.tex'
        self.children, self.filename = readfile(open(filename), filename)

    #===========================================================================
    # Make final documents
    #===========================================================================
    def make_final(self):
        exts = self._exts or ['pdf']
        for ext in exts:
            worker = getattr(self, 'make_' + ext)
            worker()

    def make_pdf(self):
        self.make_tex()
        for f in self._texfiles:
            self.system('pdflatex -interaction=nonstopmode %s' % f)

    def make_tex(self):
        for section in self._sections:
            texfile = '%s-%s.tex' % (self._output_name, section)
            all_docs = self.altsource.get_all_documents(section)
            master = all_docs.pop(0)
            for doc in all_docs:
                master.document.add(doc.context.get_macro('clearpage', warn=0)())
                master.document.add(doc.document.clear())
            with open(texfile, 'w') as F:
                F.write(master.source())
                self._texfiles.add(texfile)

    def system(self, cmd):
        print(cmd)
        os.system(cmd)

if __name__ == '__main__':
    os.chdir('../../pytex_tests/examples')
    fname = 'integral.lyx'
    # os.system('gedit integral.tex')
    # os.system('evince integral-ans.pdf')
    job = Job(open(fname))
    job.make_final()
