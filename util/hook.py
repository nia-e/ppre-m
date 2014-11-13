
import functools
import operator


class Result(object):
    def __init__(self, value):
        self.value = value


def patch_magic(func):
    """Fixes an issue with new-style classes not invoking the object's
    magics, but rather calling the original class's magic.

    This issue exists in Python > 2.2

    >>> class MyObject(object):
    >>>     def __setattr__(name, value):
    >>>         print('SET 1')
    >>>         object.__setattr__(self, name, value)
    >>> def setattr2(name, value):
    >>>     print('SET 2')
    >>> obj = MyObject()
    >>> obj.__setattr__ = blah_setattr  # Result printed is not relevant.
    'SET 1'
    >>> obj.a = 5  # Expecting 'SET 2'
    'SET 1'

    The reason is that type(obj).__setattr__ is used instead of
    obj.__setattr__ (which is still the case in old style classes).
    We can correct this by telling type(obj).__setattr__ to look up the
    object's __setattr__ if there is one set and invoke that instead.
    """
    try:
        if func.__name__[:2] != '__':
            # Only applies to magics. This will raise in some cases. Skip
            # those too.
            return
        # Get the original function
        inv_func = getattr(func.__self__.__class__, func.__name__)
        if hasattr(inv_func, '_patched_magic'):
            # If already patched, return. This patch is good for everything.
            return

        def passer(self, *args, **kwargs):
            try:
                func_ = self.__dict__[func.__name__]
            except KeyError:
                func_ = inv_func.__get__(self)
            return func_(*args, **kwargs)
        # TODO: Add docstring, func name, etc. to passer?
        passer._patched_magic = True
        setattr(func.__self__.__class__, func.__name__, passer)
    except:
        return


def multi_call(func):
    _calls = [(func, 5)]

    @functools.wraps(func)
    def func(*args, **kwargs):
        res = Result(None)
        print(args, kwargs)
        for callback, priority in func._calls:
            res = callback(res, *args, **kwargs)
        return res.value
    func._calls = _calls
    func.add_call = lambda callback, priority=10: add_call(func, callback,
                                                           priority)
    return func


def multi_call_patch(func):
    """If a function is not set up to handle res, create a function around
    it that sets res automatically"""

    try:
        func._calls
        return func
    except:
        pass
    patch_magic(func)

    def wrapped(res, *args, **kwargs):
        res.value = func(*args, **kwargs)
        return res
    return multi_call(wrapped)


def add_call(func, callback, priority=10):
    func._calls.append((callback, priority))
    func._calls.sort(key=operator.itemgetter(1))
