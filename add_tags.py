#Adds tags based on file name to the download Deezer mp3 files
#Usage:
#    python add_tags.py <path_to_the_folder> "<album_name>"

import os
import progressbar
import sys

from mutagen.id3 import TIT2, TALB, TPE1, TPE2
from mutagen.mp3 import MP3, HeaderNotFoundError


download_folder = sys.argv[1]
album_name = sys.argv[2].decode("utf-8")


def get_tags(item):
    """
    Get tags from filename
    """
    name_string = item.decode("utf-8").replace(u" (from WWW.DEEZER.LINK).mp3", u"")
    names = name_string.split(u" - ")
    return names[0], names[1]

if os.path.exists(download_folder):
    file_list = os.listdir(download_folder)
    pbar = progressbar.ProgressBar()
    for item in pbar(file_list):
        if item.split(".")[-1] == u"mp3":
            try:
                artist, title = get_tags(item)
                audio_file = MP3(download_folder + u'/' + item.decode("utf-8"))
                audio_file["TIT2"] = TIT2(encoding=3, text=title)
                audio_file["TPE1"] = TPE1(encoding=3, text=artist)
                audio_file["TALB"] = TALB(encoding=3, text=album_name)
                audio_file["TPE2"] = TPE2(encoding=3, text=album_name)
                audio_file.save()
            except HeaderNotFoundError:
                print u"Error during adding tags to %s" % item

