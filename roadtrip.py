##Instagram Updater##
import json
import requests
import datetime
import time
import emoji
import sys

from shared_functions import *
import location_parser

######INSTAGRAM FUNCTIONS######


def instagram_last_updated(data):
	date = data["created_time"]
	return date


def item_changed(item_info, tracker_info, site):
	if site == "instagram":
		return True if int(item_info) > int(tracker_info) else False
	elif site == "lastfm" or site == "location":
		return True if item_info != tracker_info else False

def instagram_updater(latest_item, tracker_time, user):
	item_time = instagram_last_updated(latest_item)
	if item_changed(item_time, tracker_time, "instagram"):
		tracker_update(user, "instagram", item_time)
		tweet_text(latest_item, "instagram", user)
	else:
		print("no instagram update currently for " + user)

def lastfm_updater(data, user, tracker_song):
	current_song = data["name"]
	current_artist = data["artist"]["#text"]
	full_info = [current_song, current_artist]

	if item_changed(current_song, tracker_song, "lastfm"):
		tracker_update(user, "lastfm", current_song)
		tweet_text(full_info, "lastfm", user)
	else:
		print("no lastfm update currently for " + user)

def location_updater(loc_curr, loc_prev, user):
	if item_changed(loc_curr, loc_prev, "location"):
		tracker_update(user, "location", loc_curr)
		tweet_text(loc_curr, "location", user)
	else:
		print("no location update currently for " + user)

def updater(site):
	# sites = ["instagram", "lastfm", "location"]

	cfg = get_config_json("config.json")
	ig_usernames = cfg["instagram"]["usernames"]
	lfm_usernames = cfg["lastfm"]["usernames"]
	loc_usernames = cfg["location"]["usernames"]

	# for site in sites:
	if site == "instagram":
		users = ig_usernames
	if site == "lastfm":
		users = lfm_usernames
	if site == "location":
		users = loc_usernames

	for user in users:
		data = {}
		if site == "instagram":
			data = json_to_hash(site, user, "no api key necessary")
		elif site == "lastfm":
			data = json_to_hash(site, user, cfg["lastfm"]["api_key"])
		elif site == "location":
			data = location_parser.get_location_hash(cfg)
		# else:
		# 	data = json_to_hash(site, user)

		latest_item = last_item(site, data)
		tracker_info = tracker_last_updated(user, site)

		if site == "instagram":
			instagram_updater(latest_item, tracker_info, user)
		elif site == "lastfm":
			lastfm_updater(latest_item, user, tracker_info)
		elif site == "location":
			location_updater(latest_item, tracker_info, user)
			
#######LASTFM FUNCTIONS#######



# MAIN
if __name__ == "__main__":
	site = sys.argv[1]
	updater(site)