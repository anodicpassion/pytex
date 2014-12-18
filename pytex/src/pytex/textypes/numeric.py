import string

__all__ = ['number', 'count', 'dimen', 'mudimen', 'glue', 'muglue']

class number(int):
    """Class used for parameter and count values"""

    def __new__(cls, v):
        try:
            return v._count_()
        except AttributeError:
            return int.__new__(cls, v)

    @property
    def source(self):
        return str(self)

class count(number):
    """Class used for count values"""
    pass

class dimen(float):
    """Class used for dimen values"""

    units = ['pt', 'pc', 'in', 'bp', 'cm', 'mm', 'dd', 'cc', 'sp', 'ex', 'em']

    def __new__(cls, v):
        try:
            return v._dimen_()
        except AttributeError:
            pass

        if isinstance(v, str) and v[-1] in string.ascii_letters:
            # Get rid of glue components
            v = list(v.split('plus').pop(0).split('minus').pop(0).strip())
            units = []
            while v and v[-1] in string.ascii_letters:
                units.insert(0, v.pop())
            v = float(''.join(v))
            units = ''.join(units)
            if units == 'pt':
                v *= 65536
            elif units == 'pc':
                v *= 12 * 65536
            elif units == 'in':
                v *= 72.27 * 65536
            elif units == 'bp':
                v *= (72.27 * 65536) / 72
            elif units == 'cm':
                v *= (72.27 * 65536) / 2.54
            elif units == 'mm':
                v *= (72.27 * 65536) / 25.4
            elif units == 'dd':
                v *= (1238.0 * 65536) / 1157
            elif units == 'cc':
                v *= (1238.0 * 12 * 65536) / 1157
            elif units == 'sp':
                pass
            # Encode fil(ll)s by adding 2, 4, and 6 billion
            elif units == 'fil':
                if v < 0: v -= 2e9
                else: v += 2e9
            elif units == 'fill':
                if v < 0: v -= 4e9
                else: v += 4e9
            elif units == 'filll':
                if v < 0: v -= 6e9
                else: v += 6e9
            elif units == 'm':
                pass
            # Just estimates, since I don't know the actual font size
            elif units == 'ex':
                v *= 5 * 65536
            elif units == 'em':
                v *= 11 * 65536
            else:
                raise ValueError('Unrecognized units: %s' % units)
        return float.__new__(cls, v)

    @property
    def source(self):
        sign = 1
        if self < 0:
            sign = -1
        if abs(self) >= 6e9:
            return str(sign * (abs(self) - 6e9)) + 'filll'
        elif abs(self) >= 4e9:
            return str(sign * (abs(self) - 4e9)) + 'fill'
        elif abs(self) >= 2e9:
            return str(sign * (abs(self) - 2e9)) + 'fil'
        else:
            return '%spt' % self.pt

    @property
    def pt(self):
        return self / 65536
    point = pt

    @property
    def pc(self):
        return self / (12 * 65536)
    pica = pc

    @property
    def in_(self):
        return self / (72.27 * 65536)
    inch = in_

    @property
    def bp(self):
        return self / ((72.27 * 65536) / 72)
    bigpoint = bp

    @property
    def cm(self):
        return self / ((72.27 * 65536) / 2.54)
    centimeter = cm

    @property
    def mm(self):
        return self / ((72.27 * 65536) / 25.4)
    millimeter = mm

    @property
    def dd(self):
        return self / ((1238 * 65536) / 1157)
    didotpoint = dd

    @property
    def cc(self):
        return self / ((1238 * 12 * 65536) / 1157)
    cicero = cc

    @property
    def sp(self):
        return self
    scaledpoint = sp

    @property
    def ex(self):
        return self / (5 * 65536)
    xheight = ex

    @property
    def em(self):
        return self / (11 * 65536)
    mwidth = em

    @property
    def fill(self):
        sign = 1
        if self < 0:
            sign = -1
        if abs(self) >= 6e9:
            return sign * (abs(self) - 6e9)
        elif abs(self) >= 4e9:
            return sign * (abs(self) - 4e9)
        elif abs(self) >= 2e9:
            return sign * (abs(self) - 2e9)
        else:
            raise ValueError('This is not a fil(ll) dimension')
    fil = filll = fill

    def __repr__(self):
        return self.source

    def __str__(self):
        return self.source

class mudimen(dimen):
    """ Class used for mudimen values """

    units = ['m']

class glue(dimen):
    """ Class used for glue values """

    def __new__(cls, g, plus=None, minus=None):
        return dimen.__new__(cls, g)

    def __init__(self, g, plus=None, minus=None):
        self.stretch = self.shrink = None
        if plus is not None:
            self.stretch = dimen(plus)
        if minus is not None:
            self.shrink = dimen(minus)

    @property
    def source(self):
        s = [dimen(self).source]
        if self.stretch is not None:
            s.append('plus')
            s.append(self.stretch.source)
        if self.shrink is not None:
            s.append('minus')
            s.append(self.shrink.source)
        return ' '.join(s)

class muglue(glue):
    """ Class used for muglue values """

    units = ['m']
