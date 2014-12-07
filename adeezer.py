# Automate downloading Deezer tracks with http://deezer.link
#
# How to use:
#
# - to download all tracks from album:
#   python adeezer.py -a <album_id>
#
# - to download all tracks from playlist:
#   python adeezer.py -p <playlist_id>

import json
import os
import progressbar
import requests
import sys

from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.common.exceptions import UnexpectedAlertPresentException, NoSuchWindowException
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC


# Time to wait for file download
TIMEOUT = 200

tracks = None


def get_tracks(item_type, item_id, file_list):
    """
    Downloads tracks information using Deezer API.
    Returns tracks list
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
    for item in tracks:
        if item['id'] > 0:
            # Check if file already exists
            check_name = u"{artist} - {title} (from WWW.DEEZER.LINK).mp3".format(artist=item['artist']['name'], title=item['title'])
            if not check_name in file_list:
                data.append([item['link'], item['artist']['name'], item['title']])
    return data


def get_download_dir(item_id):
    """
    Creates download directory based on album or playlist id
    """
    download_dir = os.path.expanduser('~') + u'/Downloads/' + str(item_id)
    if not os.path.isdir(download_dir):
        os.makedirs(download_dir)
    return download_dir


if len(sys.argv) == 3:
    item_id = sys.argv[2]
    download_dir = get_download_dir(item_id)
    file_list = os.listdir(download_dir)
    if sys.argv[1] == '-p':
        tracks = get_tracks('playlist', item_id, file_list)
    elif sys.argv[1] == '-a':
        tracks = get_tracks('album', item_id, file_list)

if tracks:
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
            element = WebDriverWait(driver, TIMEOUT).until(
                EC.presence_of_element_located((By.ID, "thankspopw"))
            )
        except (UnexpectedAlertPresentException, NoSuchWindowException):
            print(u"Invalid track %s (%s by %s)" % (item[0], item[2], item[1]))

driver.quit()
