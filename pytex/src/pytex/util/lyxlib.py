import os
import contextlib

#===============================================================================
# API functions
#===============================================================================
__all__ = ['lyx_export', 'lyx_to_tex']

def lyx_export(lyxfile, outfile=None, format='pdflatex'):  # @ReservedAssignment
    '''Export the given LyX file to the output format'''

    ext = FMT_EXTENSIONS.get(format, format)
    outfile = outfile or get_export_name(lyxfile, ext)

    # TODO: use something more robust than os.system()
    cmd = 'lyx -E %s "%s" "%s" &> /dev/null' % (format, outfile, lyxfile)
    os.system(cmd)

@contextlib.contextmanager
def lyx_to_tex(lyxfile, outfile=None, format='pdflatex'):  # @ReservedAssignment
    '''Context manager that creates a temporary export file from the given lyx 
    file
    
    Typical usage:
    
        # TeX file is saved as fname
        with latex_from_lyx('foo.lyx') as fname:
            data = open(fname, 'r', encoding='utf8').read()
        
        # TeX file is removed after leaving the with block
        os.path.exists(fname) # ==> False
    '''

    # Setup
    ext = FMT_EXTENSIONS.get(format, format)
    outfile = outfile or get_export_name(lyxfile, ext)
    lyx_export(lyxfile, outfile)

    # Return value
    try:
        yield outfile

    # Clean up
    finally:
        if os.path.exists(outfile):
            os.remove(outfile)

#===============================================================================
# Utility functions
#===============================================================================
def get_export_name(lyxname, ext, safe=True):
    '''Return the exported file name from the given lyxname.
    
    If safe=True, returns a name that doesn't exist in the filesystem.'''

    base = os.path.splitext(lyxname)[0]
    ext = ext if ext.startswith('.') else '.' + ext

    if safe:
        template = '%s-tmp%%03d%s' % (base, ext)
        for i in range(1, 1000):
            fname = template % i
            if not os.path.exists(fname):
                return fname
        else:
            raise RuntimeError('maximum number of attempts to created a new file for "%s"' % lyxname)
    else:
        return base + ext

#===============================================================================
# Module variables
#===============================================================================
FMT_EXTENSIONS = {'pdflatex': 'tex'}
