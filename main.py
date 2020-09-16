import requests
import csv
import pycountry
import webbrowser
from config import my_api_key
import math
api_key = my_api_key

# TODO: Try using FourSquare API

# Inputs
city_name = "Thessaloniki"
country_name = "Greece"
country_code = pycountry.countries.get(name = country_name).alpha_2
radius = 1500

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
places_IDs = []

# Write places data to HTML 
# ['properties'] -> ['dist'], ['kinds'], ['name'], ['xid'], ['wikidata']
# Use ['image'], ['wikipedia_extracts']['text']
xid_name={}
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
		xid_name[props['xid']] =props['name'] 

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
				places_IDs.append(props['xid'])
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
			places_IDs.append(props['xid'])

def shortestPath(places, api_key):
	details_param = {"apikey":api_key}
	coords = {}
	path=[]
	path.append(places[0])
	# Get coordinates
	for place in places:
		info = requests.get("http://api.opentripmap.com/0.1/en/places/xid/" + place + "?", details_param)
		info_json = info.json()
		x=info_json["point"]["lon"]
		y=info_json["point"]["lat"]
		coords[place] = [x,y]

	closest = path[0]
	places.remove(places[0])
	# Get distances 
	for i in range(len(places)):
		distances={}
		position = closest # most recent
		for p in places:
			distance = math.sqrt((coords[position][0]-coords[p][0])**2+(coords[position][1]-coords[p][1])**2)
			distances[p]=distance
		closest = min(distances, key=distances.get)
		path.append(closest) # add to path
		places.remove(closest) # remove from list
	return path

path = shortestPath(places_IDs,api_key)
f.write("<ol>\n")
for xid in path:
	f.write("<li>"+ xid_name[xid] + '</li>\n')
f.write("</ol>\n")

f.close()
webbrowser.open_new_tab('itinerary.html')
print("Complete")