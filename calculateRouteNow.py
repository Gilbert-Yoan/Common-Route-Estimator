import requests
import urllib.parse as urlparse
from dotenv import load_dotenv, find_dotenv
import os
from time import sleep
from peewee import *

for var in ["TOMTOM_KEY","ORIGIN","DESTINATION", "COUNTRY"]:
    os.environ.pop(var, None)

env_path = find_dotenv()
if not env_path:
    raise FileNotFoundError("⚠️ No .env file found! Check its location.")
load_dotenv(env_path, override=True)

#Define starting and ending places in the same country
origin = os.getenv("ORIGIN")  
destination = os.getenv("DESTINATION")  
country = os.getenv("COUNTRY") 

# API Key of Tomtom API
key = os.getenv("TOMTOM_KEY")        # API Key

#Requesting Geocode of locations - format will be [(lat,lon),(lat,lon),...]
geocodesInterests = []

#Tomtom API to get Geocode from natural unstructured prompts
baseUrl = "https://api.tomtom.com/search/2/geocode/"

for place in [origin,destination]:
    requestParams = (
        urlparse.quote(place) + ".json?" +
        "countrySet=" + urlparse.quote(country)
    )
    requestUrl = baseUrl + requestParams + "&key=" + key
    response = requests.get(requestUrl)
    
    if(response.status_code == 200):
        # Get response's JSON
        jsonResult = response.json()
        print("There are "+str(len(jsonResult['results']))+" results for " + place)
        
        if len(jsonResult['results']) > 0 :
            #matchConfidence is an attribute that should give the best result
            bestResult = max(jsonResult['results'], key=lambda res: res["matchConfidence"]["score"])
            latitude = bestResult['position']['lat']
            longitude = bestResult['position']['lon']
            geocodesInterests.append((latitude, longitude))
            print("Best results : " + str(latitude) + " , " + str(longitude))
            
        else:
            print("Not found : "+place)
    else:
        print("Unexpected response : " + str(response.status_code))

    sleep(0.05) #Wait a little before querying again otherwise might result in HTTP 429

def get_response(baseUrl, params):
    response = requests.get(baseUrl,params=params)
        
    if(response.status_code == 200):
        # Get response's JSON
        jsonResult = response.json()
    else:
        print("Unexpected response : " + str(response.status_code))
        return 0
    #Wait a little before querying again otherwise might result in HTTP 429   
    sleep(0.05)
    return jsonResult['routes'][0]['summary']

baseUrl = "https://api.tomtom.com/routing/1/calculateRoute/"
#Add positions and json
baseUrlOriginToDestination = baseUrl +str(geocodesInterests[0][0])+","+str(geocodesInterests[0][1])+":"+str(geocodesInterests[1][0])+","+str(geocodesInterests[1][1])+"/json?"
baseUrlReverseTravel = baseUrl +str(geocodesInterests[1][0])+","+str(geocodesInterests[1][1])+":"+str(geocodesInterests[0][0])+","+str(geocodesInterests[0][1])+"/json?"
#Prepare GET parameters
requestParams = {"key":key}

#FROM A TO B
print("From "+origin+ " to "+destination+" :")
aToB = get_response(baseUrlOriginToDestination, requestParams)
print(aToB)
#FROM B TO A
print("From "+destination+ " to "+origin+" :")
bToA = get_response(baseUrlReverseTravel, requestParams)
print(bToA)

##This will create a Sqlite DB with a simple schema if needed and put result data in it

sqlite_db = SqliteDatabase('my_app.db', autoconnect=False)

class BaseModel(Model):
    """A base model that will use our Sqlite database."""
    class Meta:
        database = sqlite_db

class TravelHist(BaseModel):
    origin = TextField()
    destination = TextField()
    departureTime = DateTimeField()
    arrivalTime = DateTimeField()
    travelTimeMins = DoubleField()
    delayTimeMins = DoubleField()
    routeLengthKm = DoubleField()

sqlite_db.connect()
sqlite_db.create_tables([TravelHist])
TravelHist.insert(origin=origin, destination=destination, departureTime=aToB['departureTime'],
                  arrivalTime=aToB['arrivalTime'],travelTimeMins=aToB['travelTimeInSeconds']/60,delayTimeMins=aToB['trafficDelayInSeconds'],
                 routeLengthKm=aToB['lengthInMeters']/1000).execute()
TravelHist.insert(origin=destination, destination=origin, departureTime=bToA['departureTime'],
                  arrivalTime=bToA['arrivalTime'],travelTimeMins=bToA['travelTimeInSeconds']/60,delayTimeMins=bToA['trafficDelayInSeconds'],
                 routeLengthKm=bToA['lengthInMeters']/1000).execute()
sqlite_db.close()