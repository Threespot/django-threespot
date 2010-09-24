"""Geographical tools dealing with US zipcodes.

ZIPS is a dictionary of {5-digit-zip: (latitude, longitude)}

The zip codes are strings and latitude/longitude are in radians. 
"""

from threespot.geo.geo import distance_miles, Point

ZIPS = {}

def _load_zips(dict):
    """Load up the zips in a fast and memory light way.

    Tests indicated that loading the zips this way increased memory by about
    5Mb, as opposed to 80MB for generated python code.
    """
    import os
    from math import pi
    here = os.path.dirname(__file__)
    source = open(os.path.join(here, 'zipcode.data'), 'r')
    try:
        line = source.readline()
        while line:
            zip, lat, long = line.strip().split()
            # fix quadrant and convert to radians
            lat = (float(lat) * pi) / 180
            long = - (float(long) * pi) / 180
            ZIPS[zip] = (lat, long)
            line = source.readline()
    finally:
        source.close()

_load_zips(ZIPS)
del _load_zips

def zip_to_zip_miles(zip1, zip2):
    try:
        zip1 = ZIPS[zip1]
    except KeyError:
        raise ValueError(zip1)
    try:
        zip2 = ZIPS[zip2]
    except KeyError:
        raise ValueError(zip2)
    return distance_miles(Point(*zip1), Point(*zip2))

def distance_to_zip_miles(point, zip):
    """Distance between a point and a zip

    Distance from Nashville International Airport (BNA) in Nashville to Los 
    Angeles International Airport (LAX) in Los Angeles:

        >>> lax = Point.from_degrees(33.94, -118.40)
        >>> int(distance_to_zip_miles(lax, "37217"))
        1794
        >>> bna = Point.from_degrees(36.12, -86.67)
        >>> distance_to_zip_miles(bna, "37217") # doctest: +ELLIPSIS
        1.29...
    """
    try:
        zip = ZIPS[zip]
    except KeyError:
        raise ValueError(zip)
    return distance_miles(point, Point(*zip))

def valid_zip(zip):
    return zip in ZIPS
