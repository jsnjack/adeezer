# Automate downloading Deezer tracks with http://deezer.link

import argparse
import json
import os
import progressbar
import requests
import sys
import time

from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.common.exceptions import UnexpectedAlertPresentException, NoSuchWindowException
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC


# Time to wait for file download
TIMEOUT = 200
# Time to wait between startig to download next track
# Consider increasing it if you browser doesn't have enough time to save the file
TRACK_TIMEOUT = 5


# Fix encode error on Windows issue #3
if os.name == "nt":
    import codecs
    sys.stdout = codecs.getwriter("iso-8859-1")(sys.stdout, 'xmlcharrefreplace')


def get_tracks(item_type, item_id):
    """
    Downloads tracks information using Deezer API.
    Returns tracks list and download directory
    """
    url = "http://api.deezer.com/{item_type}/{item_id}".format(item_type=item_type, item_id=item_id)
    response = requests.get(url)
    if response.status_code == 200:
        try:
            tracks = json.loads(response.content)['tracks']['data']
        except KeyError:
            print("Bad response:\n %s" % response.content)
            tracks = []
    else:
        print(u"Received status code {code} from Deezer API for url {url}".format(code=response.status_code, url=url))
        tracks = []
    data = []
    print u"Tracks to download:"
    download_dir = get_download_dir(item_id)
    file_list = os.listdir(download_dir)
    for item in tracks:
        if item['id'] > 0:
            # Check if file already exists
            check_name = u"{artist} - {title} (from WWW.DEEZER.LINK).mp3".format(
                artist=item['artist']['name'], title=item['title']
            ).replace(
                u"/", u"_"
            ).replace(
                u"?", u"_"
            ).replace(
                u'"', u"_"
            ).replace(
                u"*", u"_"
            )
            if check_name not in file_list:
                print check_name
                data.append([item['link'], item['artist']['name'], item['title']])
    return data, download_dir


def get_favourite_tracks(user_id):
    """
    Get favourites tracks of given user
    """
    try:
        user_id = int(user_id)
    except ValueError:
        print(u"User id should be a number")
    url = "http://api.deezer.com/user/{user_id}/playlists".format(user_id=user_id)
    response = requests.get(url)
    playlist_id = None
    if response.status_code == 200:
        try:
            playlists = json.loads(response.content)['data']
            for item in playlists:
                if item['is_loved_track']:
                    playlist_id = item['id']
                    break
        except KeyError:
            print("Bad response:\n %s" % response.content)
    else:
        print(u"Received status code {code} from Deezer API for url {url}".format(code=response.status_code, url=url))
    return get_tracks('playlist', playlist_id)


def get_download_dir(item_id):
    """
    Creates download directory based on album or playlist id
    """
    download_dir = os.path.join(os.path.expanduser(u'~'), u'Downloads', unicode(item_id))
    if not os.path.isdir(download_dir):
        os.makedirs(download_dir)
    return download_dir


def download(tracks, download_dir, headless):
    """
    Download tracks
    """
    if os.name == "posix" and headless:
        from xvfbwrapper import Xvfb
        xvfb = Xvfb(width=1280, height=720)
        xvfb.start()

    # Configure Firefox
    fp = webdriver.FirefoxProfile()
    fp.add_extension(extension='adblock.xpi')
    fp.set_preference("browser.download.folderList", 2)
    fp.set_preference("browser.download.manager.showWhenStarting", False)
    fp.set_preference("browser.download.dir", download_dir)
    fp.set_preference("browser.helperApps.neverAsk.saveToDisk", "audio/mpeg")

    driver = webdriver.Firefox(firefox_profile=fp)

    pbar = progressbar.ProgressBar()
    for item in pbar(tracks):
        driver.get("http://deezer.link/")
        driver.find_element_by_id("trackUrl").send_keys(item[0])
        driver.find_element_by_id("downloadButton").click()
        try:
            WebDriverWait(driver, TIMEOUT).until(
                EC.presence_of_element_located((By.ID, "thankspopw"))
            )
        except (UnexpectedAlertPresentException, NoSuchWindowException):
            print(u"Invalid track %s (%s by %s)" % (item[0], item[2], item[1]))
        finally:
            time.sleep(TRACK_TIMEOUT)
    driver.quit()
    if os.name == "posix" and headless:
        xvfb.stop()


def get_args():
    """
    Parse provided arguments
    """
    parser = argparse.ArgumentParser(description=u"Automate downloading tracks from deezer")

    parser.add_argument("-a", "--album", help=u"Download album with provided id")
    parser.add_argument("-p", "--playlist", help=u"Download playlist with provided id")
    parser.add_argument("-f", "--favourite", help=u"Download favourite playlist of user with provided id")
    parser.add_argument(
        "--show", dest="headless", default=True, action="store_false",
        help="Show browser window"
    )

    args = parser.parse_args()

    if not args.album or not args.playlist or not args.favourite:
        print u"Provide album id, playlist id, or user id"

    return args


def main():
    """
    Parse arguments and start downloading tracks
    """
    tracks = None
    download_dir = None

    args = get_args()

    if args.playlist:
        tracks, download_dir = get_tracks('playlist', args.playlist)
    elif args.album:
        tracks, download_dir = get_tracks('album', args.album,)
    elif args.favourite:
        tracks, download_dir = get_favourite_tracks(args.favourite)

    if tracks and download_dir:
        download(tracks, download_dir, args.headless)


if __name__ == "__main__":
    main()
