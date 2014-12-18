class LaTeXError(Exception):
    pass

class LaTeXEOFError(EOFError, Exception):
    pass


class LaTeXSyntaxError(SyntaxError, LaTeXError):
    '''Base class for reporting errors in the LaTeX syntax'''
    pass

class MissingTokenError(LaTeXSyntaxError):
    def __init__(self, tok, tok_expected, tokenizer):
        self.tok = tok
        self.tok_expected = tok_expected
        self.tokenizer = tokenizer

        # Get line number and character number to be reported
        lineno = tokenizer.get_lineno()
        charno = tokenizer.get_charno()

        # Create user message
        self.msg = msg = ['error around line %s, char %s' % (lineno, charno),
            'I was expecting %s, but got %s' % (self.report_expected(), self.report_tok()),
            '-' * 80]

        print(repr(tokenizer.source))
        print('*' * 80)
        print(self.tokenizer.source[:tokenizer._pos])
        print(list(range(max(0, lineno - 3), lineno + 1)), lineno)
        lines = [ tokenizer.get_line(i) for i in range(max(0, lineno - 3), lineno + 1) ]
        lines.append(' ' * max(0, charno - 1) + '^^^')  # highlight error
        if len(lines) > 2:
            lines.insert(0, '...')
        self.msg.extend(lines)
        self.msg = '\n'.join(msg)

        super(MissingTokenError, self).__init__(self.msg)

    def report_expected(self):
        return repr(self.tok_expected)

    def report_tok(self):
        return repr(self.tok) + str(type(self.tok))

class LaTeXEnvironmentError(LaTeXError):
    pass

class DocumentEnvError(LaTeXEnvironmentError):
    pass

class LaTeXArgError(LaTeXError, ValueError):
    pass

class InvalidCharError(LaTeXError):
    pass

class PackageImportError(LaTeXError):
    pass
