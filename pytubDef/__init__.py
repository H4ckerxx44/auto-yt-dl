import pytubDef
from configparser import ConfigParser
import logging
from yt_dlp import YoutubeDL


# Magic numbers
INTERVAL_LIMIT = 60

# Constants for reused messages in logging / printing
CONFIG_DOES_NOT_EXIST = "Config does not seem to exist, creating a new one"

# File names
CONFIG_FILE = "data/config.ini"
MONITORED_PLAYLIST = "data/monitoredPlaylist.txt"


def log():
    try:
        file = CONFIG_FILE
        config = ConfigParser()
        config.read(file)
        logging.debug(f"Returning log bool from config {str(config.getboolean('Settings', 'log'))}")
        try:
            return config.getboolean("Settings", "log")
        except:
            config.set("Settings", "log", "False")
            with open(CONFIG_FILE, "r") as conf:
                config.write(conf)
            return log()
    except Exception as e:
        logging.debug(e)
        logging.info(CONFIG_DOES_NOT_EXIST)
        create_config()
        return log()


def loop():
    playlists = return_monitored_playlist()

    for playlist in playlists:
        try:
            check_for_new_url_from_playlist(str(playlist))
        except Exception as e:
            logging.debug(e)
            logging.error(f"Something went wrong while checking for new Videos from {playlist}")
            print(f"Oops. Something went wrong while checking for new Videos: {str(e)}")


def return_interval():
    try:
        config = ConfigParser()
        config.read(CONFIG_FILE)
        logging.debug("Returning interval from config" + str(config["Settings"]["interval"]))
        return config["Settings"]["interval"]
    except Exception as e:
        logging.debug(e)
        logging.info(CONFIG_DOES_NOT_EXIST)
        create_config()
        return return_interval()


def return_channel_dir():
    try:
        config = ConfigParser()
        config.read(CONFIG_FILE)
        logging.debug("Returning channelDir from config" + str(config.getboolean("Settings", "channelDir")))
        return config.getboolean("Settings", "channelDir")
    except Exception as e:
        logging.debug(e)
        logging.info(CONFIG_DOES_NOT_EXIST)
        create_config()
        return return_channel_dir()


def return_yt_agent():
    try:
        config = ConfigParser()
        config.read(CONFIG_FILE)
        logging.debug("Returning ytagent from config" + str(config.getboolean("Settings", "ytagent")))
        return config.getboolean("Settings", "ytagent")
    except Exception as e:
        logging.debug(e)
        logging.info(CONFIG_DOES_NOT_EXIST)
        create_config()
        return return_channel_dir()


def update_interval(interval: int):
    # TODO: turn magic number into constant
    if interval >= INTERVAL_LIMIT:
        try:
            config = ConfigParser()
            config.read(CONFIG_FILE)
            config.set("Settings", "interval", str(interval))
            with open(CONFIG_FILE, "w") as configfile:
                config.write(configfile)
            logging.info(f"New interval {interval} set")
        except Exception as e:
            logging.debug(e)
            logging.info(CONFIG_DOES_NOT_EXIST)
            create_config()
            update_interval(interval)
    else:
        logging.info(f"Illegal interval: {interval}")
        print(f"Interval must be at least {INTERVAL_LIMIT}")


def toggle_channel_dir():
    try:
        config = ConfigParser()
        config.read(CONFIG_FILE)
        if return_channel_dir():
            config.set("Settings", "channelDir", "False")
        else:
            config.set("Settings", "channelDir", "True")
        with open(CONFIG_FILE, "w") as configfile:
            config.write(configfile)
        logging.info("Toggled channelDir")
    except Exception as e:
        logging.debug(e)
        logging.info(CONFIG_DOES_NOT_EXIST)
        create_config()
        toggle_channel_dir()


def toggle_yt_agent():
    try:
        config = ConfigParser()
        config.read(CONFIG_FILE)
        if return_yt_agent():
            config.set("Settings", "ytagent", "False")
        else:
            config.set("Settings", "ytagent", "True")
        with open(CONFIG_FILE, "w") as configfile:
            config.write(configfile)
        logging.info("Toggled ytagent")
    except Exception as e:
        logging.debug(e)
        logging.info(CONFIG_DOES_NOT_EXIST)
        create_config()
        toggle_yt_agent()


def create_config():
    config_object = ConfigParser()
    config_object["Settings"] = {
        "interval": "900",
        "channelDir": "True",
        "ytagent": "False",
        "log": "False"
    }
    with open(CONFIG_FILE, "w") as conf:
        config_object.write(conf)
    logging.info("New config has been created")


def download_video(video_url, path):
    logging.info("Downloading: " + video_url)
    print("Downloading new Video: " + video_url)
    try:
        if return_yt_agent():
            outtmpl = f"{path}/[%(id)s].mp4"
            ydl_opts = {
                "outtmpl": outtmpl, "cachedir": "data/cache"
            }
        else:
            outtmpl = f"{path}/%(title)s.mp4"
            ydl_opts = {
                "outtmpl": outtmpl, "cachedir": "data/cache"
            }
        with YoutubeDL(ydl_opts) as ydl:
            ydl.download(video_url)
    except:
        print(f"Failed to download video: {video_url}. Is it a livestream?")
        return False
    return True


def check_for_new_url_from_playlist(playlist_url):
    playlist_name = get_playlist_name(playlist_url)
    msg = f"Searching for new videos of {playlist_name}"
    print(msg)
    logging.info(msg)
    video_urls = get_video_urls(playlist_url)
    for video_url in video_urls:
        if not url_already_written(video_url, playlist_name):
            if download_video(video_url, compute_path(video_url, playlist_name, get_playlist_id(playlist_url))):
                write_channel_url_to_file(playlist_name, video_url)


def write_channel_url_to_file(playlist_name, url: str):
    try:
        url_file = open(f"data/{replace_illegal_characters(playlist_name)}.txt")
        print(f"{playlist_name}´s URL-File already exist")
    except Exception as e:
        logging.debug(e)
        url_file = open("data/" + replace_illegal_characters(playlist_name) + ".txt", "x")
        url_file.mode = "rt"
        print(f"{playlist_name}´s URL-File does not exist, created File")
        logging.info("Created new .txt for" + playlist_name)

    url_file.close()

    if not url_already_written(url, playlist_name):
        url_file = open("data/" + replace_illegal_characters(playlist_name) + ".txt", "a")
        url_file.writelines(" \n" + url)
        url_file.close()
        print(f"Writing URL to {playlist_name}")
        logging.info(f"Added new URL to {playlist_name}: {url}")
    else:
        logging.info(f"URL: {url} already saved in {playlist_name}")
        print("URL is already written")


def compute_path(url, name, ident):
    logging.info(f"Found new video of {name}: {url}")
    print(f"Found and downloading a new URL from {name}")
    if return_channel_dir():
        path = f"Downloads/{replace_illegal_characters(str(name))}"
    else:
        path = "Downloads"
    if return_yt_agent():
        path = f"Downloads/[{str(ident)}]"
    logging.info(f"Initiating download of {url}")
    return path


def url_already_written(url: str, channel_name: str):
    with open(f"data/{replace_illegal_characters(channel_name)}.txt") as url_file:
        file_content = url_file.readlines()
    return True if url in file_content else False


def new_monitored_playlist(playlist_url: str):
    logging.info(f"Adding new playlist/channel: {playlist_url}")
    try:
        playlist_name = get_playlist_name(playlist_url)
        actual_url = get_playlist_url(playlist_url)

        for playlist_urls in return_monitored_playlist():
            if actual_url in playlist_urls:
                msg = f"Playlist {playlist_url} is already monitored (URL in monitoredPlaylist.txt {playlist_urls})"
                logging.info(msg)
                print(msg)
                return False
        with open(MONITORED_PLAYLIST, "a") as monitored_playlist_file:
            monitored_playlist_file.write(" \n" + actual_url)

        with open(f"data/{replace_illegal_characters(playlist_name)}.txt/", "x") as urlFile:
            for video in get_video_urls(playlist_url):
                urlFile.write(f" \n{video}")

    except Exception as e:
        msg = f"Something went wrong while adding playlist: {e}"
        logging.debug(msg)
        print(msg)


def replace_illegal_characters(dirty_string: str):
    tmp = dirty_string
    illegal_chars = ("<", ">", ":", '"', "/", "\\", "|", "?", "*")
    for illegal_char in illegal_chars:
        tmp = tmp.replace(illegal_char, "")
    return tmp


def get_video_urls(playlist_url):
    ydl_opts = {"extract_flat": True, "outtmpl": "%(id)s.%(ext)s", "cachedir": "data/cache"}
    with YoutubeDL(ydl_opts) as ydl:
        result = ydl.extract_info(playlist_url, download=False)

    videos = []

    for n in range(len(result["entries"])):
        try:
            for vid in result['entries'][n]['entries']:
                videos.append("https://www.youtube.com/watch?v=" + vid["id"])
        except Exception:
            try:
                videos.append("https://www.youtube.com/watch?v=" + result['entries'][n]["id"])
            except Exception as e:
                print(f"Could not fetch videos from {playlist_url}: {str(e)}")
    return videos


def get_playlist_name(playlist_url):
    try:
        file = CONFIG_FILE
        config = ConfigParser()
        config.read(file)
        logging.debug("Returning playlist name from config" + str(config[playlist_url]["name"]))
        return config[playlist_url]["name"]
    except Exception as e:
        logging.debug(e)
        logging.info(f"Config entry for {playlist_url} does not seem to exist, creating a new one")
        create_playlist_config_entry(playlist_url)
        return get_playlist_name(playlist_url)


def get_playlist_url(playlist_url):
    ydl_opts = {
        'playlist_items': '1', 'cachedir': "data/cache"
    }
    with YoutubeDL(ydl_opts) as ydl:
        result = ydl.extract_info(playlist_url, download=False)
    return result['webpage_url']


def create_playlist_config_entry(url):
    config_object = ConfigParser()
    playlist_data = get_playlist_id_information(url)
    config_object[url] = {
        "id": playlist_data[0],
        "name": playlist_data[1],
    }
    with open('data/config.ini', 'a') as conf:
        config_object.write(conf)
    logging.info("New config entry for " + url + " has been created")


def get_playlist_id(playlist_url):
    try:
        file = CONFIG_FILE
        config = ConfigParser()
        config.read(file)
        logging.debug("Returning playlist id from config" + str(config[playlist_url]["id"]))
        return config[playlist_url]["id"]
    except Exception as e:
        logging.debug(e)
        logging.info("Config entry for " + playlist_url + "does not seem to exist, creating a new one")
        create_playlist_config_entry(playlist_url)
        return get_playlist_id(playlist_url)


def get_playlist_id_information(playlist_url):
    information = []
    # Fetch the playlists ID
    ydl_opts = {
        'playlist_items': '1', 'cachedir': "data/cache"
    }
    with YoutubeDL(ydl_opts) as ydl:
        result = ydl.extract_info(playlist_url, download=False)
    information.append(result["entries"][0]["id"])

    # Fetch the playlists Name
    information.append(result['title'])

    return information


def return_monitored_playlist():
    # TODO: replace with actual logic about config file creation
    #  catch FileNotFound exceptions
    try:
        monitored_playlist_file = open(MONITORED_PLAYLIST)
    except Exception as e:
        logging.debug(e)
        logging.info("monitoredPlaylist.txt does not seem to exist, creating a new one")
        monitored_playlist_file = open(MONITORED_PLAYLIST, "x")
        monitored_playlist_file.mode = "r"
        logging.info("monitoredPlaylist.txt created")

    lines = monitored_playlist_file.readlines()
    monitored_playlist_file.close()

    playlist_urls = []
    for line in lines:
        if "https://" in line:
            playlist_urls.append(line.replace("\n", "").replace(" ", ""))

    return playlist_urls


def remove_monitored_playlist(old_playlist_url: str):
    logging.info(f"Removing {old_playlist_url} from monitored playlists")
    with open(MONITORED_PLAYLIST) as monitored_playlist_file:
        playlist_urls = monitored_playlist_file.readlines()

    for playlist_url in playlist_urls:
        if old_playlist_url == playlist_url:
            del playlist_url
            break

    with open(MONITORED_PLAYLIST, "w") as monitored_playlist_file:
        for playlist_url in playlist_urls:
            monitored_playlist_file.write(playlist_url)
