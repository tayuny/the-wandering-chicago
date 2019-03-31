'''
Clean the data
'''
import re
import pandas as pd
import numpy as np
import googlemaps

FAMILY_SUPPORT = pd.read_csv(r"family_support.csv")
HEALTH_SERVICE = pd.read_excel(r"health_service.xlsx")
COMMUNITY = pd.read_csv(r"community.csv")
PARK = pd.read_csv(r"park.csv")
WARMING_CENTER = pd.read_csv(r'warming_center.csv')
COOLING_CENTER = pd.read_csv(r'cooling_center.csv')
SENIOR_CENTER = pd.read_csv(r'senior_center.csv')
CONDOM = pd.read_csv(r'condom.csv')
HEALTH_CLINIC = pd.read_csv(r'health_clinic.csv')

COL_LIST = ["facility_name", "address", "community_area",
            "phone_number", "zipcode", "operation_time",
            "longitude", "latitude", "x_coordinate",
            "y_coordinate", "service_type", "notes"]

RENAME_DICT = {'ADDITIONAL NOTES': 'notes', 'ADDRESS': 'address',
               'Address': 'address', 'Clinic Type': 'service_type',
               'Community Area': 'community_area',
               'Community Area (#)': 'community_area',
               'Division': 'service_type',
               'FACILITY_N': 'facilities',
               'FQHC, Look-alike, or Neither; Special Notes': 'notes',
               'Facility': 'facility_name',
               'HOURS OF OPERATION': 'operation_time',
               'Hours of Operation': 'operation_time', 'LOCATION': 'location',
               'Location':'location', 'Latitude': 'latitude',
               'Longitude': 'longitude', 'PARK': 'facility_name',
               'PHONE': 'phone_number', 'Phone': 'phone_number',
               'Phone 1': 'phone_number', 'Phone Number': 'phone_number',
               'Program Model': 'notes', 'SITE': 'facility_name',
               'Site Name': 'facility_name', 'Street Address': 'address',
               'X Coordinate': 'x_coordinate', 'X_COORD': 'longitude',
               'Y Coordinate': 'y_coordinate', 'Y_COORD': 'latitude',
               'ZIP': 'zipcode', 'ZIP Code': 'zipcode'}



def extract_lon_and_lat(df, col_name):
    '''
    Extract longitude and latitude of a data frame from a certain column
    Inputs:
        df: a data frame
        col_name: the name of the column that contains longitude and
          latitude information
    Outputs:
        add two new columns of longitude and latitude information
    '''
    df['latitude'] = df.apply(lambda x: re.search((r'(\d\d\.[0-9]+)(\,)'),\
                                                  x[col_name]).group(1)\
                                                  if not (x[col_name]\
                                                  is np.nan) else np.nan,\
                                                  axis=1)
    df['longitude'] = df.apply(lambda x: re.search((r'(\, )(-\d\d\.[0-9]+)'),\
                                                    x[col_name]).group(2)\
                                                    if not (x[col_name]\
                                                    is np.nan) else np.nan,\
                                                    axis=1)
    return df


def get_zipcode_address(df, col_name):
    '''
    Extract zip code and address of the data frame from a certain column
    Inputs:
        df: a data frame
        col_name: the name of the column that contains zipcode and address
          information
    Outputs:
        add two new columns of zipcode and address information
    '''
    if "zipcode" not in df.columns:
        df['zipcode'] = df.apply(lambda x: re.search(
            (r"([\w\s\.]+)([0-9]{5})(\n)"), x[col_name]).group(2), axis=1)
    df['address'] = df.apply(lambda x: re.search(
        (r"([\w\s\.]+)([0-9]{5})(\n)"), x[col_name]).group(1), axis=1)

    return df


def select_columns(df):
    '''
    The function is used to select the target columns, and add empty target
    columns which does not exist in the given data frame.
    Input:
        df: the filtered dataframe
    Returns:
        target df
    '''
    for col in df.columns:
        if col not in COL_LIST:
            df = df.drop(columns=[col])
    for target_col in COL_LIST:
        if target_col not in df.columns:
            df[target_col] = np.nan

    return df[COL_LIST]


def fill_in_facility(df):
    '''
    This function is used to find the collection of facilities in a park
    Input:
        df: the filtered dataframe
    Returns:
        df with collection of facilities (string in "notes" column)
    '''
    df["number"] = 1
    fac_table = df.pivot_table(index=["facility_name"],\
                               columns=["facilities"], values="number")
    fac_table["notes"] = ""
    fac_table["facilities"] = fac_table.index
    for fac_col in fac_table.columns[:-2]:
        fac_table.loc[fac_table[fac_col].notnull(), "notes"] +=\
                                                            (fac_col + "/  ")

    return fac_table[["facilities", "notes"]]


def get_coordiance(df):
    '''
    Get the latitude and longitude from an address through Google Map API
    Inputs:
        df: a data frame
    Ouputs:
        add two columns to the data frame and return the new data frame
    '''
    gmaps_key = googlemaps.Client(key=\
                                'AIzaSyABYmQbCm2aro_JDQkTV_Td96fvUA6g_nY')
    df['geocode_result'] = df.apply(lambda x: \
                                gmaps_key.geocode(x['address']), axis=1)
    df['latitude'] = df.apply(lambda x:\
                    x['geocode_result'][0]['geometry']['location']['lat']\
                    if x['geocode_result'] else None, axis=1)
    df['longitude'] = df.apply(lambda x:\
                    x['geocode_result'][0]['geometry']['location']['lng']\
                    if x['geocode_result'] else None, axis=1)
    df_cleaned = df.drop(columns=['geocode_result'])
    return df_cleaned


# For warming center
WARMING_CENTER['facility_name'] = WARMING_CENTER['SITE TYPE'] + " (" + \
                                  WARMING_CENTER['SITE NAME'] + ")"
WARMING_CENTER = WARMING_CENTER.rename(RENAME_DICT, axis='columns')
WARMING_CENTER = extract_lon_and_lat(WARMING_CENTER, 'location')
WARMING_CENTER = select_columns(WARMING_CENTER)
WARMING_CENTER['service_type'] = 'warming center'

# For cooling center
COOLING_CENTER['facility_name'] = COOLING_CENTER['SITE TYPE'] + " (" + \
                                  COOLING_CENTER['SITE NAME'] + ")"
COOLING_CENTER = COOLING_CENTER.rename(RENAME_DICT, axis='columns')
COOLING_CENTER = extract_lon_and_lat(COOLING_CENTER, 'location')
COOLING_CENTER = select_columns(COOLING_CENTER)
COOLING_CENTER['service_type'] = 'cooling center'

# For senior center
SENIOR_CENTER['facility_name'] = SENIOR_CENTER['PROGRAM'] + " (" + \
                                 SENIOR_CENTER['SITE NAME'] + ")"
SENIOR_CENTER = SENIOR_CENTER.rename(RENAME_DICT, axis='columns')
SENIOR_CENTER = extract_lon_and_lat(SENIOR_CENTER, 'location')
SENIOR_CENTER = select_columns(SENIOR_CENTER)
SENIOR_CENTER['service_type'] = 'senior center'

# For condom distribution site
CONDOM['facility_name'] = CONDOM['Name'] + " (" + CONDOM['Venue Type'] + ")"
CONDOM = CONDOM.rename(RENAME_DICT, axis="columns")
CONDOM = extract_lon_and_lat(CONDOM, 'location')
CONDOM = select_columns(CONDOM)
CONDOM['service_type'] = 'condom distribution site'

# For health clinic
HEALTH_CLINIC = HEALTH_CLINIC.rename(RENAME_DICT, axis=1)
HEALTH_CLINIC = select_columns(HEALTH_CLINIC)
HEALTH_CLINIC["operation_time"] = HEALTH_CLINIC.apply(lambda x: re.sub(\
    r"\¨C", "-", x["operation_time"]) if not (x["operation_time"]\
    is np.nan) else np.nan, axis=1)

# For family support
FAMILY_SUPPORT = FAMILY_SUPPORT.rename(RENAME_DICT, axis="columns")
FAMILY_SUPPORT = select_columns(FAMILY_SUPPORT)
FAMILY_SUPPORT["service_type"] = FAMILY_SUPPORT.apply(lambda x:\
    "family support (" + x["service_type"] + ")", axis=1)
FAMILY_SUPPORT = FAMILY_SUPPORT[FAMILY_SUPPORT["zipcode"].notnull()]
FAMILY_SUPPORT["zipcode"] = FAMILY_SUPPORT.apply(lambda x:\
                                        int(x["zipcode"]), axis=1)

# For health service
HEALTH_SERVICE = HEALTH_SERVICE.rename(RENAME_DICT, axis="columns")
HEALTH_SERVICE = extract_lon_and_lat(HEALTH_SERVICE, "address")
HEALTH_SERVICE = get_zipcode_address(HEALTH_SERVICE, "address")
HEALTH_SERVICE = select_columns(HEALTH_SERVICE)
HEALTH_SERVICE["service_type"] = "health service"

# For community service
COMMUNITY = COMMUNITY.rename(RENAME_DICT, axis="columns")
COMMUNITY = extract_lon_and_lat(COMMUNITY, "location")
COMMUNITY["service_type"] = "community service"
COMMUNITY = select_columns(COMMUNITY)

# For park
PARK = PARK.rename(RENAME_DICT, axis="columns")
FAC_TABLE = fill_in_facility(PARK).reset_index()
FAC_TABLE["longitude"] = 0
FAC_TABLE["latitude"] = 0
for fac_name in list(PARK["facility_name"].unique()):
    lon_lat = PARK.loc[PARK["facility_name"] == fac_name,\
                       ["longitude", "latitude"]].iloc[[0]]
    FAC_TABLE.loc[FAC_TABLE["facility_name"] == fac_name, "longitude"]\
                                      = lon_lat["longitude"].values[0]
    FAC_TABLE.loc[FAC_TABLE["facility_name"] == fac_name, "latitude"]\
                                      = lon_lat["latitude"].values[0]

FAC_TABLE["service_type"] = "park"
PARK = select_columns(FAC_TABLE)
FOOD_PANTRY = pd.read_csv("food_pantry.csv")
FOOD_PANTRY = get_coordiance(FOOD_PANTRY)
FOOD_PANTRY = select_columns(FOOD_PANTRY)
SHELTER = pd.read_csv("shelter.csv")
SHELTER = get_coordiance(SHELTER)
SHELTER = select_columns(SHELTER)

FULL_DATA = pd.concat([FAMILY_SUPPORT, HEALTH_SERVICE, COMMUNITY,\
                       PARK, WARMING_CENTER, COOLING_CENTER,\
                       SENIOR_CENTER, CONDOM, HEALTH_CLINIC,\
                       FOOD_PANTRY, SHELTER], join="inner").reset_index(\
                       drop=True)
FULL_DATA["service_type"] = FULL_DATA["service_type"].apply(\
                            lambda x: x.lower())
FULL_DATA.to_csv("full_data.csv")
