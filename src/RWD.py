import os
import praw
import urllib.request
import datetime
import glob
import ctypes
import struct
import urllib
import sys
import re

from PIL import Image
from PyQt5 import QtCore
from PyQt5.QtWidgets import (QWidget, QPushButton, QLineEdit,
                             QApplication, QLabel, QHBoxLayout,
                             QVBoxLayout, QMainWindow, QScrollArea, QWidgetItem)
from PyQt5.QtGui import QIcon, QPixmap, QColor


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


def resize_image(file):
    """Resizes images to a width of 1366"""
    try:
        the_img = Image.open(file)
    except OSError:
        try:
            os.remove(file)
            print("Removed " + file + " due to damaged file.")
        except PermissionError as e:
            print(e)
        return
    the_img = the_img.resize((int(1366), int(768)), Image.ANTIALIAS)
    # the_img.resize((int(1366), int(((1366 * int(the_img.size[1])) / int(the_img.size[0])))), Image.ANTIALIAS)
    the_img.save(file)


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


def get_current_count(folder):
    file_list = glob.glob(folder + "*")
    biggest = 0
    for i in file_list:
        file_number = int(re.search('[\\\\](\d+)\.\w{3}', i).group(1))
        if file_number > biggest:
            biggest = file_number
    return biggest


# Make a file_name and a list holding the wallpapers that were already downloaded, as to avoid repetition. yay
# Also makes a error_log and a list for handling_errors
wp_dll_save_file = 'wallpapers_downloaded.txt'
if not os.path.isfile(wp_dll_save_file):
    wallpapers_downloaded = []
else:
    with open(wp_dll_save_file, "r") as f:
        wallpapers_downloaded = f.read()
        wallpapers_downloaded = wallpapers_downloaded.split("\n")
        wallpapers_downloaded = list(filter(None, wallpapers_downloaded))

error_save_file = 'error_log.txt'
error_list = []

# PRAW instances
reddit = praw.Reddit('bot1')
subreddit = reddit.subreddit('wallpapers')

# Create folder for current date
current_date = datetime.datetime.now()
d_m_y = "{0}.{1}.{2}".format(current_date.day, current_date.month, current_date.year)
save_folder = os.getcwd() + "\data\\" + "wallpapers\\" + d_m_y + "\\"
if not os.path.exists(save_folder):
    os.makedirs(save_folder)


# App Classes
class ImageLabel(QLabel):
    """Adaptation of QLabel, as to show an image and change that image to the current wallpaper when clicked."""
    apply_signal = QtCore.pyqtSignal("QString")

    def __init__(self, the_image):
        super().__init__()
        self.the_image = the_image
        self.setPixmap(QPixmap(the_image).scaled(150, 100))

    def mouseReleaseEvent(self, QMouseEvent):
        self.apply_signal.emit(self.the_image)


class BlankImageLabel(QLabel):
    def __init__(self):
        super().__init__()
        self.the_pixmap = QPixmap(150, 100)
        self.the_pixmap.fill(QColor(0, 0, 0, 0))
        self.setPixmap(self.the_pixmap)


class RWDThreadDownloader(QtCore.QThread):
    """PyQT Thread responsible for the downloading of the wallpapers"""
    url_message = QtCore.pyqtSignal("QString")
    enable_button = QtCore.pyqtSignal(bool)
    image_to_display = QtCore.pyqtSignal("QString")

    def __init__(self, the_widget):
        super().__init__()
        self.st_bar = the_widget.st_bar

    def run(self):
        # Counting used for naming the wallpapers
        old_wp_count = get_current_count(save_folder)
        new_wp_count = 0

        the_urls = []
        for submission in subreddit.hot(limit=20):
            if submission.url not in wallpapers_downloaded:
                self.url_message.emit("Fetching links...")
                wallpapers_downloaded.append(submission.url)
                # Check if it's a imgur album link
                if is_imgur_album(submission.url):
                    for imgur_link in get_imgur_album_link(submission.url):
                        the_urls.append("http:{0}".format(imgur_link))
                # If it's not and imgur album link, just add to the list
                else:
                    # Does it end in png/jpg or not? If yes: continue, else: put a .png at the end.
                    if is_image(submission.url):
                        the_urls.append(submission.url)
                    else:
                        the_urls.append(submission.url + ".png")

        # Downloading
        for the_url in the_urls:
            self.url_message.emit("Downloading {0}...".format(the_url))
            try:
                current_count = new_wp_count + old_wp_count + 1
                urllib.request.urlretrieve(the_url, save_folder + str(current_count) + the_url[-4:])
                wallpapers_downloaded.append("{0} - {1}:".format(d_m_y, str(current_count)))
                wallpapers_downloaded.append(the_url)
                new_wp_count += 1
                self.url_message.emit("{0} downloaded!".format(the_url))
                self.image_to_display.emit(save_folder + str(current_count) + the_url[-4:])
            except (urllib.error.HTTPError, urllib.error.URLError) as e:
                the_error = "{1} - {0}".format(the_url, e)
                self.url_message.emit(the_error)
                error_list.append(the_error + " - {0}".format(d_m_y))
                continue
            self.sleep(1)

        self.url_message.emit("Downloaded {0} new wallpapers!".format(new_wp_count))
        self.sleep(1)
        # Write wallpapers saved to avoid repetition
        with open(wp_dll_save_file, 'w') as wp_dll_f:
            for i in wallpapers_downloaded:
                wp_dll_f.write(i + "\n")
        with open(error_save_file, 'a') as error_f:
            for i in error_list:
                error_f.write(i + "\n")
        self.enable_button.emit(True)


class RWDThreadResizer(QtCore.QThread):
    """PyQt Thread responsible for resizing the wallpapers down to size."""
    st_message = QtCore.pyqtSignal("QString")

    def __init__(self):
        super().__init__()
        self.count = 0
        self.image = ""

    def apply_image(self, the_image):
        self.image = the_image
        self.start()

    def run(self):
        resize_image(self.image)
        sys_param_info = get_sys_parameters_info()
        sys_param_info(20, 0, self.image, 3)
        self.st_message.emit("Applied wallpaper")


class RWDWidgetDownload(QWidget):
    """PyQt Widget containing the donwload and resizing action."""

    def __init__(self, app_window, main_widget):
        super().__init__()

        self.main_w = app_window
        self.st_bar = self.main_w.statusBar()

        self.selector_widget = main_widget.selector_widget

        login_label = QLabel("Login:")
        password_label = QLabel("Password:")

        self.login_text = QLineEdit(self)
        self.login_text.resize(self.login_text.sizeHint())
        self.password_text = QLineEdit(self)
        self.password_text.resize(self.password_text.sizeHint())

        self.download_button = QPushButton('Download', self)
        self.download_button.setMinimumHeight(50)
        self.download_button.clicked.connect(self.download)

        # self.stop_button = QPushButton('Stop', self) TODO

        self.download_thread = main_widget.download_thread
        self.download_thread.enable_button.connect(self.download_button.setEnabled)
        self.resize_thread = main_widget.resize_thread

        l_box = QHBoxLayout()
        l_box.addWidget(login_label)
        l_box.addSpacing(password_label.sizeHint().width() - login_label.sizeHint().width())
        l_box.addWidget(self.login_text)

        p_box = QHBoxLayout()
        p_box.addWidget(password_label)
        p_box.addWidget(self.password_text)

        d_box = QHBoxLayout()
        d_box.addSpacing(80)
        d_box.addWidget(self.download_button)

        v_box = QVBoxLayout()
        v_box.addLayout(l_box)
        v_box.addLayout(p_box)
        v_box.addStretch(1)
        v_box.addLayout(d_box)
        v_box.addStretch(1)

        self.setLayout(v_box)

    def download(self):
        # Download wallpapers from hot posts of the day
        self.st_bar.showMessage("Fetching wallpapers...")
        self.download_button.setEnabled(False)
        self.download_thread.start()


class RWDWidgetSelector(QWidget):
    """PyQt Widget responsible for showing the downloaded wallpapers so the user can select them."""

    def __init__(self, app_window, main_widget):
        super().__init__()
        self.main_window = app_window
        self.st_bar = self.main_window.statusBar()

        # Threads
        self.download_thread = main_widget.download_thread
        self.download_thread.image_to_display.connect(self.display_image)
        self.download_thread.finished.connect(self.display_images)
        self.resize_thread = main_widget.resize_thread

        # Labels
        self.image_labels = []
        self.images = []

        # Layouts
        self.hor_layouts = []
        # List Box
        self.listBox = QVBoxLayout(self)
        self.setLayout(self.listBox)
        # Putting the scrollable area inside the list box
        scroll = QScrollArea(self)
        self.listBox.addWidget(scroll)
        scroll.setWidgetResizable(True)
        self.scroll_content = QWidget(scroll)
        # Setting the layout for the scrollable area
        self.scroll_layout = QVBoxLayout()
        self.scroll_content.setLayout(self.scroll_layout)
        scroll.setWidget(self.scroll_content)

    def display_image(self, the_image):
        # TODO: Detect corrupted images
        starting_count = len(self.image_labels)
        if starting_count % 3 == 0:  # New row
            self.hor_layouts.append(QHBoxLayout())
            self.scroll_layout.addLayout(self.hor_layouts[-1])
        self.images.append(the_image)
        self.image_labels.append(ImageLabel(the_image))
        self.image_labels[-1].apply_signal.connect(self.apply_image)
        self.hor_layouts[-1].addWidget(self.image_labels[-1])
        if starting_count % 3 != 2:  # Spaces in between images
            self.hor_layouts[-1].addStretch(1)

    def display_images(self):
        # Get wallpaper file namess
        all_files = glob.glob(save_folder + "\\*.png")
        all_files.extend(glob.glob(save_folder + "\\*.jpg"))
        numb_of_files = len(all_files)

        # Display the wallpapers
        for i in all_files:
            if i not in self.images:
                starting_count = len(self.image_labels)
                if starting_count % 3 == 0:  # New row
                    self.hor_layouts.append(QHBoxLayout())
                    self.scroll_layout.addLayout(self.hor_layouts[-1])
                self.images.append(i)
                self.image_labels.append(ImageLabel(i))
                self.image_labels[-1].apply_signal.connect(self.apply_image)
                self.hor_layouts[-1].addWidget(self.image_labels[-1])
                if starting_count % 3 != 2:  # Spaces in between images
                    self.hor_layouts[-1].addStretch(1)

        # Align layout
        remainder = 3
        for i in range(self.hor_layouts[-1].count()):
            if type(self.hor_layouts[-1].itemAt(i)) == QWidgetItem:
                remainder -= 1
        for j in range(remainder):
            self.hor_layouts[-1].addWidget(BlankImageLabel())
            if j != remainder - 1:
                self.hor_layouts[-1].addStretch(1)

    def apply_image(self, the_image):
        self.resize_thread.apply_image(the_image)


class RWDWidgetMain(QWidget):
    """PyQt Widget that joins RWDWidgetDownload and RWDWidgetSelector."""

    def __init__(self, app_window):
        super().__init__()
        self.main_w = app_window
        self.st_bar = self.main_w.statusBar()

        self.download_thread = RWDThreadDownloader(self)
        self.download_thread.url_message.connect(self.st_bar.showMessage)
        self.resize_thread = RWDThreadResizer()
        self.resize_thread.st_message.connect(self.st_bar.showMessage)

        self.selector_widget = RWDWidgetSelector(app_window, self)

        self.download_widget = RWDWidgetDownload(app_window, self)
        self.download_widget.setMaximumWidth(300)

        self.w_layout = QHBoxLayout()
        self.w_layout.addWidget(self.download_widget)
        self.w_layout.addWidget(self.selector_widget)

        self.setLayout(self.w_layout)


class RWDApp(QMainWindow):
    """Main window for the GUI"""

    def __init__(self):
        super().__init__()
        self.main_widget = RWDWidgetMain(self)
        self.setCentralWidget(self.main_widget)

        self.setGeometry(300, 300, 900, 500)
        self.setWindowTitle('RWD')
        self.setWindowIcon(QIcon(os.getcwd() + '//assets//Reddit-icon.png'))
        self.statusBar().showMessage("Welcome!")
        self.show()

    def add_threads(self, thread_name, thread_value):
        self.threads[thread_name] = thread_value


# Run App
app = QApplication(sys.argv)
ex = RWDApp()
sys.exit(app.exec_())
