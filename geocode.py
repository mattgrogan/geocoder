'''
This is a simple script to geocode a list of
cities and store them in json form.
'''

import argparse
import json
import logging
import os
import sys
import time

from geopy.geocoders import GoogleV3


class City_Cache(object):
  """ This object holds a cache of cities already geocoded """

  def __init__(self):
    """ Initalize the cache with an empty dataset """

    # Initialize with an empty array
    self._data = {}

  def load(self, filename):
    """ Load the cache from filename """

    logging.debug("Loading data from %s" % filename)

    with open(filename, 'r') as input_file:
      self._data = json.load(input_file)

  def save(self, filename):
    """ Save the cache to filename """

    logging.debug("Saving to %s" % filename)

    with open(filename, 'w') as output_file:
      json.dump(self._data, output_file, sort_keys=True,
                indent=4, separators=(',', ": "))

  def add_city(self, city, delay=1):
    """ Add a city if it does not exist in the cache """

    # Trim whitespace
    city = city.strip()

    if city in self._data.keys():
      logging.debug("Found %s in cache" % city)
    else:
      logging.debug("Geocoding city %s..." % city)

      geolocator = GoogleV3(scheme="http")
      location = geolocator.geocode(city, exactly_one=True)

      city_data = {
          'city': city,
          'formatted_address': location.raw['formatted_address'],
          'latitude': location.latitude,
          'longitude': location.longitude
      }

      self._data[city] = city_data

      logging.debug("Finished geocoding %s" % city)

      # Throttle our usage of Google Geocoder
      time.sleep(delay)

if __name__ == "__main__":

  parser = argparse.ArgumentParser(
      description="A simple city geocoder"
  )

  parser.add_argument("input_file", help="Input file (text)")
  parser.add_argument("output_file", help="Output file (json)")
  parser.add_argument("-v", "--verbose", help="Verbose output",
                      action="store_true")

  args = parser.parse_args()

  if args.verbose:
    logging.basicConfig(level=logging.DEBUG)

  cache = City_Cache()

  # Load the cache from output file, if it exists
  if os.path.isfile(args.output_file):
    cache.load(args.output_file)

  with open(args.input_file, 'r') as input_file:
    cities = input_file.readlines()

  for city in cities:
    cache.add_city(city)

  cache.save(args.output_file)
