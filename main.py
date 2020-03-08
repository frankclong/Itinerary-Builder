import requests
import csv
import pycountry
import webbrowser
from config import my_api_key
api_key = my_api_key

# Inputs
city_name = "Guelph"
country_name = "Canada"
country_code = pycountry.countries.get(name = country_name).alpha_2
radius = 10000

# Get longitude and latitude of city/area
geo_param = {"name":city_name,"country": country_code,"apikey":api_key}
url = "http://api.opentripmap.com/0.1/en/places/geoname?"
geoname = requests.get(url, geo_param)
geoname_json = geoname.json()
lon = geoname_json["lon"]
lat = geoname_json["lat"]

# Get collection of places
#Note: radius in meters
#https://dev.opentripmap.com/doc/en/
# TODO: Find best source
place_param = {"lon":lon,"lat":lat,"radius": radius,"rate":"3h","src_attr":"osm","src_geom":"osm","apikey":api_key}
places = requests.get("http://api.opentripmap.com/0.1/en/places/radius?",place_param)
places_json = places.json() # feature collection
#print(places_json)

# Write places data to HTML 
# ['properties'] -> ['dist'], ['kinds'], ['name'], ['xid'], ['wikidata']
# Use ['image'], ['wikipedia_extracts']['text']
f = open('itinerary.html','w',encoding='utf-8')
with open('places.csv', mode='w') as my_file:
	file_writer = csv.writer(my_file, delimiter=',', quotechar='"', quoting=csv.QUOTE_MINIMAL)
	details_param = {"apikey":api_key}
	prev_wiki = ""
	for p in places_json['features']: # for each place
		props = p['properties']
		# Request
		info = requests.get("http://api.opentripmap.com/0.1/en/places/xid/" + props['xid'] + "?", details_param)
		info_json = info.json()

		# TODO: remove duplicates
		# Identical name or identical wiki info
		if info_json.get("wikipedia_extracts"):
			if prev_wiki != info_json['wikipedia_extracts']['text']:
				prev_wiki = info_json['wikipedia_extracts']['text']
				f.write("<h1>"+props['name'] + '</h1>\n')
				# Tags
				f.write("<p>"+props['kinds'] + '</p>\n')
				f.write("<p>"+info_json['wikipedia_extracts']['text'] + '</p>\n')
				url = info_json['image']
				url = url.replace('/File:', '/Special:FilePath/')
				url = url +'?width=300px'
				f.write("<img src=\"" + url+ "\">" + "\n")
				f.write("<hr>\n")
		else:
			f.write("<h1>"+props['name'] + '</h1>\n')
			# Tags
			f.write("<p>"+props['kinds'] + '</p>\n')
			if info_json.get("image"):
				url = info_json['image']
				url = url.replace('/File:', '/Special:FilePath/')
				url = url +'?width=300px'
				f.write("<img src=\"" + url+ "\">" + "\n")
			f.write("<hr>\n")

f.close()
webbrowser.open_new_tab('itinerary.html')