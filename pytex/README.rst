AltTeX
~~~~~~

AltTeX is a LaTeX preprocessor that extends the LaTeX language in many useful 
ways:
  * It allows creation of LaTeX documents that render alternative versions from 
    a single source.
  * It allows mixing data from external sources such as scripts, JSON files, 
    databases, etc.
  * It offers a powerful template language provided by the Jinja2 engine

Alttex was created for aiding teachers (specially math teachers like myself) to 
create exams. It is however sufficiently generic to be useful for different 
purposes.

Nutshell
--------

Here a small example of a simple LaTeX document ``quiz.tex`` decorated with some
AltTeX commands::

    \documentclass{article}
    \usepackage[utf8]{inputenc}
    \usepackage{alttex}
    
    \begin{document}
    1. What is the capital of \alt{Brazil|Argentina}? 
	
	\begin{altcase}
	  \case{answer}
	    The capital of \alt{Brazil|Argentina} is \alt{Brasília since 1960|Buenos Aires}. 
	    \alt{Rio de Janeiro and Salvador were previous capitals.|}
	  
	  \else
	  \par
	\end{altcase}
	
    \end{document}
    
The ``alttex`` executable creates two versions of this document. The first 
version contains the questions about the Brazilian and Argentinian capitals. The
second version also displays the content inside the ``\IF{answer}{...}`` blocks.

Besides creating multiple versions of a single document, AltTeX has a powerful
template engine and can use data from different sources such as Python scripts,
JSON and YAML files or databases.

Philosophy
----------

We are alpha software! Still working on that...


Installing pre-requisites
-------------------------

AltTeX requires Python3 (although it should be easy to port the code to Python 2). 
It also have a few external dependencies:
 
  * A LaTeX distribution. It is currently only tested in the Texlive 
    distribution under Linux. It may work in other systems, but it is currently
    not a priority in AltTeX development. http://www.tug.org/texlive/
  * Jinja2 template engine: http://jinja.pocoo.org/

It is almost always preferable to install the required libraries and AltTeX 
itself using the package manager of your system. In Debian and variants (i.e., 
Ubuntu) all pre-requisites can be installed by the superuser using::

  $ apt-get install texlive python3-jinja2
   
Jinja2 is also available in the Python Package Index (PyPI, 
http://pypi.python.org). It be installed using following command::

  $ pip install jinja2
  
Note: the proper PyPI command can be either ``pip3`` or ``pip`` depending 
whether Python 2 or Python 3 is the default version.

Installing AltTeX
-----------------

Once all pre-requisites are installed, AltTeX can be installed either using 
traditional distutils method::

  $ python setup.py install
  
Or using PyPI::

  $ pip install alttex
  
Note: if the default Python version of your system is still Python 2, use 
``python3`` and ``pip3`` in the commands above 