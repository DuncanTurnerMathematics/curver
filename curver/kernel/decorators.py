
''' A module for decorators. '''

import inspect
from decorator import decorator

@decorator
def memoize(function, *args, **kwargs):
    ''' A decorator that memoizes a method of a class. '''
    
    inputs = inspect.getcallargs(function, *args, **kwargs)  # pylint: disable=deprecated-method
    self = inputs['self']
    
    if function.__name__ == '__hash__':
        # We have to handle the __hash__ method differently since it is used in the other block of code.
        if not hasattr(self, '_hash'):
            self._hash = function(*args, **kwargs)
        return self._hash
    else:
        if not hasattr(self, '_cache'):
            self._cache = dict()
        key = (function.__name__, frozenset(inputs.items()))
        if key not in self._cache:
            self._cache[key] = function(*args, **kwargs)
        return self._cache[key]

def topological_invariant(function):
    ''' Mark this function as a topological invariant.
    
    This is allows it to be picked out by the TopologicalInvariant unittests. '''
    
    function.topological_invariant = True
    return function

def ensure(*fs):
    ''' A decorator that specifies properties that the result of a functions should have. '''
    @decorator
    def wrapper(function, *args, **kwargs):
        ''' A decorator that checks that the result of a function has properties fs. '''
        
        result = function(*args, **kwargs)
        data = type('data', (), inspect.getcallargs(function, *args, **kwargs))  # pylint: disable=deprecated-method
        data.result = result
        
        for f in fs:
            assert f(data)
        return result
    
    return wrapper

def decorate_all(function):
    ''' A decorator that applies a function, most likely another decorator, to all public methods of a class. '''
    def decorate(cls):
        ''' A class decorator that applies the given function to every public method. '''
        
        for attr, method in inspect.getmembers(cls):  # there's propably a better way to do this
            if not attr.startswith('_') and inspect.isfunction(method):
                setattr(cls, attr, function(method))
        return cls
    return decorate

