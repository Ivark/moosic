__author__ = 'ivar'

def every(collection, test):
    for item in collection:
        if not test(item): return False
    return True

def any(collection, test):
    for item in collection:
        if test(item): return True
    return False

def clamp(lower, value, upper):
    return lower if value < lower else value if value < upper else upper
