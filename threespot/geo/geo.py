from math import *

GREAT_CIRCLE_MILES = 3959.873

class Point:

    def __init__(self, lat, long):
        self.latitude = lat
        assert - pi/2 <= lat <= pi/2, (
            "Latitude must be in radians and between -pi/2 and pi/2"
        )
        self.longitude = long
        assert - pi <= lat <= pi, (
            "Latitude must be in radians and between -pi and pi"
        )

    @classmethod
    def from_degrees(cls, lat, long):
        return cls((lat*pi)/180, (long*pi)/180)


def distance_angular(point1, point2):
    assert isinstance(point1, Point)
    assert isinstance(point2, Point)
    delta_long = point1.longitude - point2.longitude
    cos_delta_long = cos(delta_long)
    sin_delta_long = sin(delta_long)
    cos_lat_1 = cos(point1.latitude)
    sin_lat_1 = sin(point1.latitude)
    cos_lat_2 = cos(point2.latitude)
    sin_lat_2 = sin(point2.latitude)
    numerator = sqrt((cos_lat_2*sin_delta_long)**2 + \
        (cos_lat_1*sin_lat_2 - sin_lat_1*cos_lat_2*cos_delta_long)**2)
    denominator = sin_lat_1*sin_lat_2 + cos_lat_1*cos_lat_2*cos_delta_long
    return atan2(numerator, denominator)

def distance_miles(point1, point2):
    """
    Distance from Nashville International Airport (BNA) in Nashville to Los
    Angeles International Airport (LAX) in Los Angeles:

        >>> p1 = Point.from_degrees(36.12, -86.67)
        >>> p2 = Point.from_degrees(33.94, -118.40)
        >>> int(distance_miles(p1, p2))
        1794
    """
    return GREAT_CIRCLE_MILES * distance_angular(point1, point2)
