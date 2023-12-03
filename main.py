from time import sleep
import pytubDef
import logging
import os.path
from pytubDef import MONITORED_PLAYLIST


def find_link(url):
    return pytubDef.get_playlist_url(url.replace("\n", "").replace(" ", ""))


if pytubDef.log():
    logging.basicConfig(filename="data/mainDebug.log", encoding="utf-8", level=logging.DEBUG)

if os.path.exists(MONITORED_PLAYLIST):
    print("Deprecated monitoredChannel.txt file still exists. Converting...")
    try:
        success = True
        with open(MONITORED_PLAYLIST) as f:
            channelURLs = f.readlines()

        with open(MONITORED_PLAYLIST, "a") as monitoredPlaylistFile:
            for line in channelURLs:
                if "https://" in line:
                    print(f"Trying to find new link to {line}")
                    try:
                        monitoredPlaylistFile.write(" \n" + find_link(line))
                    except:
                        try:
                            monitoredPlaylistFile.write(" \n" + find_link(line.replace("/c/", "/channel/")))
                        except:
                            try:
                                monitoredPlaylistFile.write(" \n" + find_link(line.replace("/c/", "/@")))
                            except:
                                print(f"Could not find channel url for deprecated {line}")
                                print(f"Please add {line} manually.")
                                success = False
        if success:
            os.remove(MONITORED_PLAYLIST)
        else:
            os.rename(MONITORED_PLAYLIST, "data/DEPRECATEDmonitoredChannels.txt")
        print("Deprecated monitoredChannel.txt has been converted.")
    except Exception as e:
        print(f"Something went wrong while merging the deprecated monitoredChannel.txt file with the monitoredPlaylist.txt: {str(e)}")
        logging.debug(e)
        logging.info("Something went wrong while merging the deprecated monitoredChannel.txt file with the monitoredPlaylist.txt")

for playlist in pytubDef.return_monitored_playlist():
    try:
        pytubDef.url_already_written("", pytubDef.get_playlist_name(playlist))
    except:
        pytubDef.remove_monitored_playlist(playlist)
        pytubDef.new_monitored_playlist(playlist)
    try:
        pytubDef.get_playlist_name(playlist)
    except:
        pytubDef.create_playlist_config_entry(playlist)


logging.info("Service started.")
print("Starting loop....")

while True:
    logging.info("Checking for new videos")
    print("Checking for new Videos")
    try:
        pytubDef.loop()
    except Exception as e:
        logging.info("An error occurred while checking for new videos.")
        logging.debug(e)
        print(f"An error occurred while checking for new videos: {str(e)}")
    print(f"Sleeping for {pytubDef.return_interval()} seconds till next check")
    sleep(int(pytubDef.return_interval()))
