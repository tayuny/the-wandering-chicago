"""
crawler code
"""
import csv
import re
import json
import bs4
import requests


START_URL_FP = "https://www.foodpantries.org/ci/il-chicago"
START_URL_S = ("https://www.homelessshelterdirectory.org/cgi-bin"
                "/id/city.cgi?city=Chicago&state=IL")
STR_TO_REPLACE = ['\r', '\n', '\t', '<b>', '<br>', '</b>', '@', '\\',\
                        'â', '\x80', '\x99s', '\xa0', '[read more]']



def generate_soup(url):
    '''
    Given a url, then generate relevant soup object.
    Input:
        url: (str) url of a page
    Return:
        soup object
    '''
    response = requests.get(url)
    html = response.text

    return bs4.BeautifulSoup(html, "html.parser")


def crawl_food_pantry(output):
    '''
    Crawl the websites of food pantries and extract relevant information.
    Input:
        output: (str) filename of the file storing data extracted
          from websites
    '''
    start_soup = generate_soup(START_URL_FP)
    pantries = generate_dict_per_pantry(start_soup)

    with open(output, 'w') as file:
        colnames = ['facility_name', 'address', \
                    'phone_number', 'zipcode', 'service_type', 'notes']
        writer = csv.writer(file)
        writer.writerow(colnames)
        for p in pantries:
            p_address = p['address']
            row = [p['name'], p_address['streetAddress'], p['telephone'], \
                    p_address['postalCode'], 'food pantry', p['description']]
            writer.writerow(row)


def generate_dict_per_pantry(soup):
    '''
    Given the soup object of main page, then generate a list of dictionary
    for every food pantry.
    Input:
        soup: (object) soup of main page
    Return:
        list of dictionaries of food pantries
    '''
    pantries = []
    pantries_html = soup.find_all('script', type='application/ld+json')
    for ph in pantries_html:
        pantry_text = ph.text
        for s in STR_TO_REPLACE:
            pantry_text = pantry_text.replace(s, '')
        pantry = json.loads(pantry_text)
        if pantry['type'] == 'LocalBusiness':
            pantries.append(pantry)

    return pantries


def crawl_shelter(output):
    '''
    Crawl the websites of shelters and extract relevant information.
    Input:
        output: (str) filename of the file storing data extracted
          from websites
    '''
    start_soup = generate_soup(START_URL_S)
    shelters = generate_dict_per_shelter(start_soup)

    with open(output, 'w') as file:
        colnames = ['facility_name', 'address', 'phone_number', \
                                   'zipcode', 'service_type', 'notes']
        writer = csv.writer(file)
        writer.writerow(colnames)
        for s in shelters:
            row = [s['name'], s['address'], s['phone_number'], \
                                s['zipcode'], 'shelter', s['website']]
            writer.writerow(row)


def generate_dict_per_shelter(soup):
    '''
    Given the soup object of main page, then generate a list of dictionary
    for every shelter.
    Input:
        soup: (object) soup of main page
    Return:
        list of dictionaries of shelters
    '''
    shelters = []
    shelter_html = soup.find_all('div', class_='item_content')
    for sh in shelter_html:
        shelter = {'website': ''}
        if sh.find('a', href=True):
            url = sh.find('a', href=True)['href']
            if 'shelter=' in url:
                url_soup = generate_soup(url)
                shelter['name'] = re.findall('.*(?=\s-)', \
                        url_soup.find('h3', class_ = 'entry_title').text)[0]
                contact = url_soup.find('h4').next_sibling.next_sibling.text
                for s in STR_TO_REPLACE:
                    contact = contact.replace(s, '')
                contact = contact.strip().split(":")
                shelter['address'] = re.findall('.*(?=\s{5})', \
                                                    contact[0])[0].strip()
                shelter['zipcode'] = re.findall('\d{5}', \
                                                    contact[0])[0].strip()
                shelter['phone_number'] = contact[1].strip()
                for i in contact:
                    if "www" in i or ".com" in i or "org" in i:
                        shelter['website'] = i.strip('/')
                shelters.append(shelter)

    return shelters


if __name__ == '__main__':
    crawl_food_pantry('food_pantry.csv')
    crawl_shelter('shelter.csv')
