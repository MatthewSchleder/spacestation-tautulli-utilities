#!/bin/python

# This will export section metadata to determine what has and hasn't been watched
# It will create a file based on the field
from typing import List
import requests
import os
import csv
from datetime import datetime

from dotenv import load_dotenv

load_dotenv()
API_KEY = os.getenv("API_KEY")
ROOT_URL = os.getenv("TAUTULLI_ROOT_URL")
if not (API_KEY or ROOT_URL):
    print("Please set variables for API_KEY and TAUTULLI_ROOT_URL in .env")
    exit()


def get_metadata() -> List:
    libraries = requests.get(
        f"{ROOT_URL}/api/v2?apikey={API_KEY}&cmd=get_library_names"
    )
    lib_json = libraries.json()
    data_to_write = []

    for library in lib_json["response"]["data"]:
        media_info = requests.get(
            f"{ROOT_URL}/api/v2?apikey={API_KEY}&cmd=get_library_media_info&section_id={library['section_id']}&length=5000"
        )
        media_info = media_info.json()
        if library["section_type"] == "movie":
            for movie in media_info["response"]["data"]["data"]:
                wanted_keys = set(
                    [
                        "title",
                        "rating_key",
                        "file_size",
                        "last_played",
                        "play_count",
                    ]
                )
                movie_map = {k: movie[k] for k in movie.keys() & wanted_keys}
                data_to_write.append(movie_map)
        elif library["section_type"] == "show":
            for show_response in media_info["response"]["data"]["data"]:
                all_season_metadata = requests.get(
                    f"{ROOT_URL}/api/v2?apikey={API_KEY}&cmd=get_children_metadata&rating_key={show_response['rating_key']}"
                ).json()
                for season_children_list in all_season_metadata["response"]["data"][
                    "children_list"
                ]:
                    file_size = 0
                    if season_children_list["rating_key"]:
                        all_episode_metadata = requests.get(
                            f"{ROOT_URL}/api/v2?apikey={API_KEY}&cmd=get_library_media_info&rating_key={season_children_list['rating_key']}&media_type=episode"
                        ).json()
                        for episode_data in all_episode_metadata["response"]["data"][
                            "data"
                        ]:
                            file_size += int(episode_data["file_size"])
                        season_map = {
                            "title": f"{show_response['title']} - {season_children_list['title']}",
                            "rating_key": season_children_list["rating_key"],
                            "file_size": file_size,
                            "last_played": season_children_list["last_viewed_at"],
                            "play_count": all_episode_metadata["response"]["data"][
                                "data"
                            ][0]["play_count"],
                        }
                        data_to_write.append(season_map)

    return data_to_write


def day_subtraction(seconds_since_epoch: int) -> str:
    timestamp_date = datetime.fromtimestamp(seconds_since_epoch)
    current_date = datetime.now()
    difference = current_date - timestamp_date
    return difference.days


def write_csv(data_to_write: List) -> None:
    with open(f"Spacestation.csv", "w", newline="") as file:
        writer = csv.writer(file)
        field = [
            "title",
            "rating_key (id)",
            "file_size",
            "play_count",
            "last_played (Days ago)",
        ]

        writer.writerow(field)
        for media_info in data_to_write:
            play_count = 0
            last_played = "Never Played"
            if media_info["play_count"]:
                play_count = media_info["play_count"]
            if media_info["last_played"]:
                last_played = day_subtraction(int(media_info["last_played"]))
            writer.writerow(
                [
                    media_info["title"],
                    media_info["rating_key"],
                    media_info["file_size"],
                    play_count,
                    last_played,
                ]
            )
    print(f"Successfully written to Spacestation.csv")


if __name__ == "__main__":
    media_data = get_metadata()
    write_csv(media_data)
