def chunk(iterable, size):
    """
    Group iterable into chunks of the given size.
    
    >>> chunks = chunk(range(1,10), 3)
    >>> list(chunks)
    [[1, 2, 3], [4, 5, 6], [7, 8, 9]]
    
    """
    for i in xrange(0, len(iterable), size):
        yield iterable[i:i+size]