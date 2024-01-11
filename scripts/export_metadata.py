#!/bin/python

# This will export section metadata to determine what has and hasn't been watched
# It will create a file based on the field
import requests
import os
import csv
import datetime


from dotenv import load_dotenv

load_dotenv()
api_key = os.getenv("API_KEY")
root_url = os.getenv("TAUTULLI_ROOT_URL")

if not (api_key or root_url):
    print("Please set variables for API_KEY and TAUTULLI_ROOT_URL in .env")
    exit()


libraries = requests.get(f"{root_url}/api/v2?apikey={api_key}&cmd=get_libraries")
lib_json = libraries.json()

for item in lib_json["response"]["data"]:
    media_info = requests.get(
        f"{root_url}/api/v2?apikey={api_key}&cmd=get_library_media_info&section_id={item['section_id']}&length=5000"
    )
    movie_info = media_info.json()
    with open(f"{item['section_name']}.csv", "w", newline="") as file:
        writer = csv.writer(file)
        field = ["title", "rating_key (id)", "file_size", "play_count", "last_played (Days ago)"]

        writer.writerow(field)
        for movie_info in movie_info["response"]["data"]["data"]:
            play_count = 0
            last_played = 0
            if movie_info["play_count"]:
                play_count = movie_info["play_count"]
            if movie_info["last_played"]:
                last_played = movie_info["last_played"]
                if last_played != 0:
                    daysago = “Never Played”
                else:
                    daysago =  (datetime.now().timestamp() - int(movie_info[last_played]) / 8600
            writer.writerow(
                [
                    movie_info["title"],
                    movie_info["rating_key"],
                    movie_info["file_size"],
                    play_count,
                    daysago,
                ]
            )
        print(f"Successfully written to {item['section_name']}.csv")
