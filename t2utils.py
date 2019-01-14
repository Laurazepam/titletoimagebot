# -*- coding: utf-8 -*-
'''
t2utils.def

This module contains important utilities for Title2ImageBot.

java > python
'''
__author__ = 'calicocatalyst'
__version__ = '0.0.7b'


from PIL import Image, ImageDraw, ImageFont, ImageSequence
import praw
import pyimgur
import catutils


import argparse
import json
import logging
import re
import sqlite3
import sys
import time
from io import BytesIO
from logging.handlers import TimedRotatingFileHandler
from math import ceil
from os import remove
from gfycat.client import GfycatClient
import ffmpy

import requests
from imgurpython import ImgurClient
from imgurpython.helpers.error import (ImgurClientError,
                                       ImgurClientRateLimitError)

from prawcore.exceptions import RequestException, ResponseException


def process_submission(submission, commenter=None, customargs=None):
    # TODO implement user selectable options on summons

    # Make sure author account exists
    if not submission.author:
        catutils.add_parsed(submission.id)
        return None;

    sub = submission.subreddit.display_name
    url = submission.url
    title = submission.title
    author = submission.author.name

    # We need to verify everything is good to go
    # Check every item in this list and verify it is 'True'
    # If the submission has been parsed, throw false which will not allow the Bot
    #   To post.
    not_parsed = not catutils.check_if_parsed(submission.id)
    # TODO add gif support

    checks = [not_parsed]

    if not all(checks):
        print("Checks failed, not submitting")
        return;


    if  url.endswith('.gif') or url.endswith('.gifv'):
        # Lets try this again.
        try:
            return process_gif(submission)
        except:
            logging.warn("gif upload failed")
            return None
    # Attempt to grab the images
    try:
        response = requests.get(url)
        img = Image.open(BytesIO(response.content))
    except OSError as error:
        logging.warning('Converting to image failed, trying with <url>.jpg | %s', error)
        try:
            response = requests.get(url + '.jpg')
            img = Image.open(BytesIO(response.content))
        except OSError as error:
            logging.error('Converting to image failed, skipping submission | %s', error)
            return
    except IOError as error:
        print('Pillow couldn\'t process image, marking as parsed and skipping')
        return None;
    except Exception as error:
        print(error)
        print('Exception on image conversion lines.')
        return None;
    try:
        image = RedditImage(img)
    except Exception as error:
        # TODO add error in debug line
        print('Could not create RedditImage with error')
        return None;
    image.add_title(title, False)

    imgur = catutils.get_imgur_client_config()
    imgur_url = image.upload(imgur)

    return imgur_url





#----------
# Check config for a specific variable Value
#----------

import configparser

def check_config_for_sub_threshold(sub, config_file="config.ini"):
    config = configparser.ConfigParser()
    config.read(config_file)
    if config.has_option(sub, 'threshold'):
        return int(config[sub]['threshold'])
    else:
        return -1

def get_automatic_processing_subs(config_file="config.ini"):
    config = configparser.ConfigParser()
    config.read(config_file)
    sections = config.sections()
    sections.remove('RedditAuth')
    sections.remove('ImgurAuth')
    sections.remove('GfyCatAuth')
    return sections


#----------
# process submissions
#----------

'''

'''
import t2gfycat

def process_gif(submission):
    sub = submission.subreddit.display_name
    url = submission.url
    title = submission.title
    author = submission.author.name

    # If its a gifv and hosted on imgur, we're ok, anywhere else I cant verify it works
    if 'imgur' in url and url.endswith("gifv"):
        # imgur will give us a (however large) gif if we ask for it
        # thanks imgur <3
        url = url.rstrip('v')
    # Reddit Hosted gifs are going to be absolute hell, served via DASH which
    #       Can be checked through a fallback url :)
    try:
        response = requests.get(url)
    # Try to get an image if someone linked to imgur but didn't put the .file ext.
    except OSError as error:
        logging.warning('Converting to image failed, trying with <url>.jpg | %s', error)
        try:
            response = requests.get(url + '.jpg')
            img = Image.open(BytesIO(response.content))
        # If that wasn't the case
        except OSError as error:
            logging.error('Converting to image failed, skipping submission | %s', error)
            return
    # Lord knows
    except IOError as error:
        print('Pillow couldn\'t process image, marking as parsed and skipping')
        return None;
    # The nature of this throws tons of exceptions based on what users throw at the bot
    except Exception as error:
        print(error)
        print('Exception on image conversion lines.')
        return None;
    except:
        logging.error("Could not get image from url")
        return None;

    img = Image.open(BytesIO(response.content))
    frames = []

    # Process Gif

    # Loop over each frame in the animated image
    for frame in ImageSequence.Iterator(img):
    	# Draw the text on the frame

        # We'll create a custom RedditImage for each frame to avoid
        #      redundant code

        # TODO: Consolidate this entire method into RedditImage. I want to make
        #       Sure this works before I integrate.

        rFrame = RedditImage(frame)
        rFrame.add_title(title, False)

        frame = rFrame._image
    	# However, 'frame' is still the animated image with many frames
    	# It has simply been seeked to a later frame
    	# For our list of frames, we only want the current frame

    	# Saving the image without 'save_all' will turn it into a single frame image, and we can then re-open it
    	# To be efficient, we will save it to a stream, rather than to file
    	b = BytesIO()
    	frame.save(b, format="GIF")
    	frame = Image.open(b)

        # The first successful image generation was 150MB, so lets see what all
        #       Can be done to not have that happen

    	# Then append the single frame image to a list of frames
    	frames.append(frame)
    # Save the frames as a new image
    path_gif = 'temp.gif'
    path_mp4 = 'temp.mp4'
    frames[0].save(path_gif, save_all=True, append_images=frames[1:])
    # ff = ffmpy.FFmpeg(inputs={path_gif: None},outputs={path_mp4: None})
    # ff.run()

    imgur = catutils.get_imgur_client_config()
    try:
        url = t2gfycat.upload_file(path_gif)
        remove(path_gif)
    except:
        logging.error('Gif Upload Failed, Returning')
        remove(path_gif)
        return None
    # remove(path_mp4)
    return url


#==========
# RedditImage
#==========

class RedditImage:
    """RedditImage class

    :param image: the image
    :type image: PIL.Image.Image
    """
    margin = 10
    min_size = 500
    # TODO find a font for all unicode chars & emojis
    # font_file = 'seguiemj.ttf'
    font_file = 'roboto-emoji.ttf'
    font_scale_factor = 16
    # Regex to remove resolution tag styled as such: '[1000 x 1000]'
    regex_resolution = re.compile(r'\s?\[[0-9]+\s?[xX*×]\s?[0-9]+\]')

    def __init__(self, image):
        self._image = image
        self.upscaled = False
        width, height = image.size
        # upscale small images
        if image.size < (self.min_size, self.min_size):
            if width < height:
                factor = self.min_size / width
            else:
                factor = self.min_size / height
            self._image = self._image.resize((ceil(width * factor),
                                              ceil(height * factor)),
                                             Image.LANCZOS)
            self.upscaled = True
        self._width, self._height = self._image.size
        self._font_title = ImageFont.truetype(
            self.font_file,
            self._width // self.font_scale_factor
        )

    def _split_title(self, title):
        """Split title on [',', ';', '.'] into multiple lines

        :param title: the title to split
        :type title: str
        :returns: split title
        :rtype: list[str]
        """
        lines = ['']
        all_delimiters = [',', ';', '.']
        delimiter = None
        for character in title:
            # don't draw ' ' on a new line
            if character == ' ' and not lines[-1]:
                continue
            # add character to current line
            lines[-1] += character
            # find delimiter
            if not delimiter:
                if character in all_delimiters:
                    delimiter = character
            # end of line
            if character == delimiter:
                lines.append('')
        # if a line is too long, wrap title instead
        for line in lines:
            if self._font_title.getsize(line)[0] + RedditImage.margin > self._width:
                return self._wrap_title(title)
        # remove empty lines (if delimiter is last character)
        return [line for line in lines if line]

    def _wrap_title(self, title):
        """Wrap title

        :param title: the title to wrap
        :type title: str
        :returns: wrapped title
        :rtype: list
        """
        lines = ['']
        line_words = []
        words = title.split()
        for word in words:
            line_words.append(word)
            lines[-1] = ' '.join(line_words)
            if self._font_title.getsize(lines[-1])[0] + RedditImage.margin > self._width:
                lines[-1] = lines[-1][:-len(word)].strip()
                lines.append(word)
                line_words = [word]
        # remove empty lines
        return [line for line in lines if line]

    def add_title(self, title, boot, bg_color='#fff', text_color='#000'):
        """Add title to new whitespace on image

        :param title: the title to add
        :type title: str
        :param boot: if True, split title on [',', ';', '.'], else wrap text
        :type boot: bool
        """
        beta_centering = False
        # remove resolution appended to title (e.g. '<title> [1000 x 1000]')
        title = RedditImage.regex_resolution.sub('', title)
        line_height = self._font_title.getsize(title)[1] + RedditImage.margin
        lines = self._split_title(title) if boot else self._wrap_title(title)
        whitespace_height = (line_height * len(lines)) + RedditImage.margin
        new = Image.new('RGB', (self._width, self._height + whitespace_height), bg_color)
        new.paste(self._image, (0, whitespace_height))
        draw = ImageDraw.Draw(new)
        for i, line in enumerate(lines):
            w,h = self._font_title.getsize(line)
            left_margin = ((self._width - w)/2) if beta_centering else RedditImage.margin
            draw.text((left_margin, i * line_height + RedditImage.margin),
                      line, text_color, self._font_title)
        self._width, self._height = new.size
        self._image = new

    def upload(self, imgur):
        """Upload self._image to imgur

        :param imgur: the imgur api client
        :type imgur: imgurpython.client.ImgurClient
        :param config: imgur image config
        :type config: dict
        :returns: imgur url if upload successful, else None
        :rtype: str, NoneType
        """
        path_png = 'temp.png'
        path_jpg = 'temp.jpg'
        self._image.save(path_png)
        self._image.save(path_jpg)
        try:
            response = imgur.upload_image(path_png, title="Uploaded by /u/Title2ImageBot")
        except:
            # Likely too large
            logging.warning('png upload failed, trying jpg')
            try:
                response = imgur.upload_image(path_jpg, title="Uploaded by /u/Title2ImageBot")
            except:
                logging.error('jpg upload failed, returning')
                return None
        finally:
            remove(path_png)
            remove(path_jpg)
        return response.link
