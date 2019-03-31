"""
utility code
"""
import re
from math import radians, cos, sin, asin, sqrt, ceil
import bs4
from geopy.geocoders import Nominatim


# Part 1: helper functions for computing distance and get nearest spots
def select_categories(df, categories=None):
    '''
    Check whether the categories given by user is in the data frame columns
    Inputs:
        df: the full dataframe
        categories: (list of strings) the list of attempted service types
    Returns: dataframe which only contained the selected categories
    '''
    if not categories:
        return df

    available_col = set()
    for category in categories:
        if category in df["service_type"].unique():
            available_col.add(category)
    if available_col:
        df = df[df["service_type"].isin(available_col)]

    return df


# Compute distance

####################################################
# Source: PA #5 from Computer Science with
#         Applications 2 (CAPP 30122 Winter 2019) of
#         The University of Chicago
# Author: Instructors
# Date: 2019
####################################################
def haversine(lon1, lat1, lon2, lat2):
    '''
    Calculate the circle distance between two points
    on the earth (specified in decimal degrees)
    '''
    # convert decimal degrees to radians
    lon1, lat1, lon2, lat2 = map(radians, [lon1, lat1, lon2, lat2])

    # haversine formula
    dlon = lon2 - lon1
    dlat = lat2 - lat1
    a = sin(dlat / 2)**2 + cos(lat1) * cos(lat2) * sin(dlon / 2)**2
    c = 2 * asin(sqrt(a))

    # 6367 km is the radius of the Earth
    km = 6367 * c
    m = km * 1000
    return m


def compute_walking_time(distance):
    '''
    Converts the output of the haversine formula to walking time in minutes
    '''
    # adjusted downwards to account for manhattan distance
    walk_speed_m_per_sec = 1.1
    mins = distance / (walk_speed_m_per_sec * 60)

    return int(ceil(mins))


def get_user_location(address):
    '''
    Generates the user location class by taking address.
    Inputs:
        address:(str) address of user
    Returns:
        a object representing the user location
    '''
    geolocator = Nominatim(user_agent="The Wandering Chicago")
    location = geolocator.geocode(address)
    return (location.longitude, location.latitude)



# Part 2: helper fucntions for map plotting
####################################################
# Source: Solution for gmplot MissingKeyMapError
#        (issue 16 on Github)
# Author: santoshphilip and Leocorp
# Date: 2017
####################################################
def insert_apikey(file_name, apikey):
    """
    put the google api key in a html file
    Inputs:
        file_name:(str) the html to insert api key
        apikey:(str) the api key
    Output:
        modify the html
    """
    html_txt = open(file_name, 'r').read()
    soup = put_key(html_txt, apikey)
    new_txt = soup.prettify()
    open(file_name, 'w').write(new_txt)


def put_key(html_txt, apikey):
    """
    put the apikey in the htmltxt and return soup
    Inputs:
        html_txt:(str) the contents of html
        apikey: the Google Map JavaScript API
    Returns:
        the soup of this html
    """
    apistring = ("https://maps.googleapis.com/maps/api/js?"
                 "key=%s&callback=initialize&libraries=visualization"
                 "&sensor=true_or_false")
    soup = bs4.BeautifulSoup(html_txt, 'html.parser')
    soup.script.decompose() #remove the existing script tag
    body = soup.body
    src = apistring % (apikey,)
    tscript = soup.new_tag("script", src=src)
    body.insert(-1, tscript)
    return soup


# Part 3:helper function for export dataframe
def generate_html(df, map_url, address):
    '''
    Given the dataframe that is filtered, and generate the html
    representing the dataframe and its corresponding points in map.
    Inputs:
        df: the filtered dataframe
        address:(str) address of user
        map_url: html representing the points corresponding to the
          facilities in map
    Returns:
        html representing the dataframe and its points in map
    '''
    df_html_output = df.to_html(na_rep="", index=False)
    df_html_output = df_html_output.replace('right;">', 'center;">')\
        .replace('<th>', '<th style = "background-color: rgb(188, 198, 214)">')
    header = '<h1><font size="6" face="arial" \
                color="maroon">The Wandering Chicago</font></h1>'
    uesr_adrs = '<p><font size="4" face="arial" \
                color="black">User\'s Address: </font></p>'
    url_to_map = '<p><font size="5" face="arial" \
                color="grey">Click <a href="my_map.html">here</a> to see the \
                locations on Google Maps.</font></p>'
    uesr_adrs = re.sub(r'(?<=: ).*(?=<)', address, uesr_adrs)
    url_to_map = re.sub(r'(?<=href=").*(?=")', map_url, url_to_map)
    html = [header, uesr_adrs]
    html.append(df_html_output)
    html.append(url_to_map)

    return html


# Part 4 helper function for checking value before running whole system
def check_value(address, categories=None, walking_time=None, full_info=False):
    '''
    Inputs:
        address:(str) address of user
        categories: (list of strings) the list of attempted service types
        walking_time: (int) the desired maximum walking time
        full_info: (boolean) whether or not to return the full information
    Returns:
        boolean
    '''
    if not isinstance(address, (str, type(None))) \
        or not isinstance(categories, (list, type(None)))\
        or not isinstance(walking_time, (int, type(None)))\
        or not isinstance(full_info, bool):
        return False
    return True
