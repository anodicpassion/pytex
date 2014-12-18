import abc

class RFile(abc.ABC):
    '''Defines a minimal read-only file interface in order to check if an 
    object should be regarded as a File or as a list of tokens in the 
    initialization of a Tokenizer'''

    @abc.abstractmethod
    def read(self, n=None):
        pass

    @abc.abstractmethod
    def tell(self):
        pass

    @abc.abstractmethod
    def seek(self, pos):
        pass
