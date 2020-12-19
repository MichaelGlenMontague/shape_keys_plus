def get(l, i, d=None):
    """Returns the value of `l[i]` if possible, otherwise `d`."""
    
    if l is None:
        return d
    
    if type(l) in (dict, set):
        return l[i] if i in l else d
    
    try:
        return l[i] if i >= 0 else d
    except (IndexError, KeyError, TypeError):
        return d


def loop(n, a, b):
    """Loops `n` between `a` and `b` (exclusive)."""
    return ((n - a) - ((b - a) * ((n - a) // (b - a)))) + a


def flatten(l):
    f = []
    
    if type(l) in (list, tuple):
        for v in l:
            f += flatten(v) if type(v) in (list, tuple) else [v]
    
    return f


def hide(obj):
    data = {
        'hidden': obj.hide_viewport,
        'selected': obj.select_get()
    }
    
    obj.hide_viewport = True
    
    return obj, data


def show(hidden):
    obj, data = hidden
    
    obj.hide_viewport = data['hidden']
    obj.select_set(data['selected'])
