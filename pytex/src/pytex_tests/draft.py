from pytex import TeX, TeXJob


tex = '\\begin{center}\nText!\n\\end{center}'

doc = TeX(tex)
print(doc)
print(doc.source())