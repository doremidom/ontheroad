"""
Functions dealing with locations and places
"""

#!/usr/bin/env python

import json
import random

import requests

from shared_functions import *


######LOCATION FUNCTIONS######

# Get location hash given a config JSON file. A pretty close replica of the main method
def get_location_hash(config_json):    
    coordinates = get_location_coordinates(config_json)
    locality, photo_refs = get_location_name_and_photo_references(coordinates, config_json)
    return {"location":locality, "photo_references":photo_refs}

# Create a Twitter-worthy message about our location
def construct_locality_message(locality):
    if len(locality) > 0:
        return "Currently in {}".format(locality)
    else:
        return "Currently on the road"

def save_location_photo(name, data):
    config_json = get_config_json("config.json") # TODO: pass this in as an argument
    photo_refs = data["photo_references"]
    config_places = config_json["google_places"]
    endpoint = config_places["api_endpoint"]
    url = endpoint + "photo"
    photo_filepath = config_json["location"]["photo_filepath"]

    for photo_ref in photo_refs:
        print("photo_ref: " + photo_ref)
        params = {
            "key": config_places["api_key"],
            "maxwidth": 600, # px
            "photoreference": photo_ref
        }
        r = requests.get(url, params=params, stream=True)
        if r.status_code == 200:
            with open(photo_filepath, "wb") as f:
                for chunk in r:
                    f.write(chunk)
            return photo_filepath

    return ""


# def save_location_to_tracker(location, tracker_path):
#     with open(tracker_path, "r"):

# Find the city and state given a lat/lng pair, based on Google Places API
def get_location_name_and_photo_references(coordinates, config_json):
    locality = ""
    state = ""
    place_ids = []
    photo_refs = []

    # Retrieve nearby places using Nearby Search
    config_places = config_json["google_places"]
    endpoint = config_places["api_endpoint"]
    url_nearbysearch = endpoint + "nearbysearch/json"
    params_nearbysearch = {
        "key": config_places["api_key"],
        "radius": 24000, # 15 miles
        "location": "{},{}".format(coordinates["latitude"], coordinates["longitude"])
    }
    r = requests.get(url_nearbysearch, params=params_nearbysearch)
    # print(r.url)
    # print(r.content)
    resp_obj = json.loads(r.content) if r.ok else {}

    results = resp_obj["results"] if "results" in resp_obj else {}
    place_ids = [result["place_id"] for result in results if "place_id" in result]

    # Attempt to tease out locality (city) from Place Details
    is_locality_found = False
    is_state_found = False

    url_details = endpoint + "details/json"
    for place_id in place_ids:
        if is_locality_found and is_state_found:
            break

        # Retrieve place details
        params_details = {
            "key": config_places["api_key"],
            "placeid": place_id
        }
        r = requests.get(url_details, params=params_details)
        resp_obj = json.loads(r.content) if r.ok else {}
        # print(resp_obj)

        # Parse address components to try to find a locality
        address_components = resp_obj["result"]["address_components"] if ("result" in resp_obj and "address_components" in resp_obj["result"]) else []
        for address_component in address_components:
            address_types = address_component["types"] if "types" in address_component else []
            for address_type in address_types:
                # TODO: refactor and generalize the below using a location_matches dict
                # for match_type in ["locality", "administrative_area_level_1"]
                if is_address_type_match(address_type, "locality"):
                    if "short_name" in address_component:
                        locality = address_component["short_name"]
                        is_locality_found = True
                    elif "long_name" in address_component:
                        locality = address_component["long_name"]
                        is_locality_found = True
                elif is_address_type_match(address_type, "administrative_area_level_1"):
                    if "short_name" in address_component:
                        state = address_component["short_name"]
                        is_state_found = True
                    elif "long_name" in address_component:
                        locality = address_component["long_name"]
                        is_state_found = True

        # Get photo references
        if "result" in resp_obj and "photos" in resp_obj["result"]:
            photo_refs = [photo["photo_reference"] for photo in resp_obj["result"]["photos"]]
        else:
            print("please no photos")

    # Append state to locality if we've found it
    if is_locality_found and is_state_found:
        locality = "{}, {}".format(locality, state)
    
    return (locality, photo_refs)

# Returns a boolean based on whether address type matches match type
def is_address_type_match(address_type, match_type):
    if match_type in address_type:
        return True
    return False

# Get location coordinates based on Traccar API
def get_location_coordinates(config_json):
    coordinates = {"latitude": 0.0, "longitude": 0.0}
    
    # Get latest position data from Traccar
    config_traccar = config_json["traccar"]
    r = requests.get(config_traccar["api_endpoint"] + "positions",
                     auth=(config_traccar["email"], config_traccar["password"]))
    if not r.ok:
        return coordinates

    # Update coordinates JSON with latest position coordinates
    positions = json.loads(r.content)
    # print(positions)
    if len(positions) > 0:
        position = positions[0]
        coordinates["latitude"] = position["latitude"]
        coordinates["longitude"] = position["longitude"]
    
    return coordinates

# Generate a pair of coordinates within the continental US
def generate_random_coordinates():
    lat = random.uniform(46, 34)
    lng = random.uniform(-120, -90)
    return {
        "latitude": lat,
        "longitude": lng
    }

# Main method
if __name__ == "__main__":
    config_json = get_config_json("config.json")
    
    coordinates = get_location_coordinates(config_json)
    # coordinates = {"latitude": -82.862, "longitude": 135.0000} # Antarcticaaa
    # coordinates = generate_random_coordinates()
    print("Coordinates: {}".format(coordinates))

    locality = get_location_locality_and_state(coordinates, config_json)
    locality_message = construct_locality_message(locality)
    print(locality_message)

    # tracker_update("dnd", "location", locality)
