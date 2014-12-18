#===============================================================================
# Answer and automatic creation of distractors
#===============================================================================
# TODO: define this API and see how it should work with different answer types

class Answers(list):
    last = None

    def __init__(self):
        super(Answers, self).__init__()
        Answers.last = self
        self.has_distractor = False

    def append(self, obj):
        if self.has_distractor:
            raise ValueError('cannot append answer after yielding a distractor')
        if obj in self:
            raise AssertionError
        else:
            super(Answers, self).append(obj)

    def append_distractor(self):
        self.has_distractor = True
        if not self:
            super(Answers, self).append(0)

        while True:
            if 0.5 > _random.random():
                ans1, ans2 = oneof(self), oneof(self)
                new = (ans1 + ans2) / 2
            elif 0.5 > _random.random():
                ans1, ans2 = oneof(self), oneof(self)
                new = (ans1 + ans2) / 2 + oneof(1, 2)
            else:
                new = oneof(self) + oneof(1, -1, 2, -2, 3, -3)
            if new not in self:
                super(Answers, self).append(new)
                break

def answer(obj, clear=False):
    '''Marks object as a unique answer.'''

    if clear:
        Answers.last = None

    if Answers.last is None:
        ans = Answers()
    else:
        ans = Answers.last
    ans.append(obj)
    return obj

def distractor():
    '''Creates a distractor from the current set of answers.'''

    Answers.last.append_distractor()
    return Answers.last[-1]


if __name__ == '__main__':
    import doctest
    doctest.testmod()
