# Introduction to the Wandering Chicago Project
Final Project for CAPP30122 Computer Science with Applications II (Winter 2019)
 
Ta-Yun Yang, Xuan Bu, Yuwei Zhang

## Contents
 * [Project overview](#project-overview)
 * [Dependencies](#dependencies)
 * [Data](#data)
 * [Pipelines](#pipelines)
 * [User Guide](#user-guide)
 * [Reference](#reference)
 * [License](#license)
 * [Acknowledgement](#acknowledgement)


## Project Overview
Many cities in the U.S. spare no efforts to handle the issue of homelessness by providing a variety of relevant services, including Chicago. However, information of those services is scattered among governmental departments, private agencies(eg. charity churches), and web mapping provider (eg. Google). To maximize the effects of existing services and technologies, our project focuses on narrowing the informational gap between homeless people and service providers.

We aim to develop a recommendation system which is used to integrate accessible resources for homeless residents in Chicago. By collecting data from portal websites, using Google Map API and computing distance based on haversine formula, our software is capable of recommending nearest facilities. According to the Homeless Point-in-Time Count & Survey Report (Nathalie P. Voorhees Center, 2018), we particularly include the categories of shelters, food pantries, health services and warming/cooling centers. Meanwhile, homeless people with specific needs of family support can also find pertinent information in our system.

The target users of the system will not be restricted to the homeless. It could also be adopted by the governmental service providers, charities and institutions who have access to the contact and geographical information of the homeless.

## Dependencies

* python 3.7
* bs4 0.0.1
* re 3.x
* gmplot 1.2.0
* webbrowser 
* requests 2.19.1
* geopy 1.18.1
* pandas 0.23.4
* numpy 1.14.5
* math 1.0.0
* csv 0.14.1
* json 2.6.0
* googlemaps 3.0.2

## Data
This project using the open source data from [the City of Chicago Data Portal](https://data.cityofchicago.org/) as well as data obtained by web crawler and Google Map geocoding API. Here is a table about the source of our dataset:
<table>
  <tr>
  <th>Facility Type</th>
  <th>Source</th> 
    <th>Access</th>
  </tr>
  <tr>
    <td>Warming Centers</td>
    <td rowspan="8"style="vertical-align:middle">Chicago Data Portal</td>
    <td rowspan="8"style="vertical-align:middle">Download</td>
  </tr>
  <tr>
    <td>Cooling Centers</td>
  </tr>
  <tr>
    <td>Park</td>
  </tr>
  <tr>
    <td>Senior Centers</td>
  </tr>
  <tr>
    <td>Community Service Centers</td>
  </tr>
  <tr>
    <td>Condom Distribution Sites</td>
  </tr>
  <tr>
    <td>Familiy Support Agencies</td>
  </tr>
  <tr>
    <td>Public Health Service Centers</td>
  </tr>
  <tr>
  <td>Food Pantry Location</td>
    <td><a href="https://www.foodpantries.org/ci/il-chicago">FoodPantries.ORG</a></td>
    <td rowspan="2" style="vertical-align:middle">Web Crawler</td>
  </tr>
  <tr>
  <td>Shelter Location</td>
    <td><a href="https://www.homelessshelterdirectory.org/cgi-bin/id/city.cgi?city=Chicago&state=IL">Homeless Shelter Dictionary</a></td>
  </tr>
  <tr>
    <td>Food Pantry Geocode</td>
    <td rowspan="2"style="vertical-align:middle">Google Map Geocoding API</td>
    <td rowspan="2"style="vertical-align:middle">API</td>
  </tr>
  <tr>
    <td>Shelter Geocode</td>
 </tr>
 </table>

## Pipelines
The pipeline contains five python files:
* `find_facilities.py`: impletements the recommendation alogrithm with the processed data; and generate a web page representing the qualified facilities and their corresponding locations on Google Map
* `util.py`: contains the helper functions for crawl_food_pantry.py, crawl_shelter.py and find_facilities.py
* `crawl_food_pantry.py`: scrapes the website of food pantries
* `crawl_shelter.py`: scrapes the website of shelters
* `data_cleaning.py`: cleans the raw data from Chicago Data Portal (It is included in the `raw_data` folder)

Before executing the following code in User Guide,
* Please make sure you have installed all the packages of the same version as the ones in dependencies section.
* If you encounter such an error message,  you might need to install xlrd package from pandas separately.

```python
ImportError: No module named 'xlrd'
```
* Fire up the terminal, then go to the 'project' folder.
* Open iPython3 and import `find_facilities.py`:

```python
import find_facilities
```


## User Guide

`Inputs`: 
* filename
* address
* categories (optional)
* walking_time (optional)
* full_info (optional)

`Output`: 
* an html web page representing a table of qualified facilities
* map (require a click from the webpage)

Here is a legend for map markers:
<p align="center"><img src="https://github.com/haonen/Markdown-Photos/blob/master/legend.JPG?raw=true" width="850" height="400"></p>

In the following cases, we use the merged data of facilities provided in the file and specify address of John Crerar Library at the University of Chicago as an example. Note that if you download the data set in a different folder, please include the full path here. And address can be explicit or implicit as long as it can be identified by Google Map.
```python
filename = "full_data.csv"
address = "5730 S Ellis Ave, Chicago, IL 60637"
```

`Case 1:`

Given address as the only input, it will return the nearest 3 locations of each categories
```python
find_facilities.go(filename, address)
```
Part of the exported web page is:
<p align="center">
<img src="https://github.com/haonen/Markdown-Photos/blob/master/case%201%20html.JPG?raw=true" width="800" height="400">
</p>

Click on the hyperlink and get the corresonding Google Map:
<p align="center">
<img src="https://github.com/haonen/Markdown-Photos/blob/master/case%201%20map.JPG?raw=true" width="800" height="380">
</p>

`Case 2:`

Users can specify the categories of service type they are looking for. The function will return the nearest 3 locations of every category selected.
```python
find_facilities.go(filename, address, ["shelter", "food pantry", "warming center"])
```
`Case 3:`

Users can also specify walking time as the restriction. The function will return at most 3 nearest locations of every category specified.

```python
find_facilities.go(filename, address, ["shelter", "food pantry", "warming center"], walking_time=30)
```
`Case 4:`

Users can request for the detailed information of the facilities by specifying "True" in the full_info parameter.
```python
find_facilities.go(filename, address, ["shelter", "food pantry", "warming center"], walking_time=30, full_info=True)
```
The web page is:
<p align="center">
<img src="https://github.com/haonen/Markdown-Photos/blob/master/case%204%20html.PNG?raw=true" width="800" height="300">
</p>

The corresponding Google Map page 
<p align="center">
<img src="https://github.com/haonen/Markdown-Photos/blob/master/case%204%20map.JPG?raw=true" width="800" height="350"/>
</p>

## Reference
Nathalie P. Voorhees Center for Neighborhood & Community Improvement, University of Illinois at Chicago. (2018). Homeless Point-in-Time Count & Survey Report. Chicago, IL: Chicago Department of Family and Support Services

## License
MIT License

Copyright (c) 2019 Ta-Yun Yang, Xuan Bu, Yuwei Zhang

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.
## Acknowledgement
We would like to express our sincere gratitude to Dr. Anne Rogers, Dr. Lamont Samuels, Emma Nechamkin and Kavon Farvardin for your teaching, guidance, and support throughout the quarter.

