# -*- coding: utf8 -*-
from distutils.core import setup
import subprocess
import os

#===============================================================================
# texmf discover
#===============================================================================
local = subprocess.check_output('kpsewhich -var-value=TEXMFLOCAL', shell=True)
local = local.decode('utf8').split(':')[0].strip()
TEXMF_DIR = os.path.join(local, 'tex', 'latex', 'alttex')

#===============================================================================
# Main setup routine
#===============================================================================
CFG = \
setup(name='alttex',
      version='0.2a',
      description='LaTeX pre-processor with support to templates, separate data sources, and alternatives.',
      author='Fábio Macêdo Mendes',
      author_email='fabiomacedomendes@gmail.com',
      url='code.google.com/p/alttex',
      long_description=(
r'''A LaTeX pre-processor that supports alternatives, templates and more.

Main features:
  * Uses LaTeX syntax.
  * Can be used both as a program (the ``alttex`` executable) for final users, 
    or as a separate library for developers. 
  * Create alternative documents from a single source using the commands
    \\ALT, \\IF, \\ELSE, etc. 
  * Support for Jinja2 templates using a LaTeX-like syntax. It can be used as 
    an alternative to traditional LaTeX programming or to supply the LaTeX 
    document with data from different sources such as a Python script, a JSON 
    structure, a database, and others. 
'''),
      classifiers=[
          'Development Status :: 3 - Alpha',
          'Intended Audience :: Developers',
          'License :: OSI Approved :: GNU General Public License (GPL)',
          'Operating System :: POSIX',
          'Programming Language :: Python',
          'Topic :: Software Development :: Libraries',
          ],
      package_dir={'': 'src'},
      packages=['pytex', 'pytex.textypes', 'pytex.types', 'pytex.bin', 'pytex.util',
                'pytex.lib', 'pytex.lib.packages', 'pytex.lib.latex', 'pytex.lib.tex',
                'alttex', 'alttex.script', 'alttex.var_command',
                'alttex.filters'],
      scripts=['data/alttex', 'data/aLaTeX'],
      data_files=[(TEXMF_DIR, ('data/alttex.sty',))],
      requires=[],
)

# Post processing
if 'install' in CFG.script_args:
    print('Executing texhash')
    subprocess.check_call('texhash', shell=True)
