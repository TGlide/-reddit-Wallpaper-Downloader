# Reddit Wallpaper Downloader
This is a simple tool I've created for day to day use to fetch wallpapers from https://www.reddit.com/r/wallpapers/.

- It fetches up to 15 wallpapers from the hot section, attempts to download them and puts in a folder with a time stamp. 
e.g. A wallpaper from 20/03/2017 would be in /folder_where_main.py_is_located/data/wallpapers/20.03.2017/

- After downloading them, it randomly sets one of the downloaded files as the desktop background (Windows Only)

## Installation and Updating
With Python installed, simply install PRAW (The reddit API) by typing the following on the console(CMD):

`pip install praw`

If the program states that the Reddit API is outdated, simply run:

`pip install --upgrade praw`

Having done that, clone the repository into the desired folder.

## Usage
Simply run main.py to fetch and set new wallpapers. 

To run at startup, create a main.py shortcut, and link it to the Windows Startup Applications.

## Contributing
Pull requests and bug reports are accepted, just be educated please :)

## Planned Features
- [x] Convert imgur links to image links using imgur api
- [ ] Detect slashes and correct links using string manipulation


## Authors
- TGLIDE

## License
This project is licensed under the GNU GNL v3 License - See LICENSE.md for details.
