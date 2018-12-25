# -*- coding: utf-8 -*-
'''
t2utils.def

This module contains important utilities for Title2ImageBot.

java > python
'''
__author__ = 'calicocatalyst'
__version__ = '0.0.1'


from PIL import Image, ImageDraw, ImageFont
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

import requests
from imgurpython import ImgurClient
from imgurpython.helpers.error import (ImgurClientError,
                                       ImgurClientRateLimitError)

from prawcore.exceptions import RequestException, ResponseException


def process_submission(submission, commenter=None, customargs=None):
    # TODO implement user selectable options on summons

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
    is_not_gif = url.endswith('.gif') or url.endswith('.gifv')

    checks = [not_parsed]

    if not all(checks):
        print("Checks failed, not submitting")
        return;

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

    image = RedditImage(img)
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
    return sections


#----------
# process submissions
#----------

'''

'''

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
    font_file = 'roboto.ttf'
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
        # remove resolution appended to title (e.g. '<title> [1000 x 1000]')
        title = RedditImage.regex_resolution.sub('', title)
        line_height = self._font_title.getsize(title)[1] + RedditImage.margin
        lines = self._split_title(title) if boot else self._wrap_title(title)
        whitespace_height = (line_height * len(lines)) + RedditImage.margin
        new = Image.new('RGB', (self._width, self._height + whitespace_height), bg_color)
        new.paste(self._image, (0, whitespace_height))
        draw = ImageDraw.Draw(new)
        for i, line in enumerate(lines):
            draw.text((RedditImage.margin, i * line_height + RedditImage.margin),
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
            logging.warning('png upload failed, trying jpg | %s', error)
            try:
                response = imgur.upload_image(path_jpg, title="Uploaded by /u/Title2ImageBot")
            except:
                logging.error('jpg upload failed, returning | %s', error)
                return None
        finally:
            remove(path_png)
            remove(path_jpg)
        return response.link
