'''
``alttex`` Usage
================

The ``alttex`` command is used to compile LaTeX files that uses the commands
defined in the ``alttex`` package. Theses commands define alternatives (using
the \ALT, \ONLY, and the corresponding enviroments) and also a templating 
language (commands such as \VAR, \CMD, etc) that can be used used to mix LaTeX 
with some other data source.   
'''

from pytex.alttex.job import Job
import argparse
import os
import sys

#===============================================================================
# Parse arguments
#===============================================================================
def parser():
    'Creates a parser for the program arguments'

    parser = argparse.ArgumentParser(description='Compiles multiple versions of a LaTeX document in PDF')
    parser.add_argument('file', help='path of input file')
    parser.add_argument('-s', '--sections', help='list of sections separated by commas')
    parser.add_argument('-o', '--output', help='name of output file')
    parser.add_argument('-n', '--num-alts', type=int, default=0, help='number of alternatives to be created')
    parser.add_argument('-N', '--num-templates', type=int, default=1, help='number of template renderings to be created')
    parser.add_argument('-t', '--tex', action='store_true', help='create LaTeX output rather than compiling them to PDF\'s')
    parser.add_argument('-d', '--debug', action='store_true', help='run alttex in debug mode')
    return parser

#===============================================================================
# Debugger
#===============================================================================
def info(type, value, tb):
    import traceback, pdb
    # we are NOT in interactive mode, print the exception...
    traceback.print_exception(type, value, tb)
    print()
    # ...then start the debugger in post-mortem mode.
    pdb.pm()

#===============================================================================
# Take action
#===============================================================================
def main(cmd=None):
    'Executes the main command'

    args = parser().parse_args(cmd)
    if args.debug:
        sys.excepthook = info

    job = Job(open(args.file))
    if args.sections:
        job.set_sections(args.sections.split(','))
    if args.output:
        job.set_output(args.output)
    job.set_numdocs(args.num_templates)

    if args.tex:
        job.make_tex()
    else:
        job.make_pdf()

if __name__ == '__main__':
    os.chdir('../../examples')
    cmd = 'integral.lyx'
    main(cmd.split())
