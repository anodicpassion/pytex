import sys
import os
from pytex.errors import LaTeXError
from pytex import alttex
from pytex.util.errors import render_error

def pre_process(texfile, altfile):
    '''Process alttex file'''

    # Convert to latex if Lyx input
    if texfile.endswith('.lyx'):
        execute('lyx -e pdflatex %s' % texfile)
        texfile = texfile[:-3] + 'tex'

    # Process altsource for a single run
    with open(texfile) as F:
        try:
            alt = alttex.AltSource(F)
            out = alt.get_source(0)
        except:
            out = render_error(as_document=True)

    # Save the processed file
    with open(altfile, 'w') as F:
        F.write(out)

def process_error(texfile):
    print('error on: ', texfile)
    raise NotImplementedError

def execute(cmd):
    '''Executes a command in shell'''

    os.system(cmd)

#===============================================================================
# Take action
#===============================================================================
def main():
    'Executes the main command'

    texfile = altname = None
    argv = list(sys.argv)
    argv[0] = 'pdflatex'
    for idx, arg in enumerate(argv):
        if idx and not arg.startswith('-'):
            texfile = arg
            name, ext = os.path.splitext(texfile)
            altname = name + '-alt' + ext
            argv[idx] = altname
            break

    # No input file: simply redirects output to LaTeX
    if texfile is None:
        print('aLaTeX: pdfLaTeX frontend with a altex preprocessor\n')

        # Call latex with the correct arguments
        cmd = ' '.join(argv)
        execute(cmd)

    # Input! Preprocess and pass the procesed file to LaTeX
    else:
        try:
            pre_process(texfile, altname)
        except LaTeXError:
            process_error(texfile, altname)
        except FileNotFoundError:
            argv[idx] = texfile

        # Execute LaTeX with the pre-processed document
        cmd = ' '.join(argv)
        execute(cmd)

        # Change file names
        altname, _ = os.path.splitext(altname)
        if os.path.exists(altname + '.pdf'):
            execute('mv %s.pdf %s.pdf' % (altname, name))
            execute('rm %s.* -f' % altname)

if __name__ == '__main__':
    main()
