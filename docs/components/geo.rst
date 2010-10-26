Geographic Helpers
====================

The ``countries`` module
--------------------------

A list of the country names (official short names in English) in 
alphabetical order as given in ISO 3166-1 and the corresponding 
ISO 3166-1-alpha-2 code elements.

To use::

    >>> from threespot.geo import countries
    >>> countries[2]
    ("al", u"Albania")

This is useful when you need a choice field in a Django model that includes all countries::

    from django.db import models
    
    class Person(models.Model):
        name = models.CharField(max_length=255)
        country = models.CharField(max_length=2, choices=countries)

The ``geo`` module
---------------------

Calculate distances between points on the globe. For example, say you want to calculate the Distance from Nashville International Airport (BNA) in Nashville to the Los Angeles International Airport (LAX) in Los Angeles:

    >>> from threespot.geo import geo
    >>> p1 = geo.Point.from_degrees(36.12, -86.67)
    >>> p2 = geo.Point.from_degrees(33.94, -118.40)
    >>> int(geo.distance_miles(p1, p2))
    1794

The ``zipcode`` module
------------------------

Geographical tools dealing with US zipcodes. 

To find the lat/long coordinates of a zipcode::

    >>> from threespot.geo import zipcode
    >>> zipcode.ZIPS[00605]
    (18.428801, 67.153503)

To find the distance in miles between two zipcodes::

    >>> int(zipcode.zip_to_zip_miles(21211, 23233))
    126

To find the distance between a zipcode and any arbitrary lat/long coordinate::

    >>> from threespot.geo import geo, zipcode
    >>> lax = Point.from_degrees(33.94, -118.40)
    >>> int(distance_to_zip_miles(lax, "37217"))
    1794