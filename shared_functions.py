import json

import emoji
import requests
import tweepy

# import location_parser

####APP FUNCTIONS####
def json_to_hash(site, username, api_key="API_KEY_HERE"):
    # data = {}
    # if site == "location":
    #     data = location_parser.get_location_hash()
    # else:

    endpoint= {
        'instagram':'https://www.instagram.com/'+username+'/media/', 
        'lastfm':'http://ws.audioscrobbler.com/2.0/?method=user.getrecenttracks&user='+username+'&api_key='+api_key+'&format=json'
    }
    r = requests.get(endpoint[site])
    resp = r.text
    data = json.loads(resp)

    return data

def last_item(site, data):
    if site == "instagram":
        last_photo = data["items"][0]
        return last_photo
    elif site == "lastfm":
        last_song = data["recenttracks"]["track"][0]
        return last_song
    elif site == "location":
        last_location = data["location"]
        return last_location

def tracker_last_updated(user, site):
    with open("updatetracker.json","r+") as f:
        data = f.read()
        info = json.loads(data)
        updated = info[site][user]
        return updated

def tracker_update(user, site, update_info):
    with open("updatetracker.json","r+") as f:
        data = f.read()
        info = json.loads(data)
        info[site][user] = update_info
        # f.seek(0)
        # json.dump(info, f, indent=4)

    with open("updatetracker.json", "w") as f:
        json.dump(info, f, indent=4)

def tweet_text(data, site, user, photo_filepath=""):
    tweet = ""

    if user == "doremidom":
        person = "Dominique"
    else:
        person = "David"

    # Twitter API authentication
    cfg = get_config_json("config.json") # TODO: pass this in as an argument
    cfg_twitter = cfg["twitter"]
    consumer_key = cfg_twitter["consumer_key"]
    consumer_secret = cfg_twitter["consumer_secret"]
    access_key = cfg_twitter["access_key"]
    access_secret = cfg_twitter["access_secret"]

    resp = {"id": "FAILED"}
    auth = tweepy.OAuthHandler(consumer_key, consumer_secret)
    auth.set_access_token(access_key, access_secret)
    api = tweepy.API(auth)

    if site == "instagram":
        url = data["link"]
        tweet = person + " just posted a new picture from the road! " + url
        print(tweet)
        resp = api.update_status(tweet)
        print(resp.id)
        # return tweet
    elif site == "lastfm":
        song = data[0]
        artist = data[1]
        tweet = ':musical_note:' + ' Currently listening to ' + song + " by " + artist
        tweet = emoji.emojize(tweet)
        print(tweet.encode("utf-8"))
        resp = api.update_status(tweet)
        print(resp.id)
        # return tweet
    elif site == "location":
        tweet = "Last spotted on the road"
        # location = data["location"] if "location" in data else ""
        location = data
        print(data)
        if len(location) > 0:
            tweet = "Last spotted in {}".format(location)
        print(tweet)
        print("photo_filepath: " + photo_filepath)

        if photo_filepath != "":
            resp = api.update_with_media(photo_filepath.encode("utf-8"), status=tweet.encode("utf-8"))
            print("location photo found! it's at " + photo_filepath)
            print(resp.id)
        else:
            resp = api.update_status(tweet)
            print(resp.id)

        # return tweet


# Retrieve JSON object with all config properties
def get_config_json(config_path):
    config_json = {}
    with open(config_path, "r") as f:
        config_json = json.loads(f.read())
    return config_json

# Retrieve
# def get_location_photo(data):
