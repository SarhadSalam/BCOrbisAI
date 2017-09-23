import functools

class memoized(object):
    '''Decorator. Caches a function's return value each time it is called.
    If called later with the same arguments, the cached value is returned
    (not reevaluated). Taken from https://wiki.python.org/moin/PythonDecoratorLibrary#Memoize
    '''

    def __init__(self, func):
        self.func = func
        self.cache = {}
        self.__doc__ = func.__doc__
        self.__repr__ = func.__repr__

    def __call__(self, *args):
        # if not isinstance(args, collections.Hashable):
        #     # uncacheable. a list, for instance.
        #     # better to not cache than blow up.
        #     return self.func(*args)
        if args in self.cache:
            return self.cache[args]
        else:
            value = self.func(*args)
            self.cache[args] = value
            return value

    def __get__(self, obj, objtype):
        '''Support instance methods.'''
        f = functools.partial(self.__call__, obj)
        f.__doc__ = self.func.__doc__
        f.__repr__ = self.func.__repr__
        return f

# Below functions are memoized because they are often called many times in large loops

@memoized
def add_points(p1, p2):
    """
    Adds two points together

    :param (int,int) p1: First point
    :param (int,int) p2: Second point
    :return: (p1.x + p2.x, p1.y + p2.y)
    :rtype: (int,int)
    """
    return tuple(map(lambda x, y: x + y, p1, p2))

@memoized
def sub_points(p1, p2):
    """
        Subtracts p2 from p1

        :param (int,int) p1: First point
        :param (int,int) p2: Second point
        :return: (p1.x - p2.x, p1.y - p2.y)
        :rtype: (int,int)
        """
    return tuple(map(lambda x, y: x - y, p1, p2))

@memoized
def mod_point(point, mod_tuple):
    """
    :param (int,int) point: (x,y) point
    :param (int,int) mod_tuple: modulo tuple
    :return: (point[0] % mod_tuple[0], point[1] % mod_tuple[1])
    :rtype: (int,int)
    """
    return tuple(map(lambda n, k: n % k, point, mod_tuple))

def mod_taxi_cab_distance(p1, p2, width, height):
    dx = get_smaller_mod_distance_on_line(p1[0], p2[0], width)
    dy = get_smaller_mod_distance_on_line(p1[1], p2[1], height)
    return dx + dy

def get_smaller_mod_distance_on_line(a, b, length):
    inner = abs(a-b)
    if a < b:
        smaller, bigger = a, b
    else:
        smaller, bigger = b, a
    outer = smaller + abs(length-bigger)
    if inner < outer: return inner
    return outer