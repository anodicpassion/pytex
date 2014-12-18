import nose
from nose.tools import eq_, raises
from alttex.template import Template

def template(src, values=None):
    'Return a list of alternatives in the given section'
    return Template(src).render()

if __name__ == '__main__':
    nose.main()
