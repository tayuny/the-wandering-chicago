'''
Main code for finding the nearest target spots and
export an webpage
'''
import os
import webbrowser
import pandas as pd
import util
import gmplot


COLOR_MAP = {'family support (children services)': '#FFFACD',
             'family support (senior services)':'#FFFACD',
             'family support (domestic violence)':'#FFFACD',
             'family support (homeless services)':'#FFFACD',
             'family support (human services delivery)':'#FFFACD',
             'family support (workforce services)':'#FFFACD',
             'family support (youth services)':'#FFFACD',
             'health service':'#87CEFA',
             'senior center':'#FFFACD',
             'community service':'#FFFACD',
             'park':'#8FBC8F',
             'warming center':'#DC143C',
             'cooling center':'#4169E1',
             'condom distribution site':'#87CEFA',
             'mental health clinic':'#87CEFA',
             'sti specialty clinic':'#87CEFA',
             'wic clinic':'#87CEFA',
             'food pantry':'#FFD700',
             'shelter':'#FFA500'}

COL_TYPES = {'facility_name':str, 'address':str, 'community_area':str,
             'phone_number':str, 'zipcode':str, 'operation_time':str,
             'longitude':float, 'latitude':float, 'x_coordinate':float,
             'y_coordinate':float, 'service_type':str, 'notes':str}


def compute_distance(df, address, categories=None, walking_time=None):
    '''
    Compute the distance between user's location and all the facilities in
    our dataset
    Inputs:
        df: the full dataframe
        address:(str) address of user
        categories: (list of strings) the list of attempted service types
        walking_time: (int) the desired maximum walking time
    Returns:
        the new data frame
    '''
    user_lon, user_lat = util.get_user_location(address)
    df = util.select_categories(df, categories)
    df = df[df["longitude"].notnull() & df["latitude"].notnull()]
    df['distance'] = df.apply(lambda x: util.haversine(x['longitude'],\
      x['latitude'], user_lon, user_lat), axis=1)
    if walking_time is not None:
        df['walking_time'] = df.apply(lambda x: util.compute_walking_time(\
                                      x['distance']), axis=1)
        filter_cond = df['walking_time'] <= walking_time
        df = df[filter_cond]

    return df


def get_nearest_spots(df, address, categories=None, walking_time=None,
                      full_info=False):
    '''
    Get the spots that satisfies user's demands
    Inputs:
        df: the full dataframe
        address:(str) address of user
        categories: (list of strings) the list of attempted service types
        walking_time: (int) the desired maximum walking time
        full_info: (boolean) whether or not to return the full information
    Returns: dataframe with nearest spots of each selected category
    '''
    df = compute_distance(df, address, categories, walking_time)
    nearest_df = pd.DataFrame(columns=df.columns)
    coordinate_dict = {}

    for category in df["service_type"].unique():
        current_df = df[df["service_type"] == category].sort_values(by=["distance"]).iloc[:30]
        current_df = current_df.drop_duplicates("facility_name", keep="first")
        nearest_df = pd.concat([nearest_df, current_df.iloc[:3]], join="inner")
    nearest_df["coordinates"] = nearest_df.apply(\
      lambda x: tuple([x['latitude'], x['longitude']]), axis=1)

    for category in nearest_df["service_type"].unique():
        coordinate_dict[category] = list(nearest_df[\
          nearest_df["service_type"] == category]["coordinates"])

    if full_info:
        difference_col = ['longitude', 'latitude', 'x_coordinate',
                          'y_coordinate', 'coordinates']
    else:
        difference_col = ['longitude', 'latitude', 'x_coordinate',
                          'y_coordinate', 'coordinates', 'notes']

    return nearest_df.drop(difference_col, axis=1), coordinate_dict


def map_plot(address, dict_of_geocode):
    '''
    Plotting the location of facilities on a google map
    Inputs:
        user_location: the latitude and longitude of user
        dict_of_geocode:(dict) the dictionary mapping categories to list of geocodes
    Ouputs:
       Pop up the html of google map
    '''
    user_location = util.get_user_location(address)
    user_lon, user_lat = user_location
    gmap = gmplot.GoogleMapPlotter(user_lat, user_lon, 14)
    gmap.coloricon = "http://www.googlemapsmarkers.com/v1/%s/"
    for cat, geocodes in dict_of_geocode.items():
        facility_lats, facility_lons = zip(*geocodes)
        color = COLOR_MAP[cat]
        gmap.scatter(facility_lats, facility_lons, color, size=60, marker=True)
    gmap.marker(user_lat, user_lon, '#000000', title='User Location')
    gmap.draw("my_map.html")
    util.insert_apikey("my_map.html", 'AIzaSyBu5c2MH9Rj8tPzYmr14VC87Jp3xY-estc')
    return "my_map.html"


def export_output(df, map_url, address):
    '''
    Given the dataframe that is filtered, then output the html
    representing the dataframe and its corresponding points in map.
    Inputs:
        df: the filtered dataframe
        address:(str) address of user
        map_url: html representing the points corresponding to the
          facilities in map
    '''
    filename = 'output.html'
    cur_path = os.getcwd()
    html = util.generate_html(df, map_url, address)
    body = '\r\n\n<br>'.join(html)
    html_output = open(filename, 'w')
    html_output.write(body)
    file_path = 'file://' + cur_path + '/' + filename
    webbrowser.open(file_path)


def go(filename, address, categories=None, walking_time=None,
       full_info=False):
    '''
    Process the raw data and run the whole program.
    Inputs:
        filename: (str) filename of the data
        address:(str) address of user
        categories: (list of strings) the list of attempted service types
        walking_time: (int) the desired maximum walking time
        full_info: (boolean) whether or not to return the full information
    '''
    try:
        pd.options.display.max_colwidth = 650
        df = pd.read_csv(filename, dtype=COL_TYPES, index_col=0)
    except IOError:
        print("Could not read file: {}".format(filename))
    assert util.check_value(address, categories, walking_time, full_info) \
                                                    is True, 'Value Error!'

    df, dict_of_geocode = get_nearest_spots(\
      df, address, categories, walking_time, full_info)
    map_url = map_plot(address, dict_of_geocode)
    export_output(df, map_url, address)
