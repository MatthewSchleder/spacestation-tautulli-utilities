# spacestation-tautulli-utilities

Python scripts to access information for SpaceStation's tautulli instance

## Setup

This assumes that you have a running Tautulli instance and is already configured to your plex server. These only need to be done once

1. Download Python, if you don't already have it
1. Navigate to the .env.template and replace the two variables with your instance and API key, do not add an ending '/' to the root URL
1. Rename `.env.template` to `.env`
1. Open a terminal window and run `pip install -r requirements.txt`

## Running the scripts

1. From any terminal window, run

```shell
python scripts/file_name.py
```

You will be greeted with messages for output files or errors, if any occur
