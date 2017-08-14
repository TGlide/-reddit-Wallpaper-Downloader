# Reddit WallLoad
This is a simple tool I've created for day to day use to fetch wallpapers from https://www.reddit.com/r/wallpapers/.

- It fetches up to 30 wallpapers from the hot section, attempts to download them and puts in a folder with a time stamp. 
e.g. A wallpaper from 20/03/2017 would be in /folder_where_main.py_is_located/data/wallpapers/20.03.2017/

- After downloading them, it displays the images for you to choose (Windows Only)

## Installation and Updating
With Python installed, simply install PRAW (The reddit API) by typing the following on the console(CMD):

`pip install praw`

If the program states that the Reddit API is outdated, simply run:

`pip install --upgrade praw`

Also install PyQt 5 running the following on the console:

`pip install pyqt5`

Having done that, clone the repository into the desired folder, and it's ready for use!

## Usage
Simply run RWD.py to fetch and set new wallpapers. 

To run at startup, create a RWD.py shortcut, and link it to the Windows Startup Applications.

If you wish for the program to run without displaying the python console, simply rename RWD.py to RWD.pyw. (For windows only)

## Contributing
Pull requests and bug reports are accepted, just be educated please :)

## Planned Features
- [x] Convert imgur links to image links using imgur api
- [ ] Detect slashes and correct links using string manipulation
- [ ] Add upvote buttons for each wallpaper
- [ ] Add delete option for each wallpaper
- [ ] Add subreddit chooser
- [ ] Add favorites section


## Authors
- TGLIDE

## License
This project is licensed under the GNU GNL v3 License - See LICENSE.md for details.
