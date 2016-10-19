# -*- coding: utf-8 -*-

import pickle
import json
import string
import urllib2
from bs4 import BeautifulSoup


def prepare_geojson_cities():
    print("input 'scrape' to re-scrape data from Natural Resources Canada.")
    print("hit any other key to go straight to geojson generation.")
    move = raw_input(">").lower().split()
    if len(move) and move[0] == "scrape":
        known_cities = scrape_cities()
        save_cities(known_cities)
    else:
        known_cities = restore_cities()

    add_coordinates(known_cities)
    persist_cities(known_cities)

def scrape_cities():
    known_cities = {}
    uri_pattern = "http://planthardiness.gc.ca/index.pl?m=22&lang=fr&prov=Quebec&val=%s"
    for letter in  list(string.ascii_lowercase):
        page = urllib2.urlopen(uri_pattern % letter).read()
        soup = BeautifulSoup(page, 'lxml')
        for i in soup.find_all('table'):
            for tr in i.find_all('tr'):
                tds = tr.find_all('td')
                city_name = tds[0].text.encode("utf-8")
                known_cities[city_name] = [tds[2].text, tds[4].text]
    return known_cities


def save_cities(obj, filename='cities.pk1'):
    with open(filename, 'wb') as output:
        pickle.dump(obj, output, pickle.HIGHEST_PROTOCOL)

def restore_cities():
    with open('cities.pk1', 'rb') as input:
        return pickle.load(input)

def add_coordinates(known_cities):
    try:
        with open('../static/CA.txt') as f:
            for line in f:
                x = y = 0
                split_line_tab = line.split("\t")
                if len(split_line_tab) == 1:
                    columns  = line.split()
                else:
                    columns = split_line_tab

                city_name = columns[1]
                for col in [3,4,5,6]:
                    try:
                        x = float(columns[col])
                        y = float(columns[col+1])
                        break
                    except ValueError:
                        pass

                if(city_name == "Hébertville"):
                    print("%s | X: %s | Y: %s" % (city_name, x, y))

                if known_cities.has_key(city_name):
                    #print("%s | X: %s | Y: %s" % (city_name, x, y))
                    known_cities[city_name].append((x,y))
    except IOError:
        import os
        print(os.getcwd())
    finally:
        f.close()

def persist_cities(known_cities):
    geojson_cities = []

    for city_name in known_cities:
        c = known_cities[city_name]
        zone = c[0]
        rusticity = c[1]
        if(len(c) > 2 and len(c[2]) == 2):
            geojson_cities.append(get_geojson_city(city_name, c[0], c[1], c[2][0], c[2][1]))
        else:
            print("%s has no x,y data: %s" % (city_name, c))

    with open('../static/cities_raw.geojson', 'w') as f:
        json.dump(geojson_cities, f)

def get_geojson_city(name, zone, rusticity, x, y):
    return {
      "type": "Feature",
      "geometry": {
        "type": "Point",
        "coordinates": [x, y]
      },
      "properties": {
        "name": name,
        "rusticity": rusticity,
        "popupContent": zone
      }
    }


prepare_geojson_cities()
