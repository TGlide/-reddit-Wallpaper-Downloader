import random, os, praw, urllib.request, datetime, glob, ctypes, struct


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


# Make a file_name and a list holding the wallpapers that were already downloaded, as to avoid repetition
file_name = 'wallpapers_downloaded.txt'
if not os.path.isfile(file_name):
    wallpapers_downloaded = []
else:
    with open(file_name, "r") as f:
        wallpapers_downloaded = f.read()
        wallpapers_downloaded = wallpapers_downloaded.split("\n")
        wallpapers_downloaded = list(filter(None, wallpapers_downloaded))

# PRAW instances
reddit = praw.Reddit('bot1')
subreddit = reddit.subreddit('wallpapers')

# Create folder for current date
current_date = datetime.datetime.now()
d_m_y = "{0}.{1}.{2}\\".format(current_date.day, current_date.month, current_date.year)
save_folder = os.getcwd() + "\wallpapers\\" + d_m_y
if not os.path.exists(save_folder):
    os.makedirs(save_folder)

# Download wallpapers from hot posts of the day
print("Fetching wallpapers...")
new_wp_count = 0
for submission in subreddit.hot(limit=15):
    if submission.url not in wallpapers_downloaded:
        if is_image(submission.url):
            wallpapers_downloaded.append(submission.url)
            urllib.request.urlretrieve(submission.url, save_folder + str(submission.id) + submission.url[-4:])
            new_wp_count += 1
print("Printed {0} new wallpapers!".format(new_wp_count))

# Write wallpapers saved to avoid repetition
with open(file_name, 'w') as f:
    for i in wallpapers_downloaded:
        f.write(i + "\n")

# Apply random wallpaper from current day folder
all_files = glob.glob(save_folder + "\\*.png")
all_files.extend(glob.glob(save_folder + "\\*.jpg"))
rng = random.Random()
image_chosen = rng.choice(all_files)
sys_param_info = get_sys_parameters_info()
sys_param_info(20, 0, image_chosen, 3)
