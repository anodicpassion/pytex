def tex_document(body):
    '''Creates a complete LaTeX document from a string of LaTeX code that 
    represents the document body.'''

    return r'''\documentclass{article}
\begin{document}
\usepackage{Verbatim}
%s
\end{document}''' % body


