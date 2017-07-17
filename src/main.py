import random
import os
import praw
import urllib.request
import datetime
import glob
import ctypes
import struct
import urllib
import time
import sys
import PIL
import re

from PIL import Image


def is_image(some_url):
    """Defines if a url is an image"""
    if some_url[-4:] != '.jpg' and some_url[-4:] != '.png':
        return False
    else:
        return True


def is_64_windows():
    """Find out how many bits is OS. """
    return struct.calcsize('P') * 8 == 64


def get_sys_parameters_info():
    """Based on if this is 32bit or 64bit returns correct version of SystemParametersInfo function. """
    return ctypes.windll.user32.SystemParametersInfoW if is_64_windows() \
        else ctypes.windll.user32.SystemParametersInfoA


def resize_images(files):
    for img in files:
        try:
            the_img = Image.open(img)
        except OSError:
            try:
                os.remove(img)
                print("Removed " + img + " due to damaged file.")
            except PermissionError as e:
                print(e)
                continue
            continue
        the_img = \
            the_img.resize((int(1366), int(((1366 * int(the_img.size[1])) / int(the_img.size[0])))), Image.ANTIALIAS)
        the_img.save(img)


def is_imgur_album(link):
    """Checks if link is from an imgur album"""
    return "imgur.com/a/" in link


def get_imgur_album_link(link):
    """Gets all image links from an imgur album"""
    page_source = urllib.request.urlopen(link)
    page_source = str(page_source.read())
    # the_match = re.search('<link rel="image_src"\s*href="([^">]*)"/>', page_source)
    the_matches = re.findall('<a href="([^">]*)" class="zoom">', page_source)
    return the_matches


# Make a file_name and a list holding the wallpapers that were already downloaded, as to avoid repetition.
# Also makes a error_log and a list for handling_errors
file_name = 'wallpapers_downloaded.txt'
if not os.path.isfile(file_name):
    wallpapers_downloaded = []
else:
    with open(file_name, "r") as f:
        wallpapers_downloaded = f.read()
        wallpapers_downloaded = wallpapers_downloaded.split("\n")
        wallpapers_downloaded = list(filter(None, wallpapers_downloaded))
error_file = 'error_log.txt'
errors_log = []

# PRAW instances
reddit = praw.Reddit('bot1')
subreddit = reddit.subreddit('wallpapers')

# Create folder for current date
current_date = datetime.datetime.now()
d_m_y = "{0}.{1}.{2}".format(current_date.day, current_date.month, current_date.year)
save_folder = os.getcwd() + "\data\\" + "wallpapers\\" + d_m_y + "\\"
if not os.path.exists(save_folder):
    os.makedirs(save_folder)

# Download wallpapers from hot posts of the day
print("Fetching wallpapers...")
new_wp_count = 0
error_count = 0
for submission in subreddit.hot(limit=20):
    if submission.url not in wallpapers_downloaded:
        # Check if it's a imgur album link
        if is_imgur_album(submission.url):
            the_urls = get_imgur_album_link(submission.url)
            wallpapers_downloaded.append(submission.url)
            for the_url in the_urls:
                the_url = "http:{0}".format(the_url)
                # Try downloading
                try:
                    urllib.request.urlretrieve(the_url, save_folder + str(new_wp_count + 1) + the_url[-4:])
                    wallpapers_downloaded.append("{0} - {1}:".format(d_m_y, str(new_wp_count + 1)))
                    wallpapers_downloaded.append(the_url)
                    new_wp_count += 1
                    print("{0} downloaded...".format(the_url))
                # If it fails, put an error in the error log
                except (urllib.error.HTTPError, urllib.error.URLError) as e:
                    the_error = "{1} - {0}".format(the_url, e)
                    print(the_error)
                    errors_log.append(the_error + " - {0}".format(d_m_y))
                    continue
        # If it's not
        else:
            # Does it end in png/jpg or not? If yes: continue, else: put a .png at the end.
            if is_image(submission.url):
                the_url = submission.url
            else:
                the_url = submission.url + ".png"
            # Try downloading
            try:
                urllib.request.urlretrieve(the_url, save_folder + str(new_wp_count + 1) + the_url[-4:])
                wallpapers_downloaded.append("{0} - {1}:".format(d_m_y, str(new_wp_count + 1)))
                wallpapers_downloaded.append(submission.url)
                new_wp_count += 1
                print("{0} downloaded...".format(the_url))
            # If it fails, put an error in the error log
            except (urllib.error.HTTPError, urllib.error.URLError) as e:
                the_error = "{1} - {0}".format(the_url, e)
                print(the_error)
                errors_log.append(the_error + " - {0}".format(d_m_y))
                continue

print("Downloaded {0} new wallpapers!".format(new_wp_count))

# Write wallpapers saved to avoid repetition
with open(file_name, 'w') as f:
    for i in wallpapers_downloaded:
        f.write(i + "\n")
with open(error_file, 'a') as f:
    for i in errors_log:
        f.write(i + "\n")

# Apply random wallpaper from current day folder
all_files = glob.glob(save_folder + "\\*.png")
all_files.extend(glob.glob(save_folder + "\\*.jpg"))
print("Resizing images...")
resize_images(all_files)
all_files = glob.glob(save_folder + "\\*.png")
all_files.extend(glob.glob(save_folder + "\\*.jpg"))
rng = random.Random()
image_chosen = rng.choice(all_files)
sys_param_info = get_sys_parameters_info()
sys_param_info(20, 0, image_chosen, 3)
time.sleep(3)
