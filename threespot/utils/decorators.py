from functools import wraps

def annotate(**kwargs):
    """
    A decorator which annotates a function with properties specified in the key-
    word arguments.
    
    >>> @annotate(bar=123)
    ... def foo():
    ...     return True
    ... 
    >>> foo.bar
    123

    
    """
    def _wrapped_view_func(fn):
        for property, value in kwargs.items():
            setattr(fn, property, value)
        return fn
    return _wrapped_view_func

def return_json(view_func):
    """
    Decorator for a view function that sets the response's content-type 
    header to `application/json`.
    """
    def _wrapped_view_func(request, *args, **kwargs):
        response = view_func(request, *args, **kwargs)
        response['Content-Type'] = "application/json"
        return response
    return wraps(view_func)(_wrapped_view_func)
