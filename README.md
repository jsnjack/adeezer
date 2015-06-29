adeezer
============
###deezer.link requires subscription to download tracks. This script doesn't work anymore
***
###What is it
This script helps to automate downloading tracks from Deezer with [dezeer.link](http://deezer.link/)

###How to install
* Install Firefox browser
* Clone the repository
* It is recommended to use it with virtualenv. Create virtual environment and activate it:
```bash
virtualenv env
```
```bash
source ./env/bin/activate
```
* Install dependencies:
```bash
pip install -r requirements.txt
```
* Install Xvfb server (Linux only)
 * Fedora: `sudo dnf install xorg-x11-server-Xvfb`
 * Ubuntu: `sudo apt-get install xvfb`

###How to use
To download all tracks from playlist run:
```bash
python adeezer.py -p <playlist_id>
```
To download all tracks from album run:
```bash
python adeezer.py -a <album_id>
```
To download all your favourite tracks:
```bash
python adeezer.py -f <user_id>
```

All tracks will be downloaded to `<HOME>/Downloads/<item_id>`

To populate ID3 tags of the downloaded mp3 files based on their name use command:
```bash
python add_tags.py <path_to_folder> "<album_name>"
```

By default in Linux downloading will start in headless mode. To disable headless mode pass `--show_browser` as last argument for the adeezer script.
```bash
python adeezer.py -p <playlist_id> --show_browser
```
