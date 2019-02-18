#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Title2ImageBot
Complete redesign of titletoimagebot by gerenook with non-deprecated apis

This file contains the main methods, and the methods to handle post processing
Image Processing / Imgur Uploading is done in t2utils

"""
import argparse
import configparser
import logging
import re
import sqlite3
import time
from io import BytesIO
from math import ceil
from os import remove

import praw
import praw.exceptions
import praw.models
import pyimgur
import requests
from PIL import Image, ImageDraw, ImageFont, ImageSequence
from gfypy import gfycat

import messages

__author__ = 'calicocatalyst'
__version__ = '0.3b'


class TitleToImageBot(object):
    def __init__(self, config, database):
        """

        :type database: BotDatabase
        :type config: Configuration
        """
        self.config = config
        self.reddit = self.config.auth_reddit_from_config()
        self.imgur = self.config.get_imgur_client_config()
        self.gfycat = self.config.get_gfycat_client_config()

        self.database = database

    def check_mentions_for_requests(self, postlimit=10):
        for message in self.reddit.inbox.all(limit=postlimit):
            self.process_message(message)

    def check_subs_for_posts(self, postlimit=25):
        subs = self.config.get_automatic_processing_subs()
        for sub in subs:
            subr = self.reddit.subreddit(sub)
            for post in subr.new(limit=postlimit):
                if self.database.submission_exists(post.id):
                    continue
                title = post.title

                has_triggers = self.config.configfile.has_option(sub, 'triggers')
                has_threshold = self.config.configfile.has_option(sub, 'threshold')

                if has_triggers:
                    triggers = str(self.config.configfile[sub]['triggers']).split('|')
                    if not any(t in title.lower() for t in triggers):
                        logging.info('Title %s doesnt appear to contain any of %s, adding to parsed and skipping'
                                     % (title, self.config.configfile[sub]["triggers"]))
                        self.database.submission_insert(post.id, post.author.name, title, post.url)
                        continue
                else:
                    logging.debug('No triggers were defined for %s, not checking' % sub)

                if has_threshold:
                    threshold = int(self.config.configfile[sub]['threshold'])
                    if post.score < threshold:
                        logging.debug('Threshold not met, not adding to parsed, just ignoring')
                        continue
                    else:
                        logging.debug('Threshold met, posting and adding to parsed')
                else:
                    logging.debug('No threshold for %s, replying to everything :)' % sub)
                self.process_submission(post, None, None)
                if self.database.submission_exists(post.id):
                    continue
                else:
                    self.database.submission_insert(post.id, post.author.name, title, post.url)

    def reply_imgur_url(self, url, submission, source_comment, upscaled=False):
        """
        :param upscaled:
        :param url: Imgur Url
        :type url: str
        :param submission: Submission that the post was on. Reply if source_comment = False
        :type submission: praw.models.Submission
        :param source_comment: Comment that invoked bot if it exists
        :type source_comment: praw.models.Comment
        :returns: True on success, False on failure
        :rtype: bool
        """
        if url is None:

            logging.info('URL returned as none.')
            logging.debug('Checking if Bot Has Already Processed Submission')
            # This should return if the bot has already replied.
            # So, lets check if the bot has already been here and reply with that instead!
            for comment in submission.comments.list():
                if isinstance(comment, praw.models.MoreComments):
                    # See praw docs on MoreComments
                    continue
                if not comment or comment.author is None:
                    # If the comment or comment author was deleted, skip it
                    continue
                if comment.author.name == self.reddit.user.me().name and 'Image with added title' in comment.body:
                    if source_comment:
                        self.responded_already_reply(source_comment, comment, submission)

            if self.database.message_exists(source_comment.id):
                return
            else:
                self.database.message_insert(source_comment.id, source_comment.author.name, "comment reply",
                                             source_comment.body)
            # Bot is being difficult and replying multiple times so lets try this :)
            return
        logging.info('Creating reply')
        reply = messages.standard_reply_template.format(
            image_url=url,
            nsfw="(NSFW)" if submission.over_18 else '',
            upscaled=' (image was upscaled)\n\n' if upscaled else '',
            submission_id=submission.id
        )
        try:
            if source_comment:
                source_comment.reply(reply)
            else:
                submission.reply(reply)
        except praw.exceptions.APIException as error:
            logging.error('Reddit api error, we\'ll try to repost later | %s', error)
            return False
        except Exception as error:
            logging.error('Cannot reply, skipping submission | %s', error)
            return False
        self.database.submission_insert(submission.id, submission.author.name, submission.title, url)
        return True

    def responded_already_reply(self, source_comment, comment, submission):
        com_url = messages.comment_url.format(postid=submission.id, commentid=comment.id)
        reply = messages.already_responded_message.format(commentlink=com_url)

        source_comment.reply(reply)
        self.database.message_insert(source_comment.id, comment.author.name, "comment reply", source_comment.body)

    def process_submission(self, submission, source_comment, title):
        """
        Process Submission Using t2utils given the above args, and use the other
            provided function to reply

        :param submission: Submission object containing image to parse
        :type submission: praw.models.submission
        :param source_comment: Comment that invoked if any did, may be NoneType
        :type source_comment: praw.models.Comment, None
        :param title: Custom title if any (Currently it will always be None)
        :type title: String
        """
        _ = title
        url = self.process_image_submission(submission)
        self.reply_imgur_url(url, submission, source_comment)

    def process_message(self, message):
        """Process given message (remove, feedback, mark good/bad bot as read)
    
        :param message: the inbox message, comment reply or username mention
        :type message: praw.models.Message, praw.models.Comment
        """
        if not message.author:
            return
        message_author = message.author.name
        subject = message.subject.lower()
        # body_original = message.body
        body = message.body.lower()
        if self.database.message_exists(message.id):
            logging.debug("bot.process_message() Message %s Already Parsed, Returning", message.id)
            return
        if message_author.lower() == "the-paranoid-android":
            message.reply("Thanks Marv")
            logging.info("Thanking marv")
            self.database.message_insert(message.id, message_author, message.subject.lower(), body)
            return
        # Skip Messages Sent by Bot
        if message_author == self.reddit.user.me().name:
            logging.debug('Message was sent, returning')
            return
        # process message
        if (isinstance(message, praw.models.Comment) and
                (subject == 'username mention' or
                 (subject == 'comment reply' and 'u/title2imagebot' in body))):

            if message.author.name.lower() == 'automoderator':
                message.mark_read()
                return

            match = None
            title = None
            if match:
                title = match.group(1)
                if len(title) > 512:
                    title = None
                else:
                    logging.debug('Found custom title: %s', title)
            self.process_submission(message.submission, message, title)

            message.mark_read()
        elif subject.startswith('feedback'):
            logging.debug("TODO: add feedback forwarding support")
        # mark short good/bad bot comments as read to keep inbox clean
        elif 'good bot' in body and len(body) < 12:
            logging.debug('Good bot message or comment reply found, marking as read')
            message.mark_read()
        elif 'bad bot' in body and len(body) < 12:
            logging.debug('Bad bot message or comment reply found, marking as read')
            message.mark_read()

        # Check if the bot has processed already, if so we dont need to do anything. If it hasn't,
        # add it to the database and move on
        if self.database.message_exists(message.id):
            logging.debug("bot.process_message() Message %s Already Parsed, no need to add", message.id)
            return
        else:
            self.database.message_insert(message.id, message_author, subject, body)

    # noinspection PyUnusedLocal
    def process_image_submission(self, submission, commenter=None, customargs=None):
        """

        :param submission: Submission that points to a URL we need to process
        :type submission: praw.models.Submission
        :param commenter: Commenter who requested the thing
        :type commenter: praw.models.Redditor
        :param customargs: List of custom arguments. Not implemented, but lets be ready for it once we figure out how
        :type customargs: List
        :return: URL the image has been uploaded to, None if it failed to upload
        :rtype: String, None
        """
        # TODO implement user selectable options on summons

        # Make sure author account exists
        if not submission.author:
            self.database.submission_insert(submission.id, submission.author.name, submission.title, submission.url)
            return None

        sub = submission.subreddit.display_name
        url = submission.url
        title = submission.title
        submission_author = submission.author.name

        # We need to verify everything is good to go
        # Check every item in this list and verify it is 'True'
        # If the submission has been parsed, throw false which will not allow the Bot
        #   To post.
        not_parsed = not self.database.submission_exists(submission.id)

        checks = [not_parsed]

        if not all(checks):
            print("Checks failed, not submitting")
            return None

        if url.endswith('.gif') or url.endswith('.gifv'):
            # Lets try this again.
            # noinspection PyBroadException
            try:
                return self.process_gif(submission)
            except Exception as ex:
                logging.warning("gif upload failed with %s" % ex)
                return None
        # Attempt to grab the images
        try:
            response = requests.get(url)
            img = Image.open(BytesIO(response.content))
        except (OSError, IOError) as error:
            logging.warning('Converting to image failed, trying with <url>.jpg | %s', error)
            try:
                response = requests.get(url + '.jpg')
                img = Image.open(BytesIO(response.content))
            except (OSError, IOError) as error:
                logging.error('Converting to image failed, skipping submission | %s', error)
                return None
        except Exception as error:
            print(error)
            print('Exception on image conversion lines.')
            return None
        # noinspection PyBroadException
        try:
            image = RedditImage(img)
        except Exception as error:
            print('Could not create RedditImage with %s' % error)
            return None
        image.add_title(title, False)

        imgur_url = self.upload(image)

        return imgur_url

    def process_gif(self, submission):
        """

        :param submission:
        :type submission: praw.models.Submission
        """
        # sub = submission.subreddit.display_name
        url = submission.url
        title = submission.title
        # author = submission.author.name

        # If its a gifv and hosted on imgur, we're ok, anywhere else I cant verify it works
        if 'imgur' in url and url.endswith("gifv"):
            # imgur will give us a (however large) gif if we ask for it
            # thanks imgur <3
            url = url.rstrip('v')
        # Reddit Hosted gifs are going to be absolute hell, served via DASH which
        #       Can be checked through a fallback url :)
        try:
            response = requests.get(url)
        # The nature of this throws tons of exceptions based on what users throw at the bot
        except Exception as error:
            print(error)
            print('Exception on image conversion lines.')
            return None

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

            r_frame = RedditImage(frame)
            r_frame.add_title(title, False)

            frame = r_frame.image
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
        # path_mp4 = 'temp.mp4'
        frames[0].save(path_gif, save_all=True, append_images=frames[1:])
        # ff = ffmpy.FFmpeg(inputs={path_gif: None},outputs={path_mp4: None})
        # ff.run()

        # noinspection PyBroadException
        try:
            url = self.upload_to_gfycat(path_gif).url
            remove(path_gif)
        except Exception as ex:
            logging.error('Gif Upload Failed with %s, Returning' % ex)
            remove(path_gif)
            return None
        # remove(path_mp4)
        return url

    def upload(self, reddit_image):
        """Upload self._image to imgur

        :type reddit_image: RedditImage
        :param reddit_image:
        :returns: imgur url if upload successful, else None
        :rtype: str, NoneType
        """
        path_png = 'temp.png'
        path_jpg = 'temp.jpg'
        reddit_image.image.save(path_png)
        reddit_image.image.save(path_jpg)
        # noinspection PyBroadException
        try:
            response = self.upload_to_imgur(path_png)
        except Exception as ex:
            # Likely too large
            logging.warning('png upload failed with %s, trying jpg' % ex)
            try:
                response = self.upload_to_imgur(path_jpg)
            except Exception as ex:
                logging.error('jpg upload failed with %s, returning' % ex)
                return None
        finally:
            remove(path_png)
            remove(path_jpg)
        return response.link

    def upload_to_imgur(self, local_image_url):
        response = self.imgur.upload_image(local_image_url, title="Uploaded by /u/Title2ImageBot")
        return response

    def upload_to_gfycat(self, local_gif_url):
        generated_gfycat = self.gfycat.upload_file(local_gif_url)
        return generated_gfycat

    def run(self, limit):
        logging.info('Checking Mentions')
        self.check_mentions_for_requests(limit)
        logging.info('Checking Autoreply Subs')
        self.check_subs_for_posts(limit)


class RedditImage:
    """RedditImage class

    :param image: the image
    :type image: PIL.Image.Image
    """
    margin = 10
    min_size = 500
    # TODO find a font for all unicode chars & emojis
    # font_file = 'seguiemj.ttf'
    font_file = 'NotoSans-Regular.ttf'
    font_scale_factor = 16
    # Regex to remove resolution tag styled as such: '[1000 x 1000]'
    regex_resolution = re.compile(r'\s?\[[0-9]+\s?[xX*×]\s?[0-9]+\]')

    def __init__(self, image):
        self.image = image
        self.upscaled = False
        width, height = image.size
        # upscale small images
        if image.size < (self.min_size, self.min_size):
            if width < height:
                factor = self.min_size / width
            else:
                factor = self.min_size / height
            self.image = self.image.resize((ceil(width * factor),
                                            ceil(height * factor)),
                                           Image.LANCZOS)
            self.upscaled = True
        self._width, self._height = self.image.size
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

        :param text_color:
        :param bg_color:
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
        new.paste(self.image, (0, whitespace_height))
        draw = ImageDraw.Draw(new)
        for i, line in enumerate(lines):
            w, h = self._font_title.getsize(line)
            left_margin = ((self._width - w) / 2) if beta_centering else RedditImage.margin
            draw.text((left_margin, i * line_height + RedditImage.margin),
                      line, text_color, self._font_title)
        self._width, self._height = new.size
        self.image = new


class Configuration(object):

    def __init__(self, config_file):
        self._config = configparser.ConfigParser()
        self._config.read(config_file)
        self.configfile = self._config

    def get_automatic_processing_subs(self):
        sections = self._config.sections()

        config_internal_sections = ["RedditAuth", "GfyCatAuth", "ImgurAuth", "IgnoreList"]

        for i in sections:
            if i in config_internal_sections:
                sections.remove(i)
        # TODO: fix this
        sections.remove("IgnoreList")
        sections.remove("ImgurAuth")
        return sections

    def get_user_ignore_list(self):
        ignorelist = []
        for i in self._config.items("IgnoreList"):
            ignorelist.append(i[0])
        return ignorelist

    def get_gfycat_client_config(self):
        client_id = self._config['GfyCatAuth']['publicKey']
        client_secret = self._config['GfyCatAuth']['privateKey']
        username = self._config['GfyCatAuth']['username']
        password = self._config['GfyCatAuth']['password']
        client = gfycat.GfyCatClient(client_id, client_secret, username, password)
        return client

    def auth_reddit_from_config(self):
        return (praw.Reddit(client_id=self._config['RedditAuth']['publicKey'],
                            client_secret=self._config['RedditAuth']['privateKey'],
                            username=self._config['RedditAuth']['username'],
                            password=self._config['RedditAuth']['password'],
                            user_agent=self._config['RedditAuth']['userAgent']))

    def get_imgur_client_config(self):
        return pyimgur.Imgur(self._config['ImgurAuth']['publicKey'])


class BotDatabase(object):
    def __init__(self, db_filename):
        self._sql_conn = sqlite3.connect(db_filename)
        self._sql = self._sql_conn.cursor()

    def message_exists(self, message_id):
        """Check if message exists in messages table

        :param message_id: the message id to check
        :type message_id: str
        :returns: True if message was found, else False
        :rtype: bool
        """
        self._sql.execute('SELECT EXISTS(SELECT 1 FROM messages WHERE id=?)', (message_id,))
        if self._sql.fetchone()[0]:
            return True
        else:
            return False

    def submission_exists(self, message_id):
        self._sql.execute('SELECT EXISTS(SELECT 1 FROM submissions WHERE id=?)', (message_id,))
        if self._sql.fetchone()[0]:
            return True
        else:
            return False

    def message_parsed(self, message_id):
        # TODO: Fix the implementation of this
        self._sql.execute('SELECT EXISTS(SELECT 1 FROM messages WHERE id=? AND parsed=1)', (message_id,))
        if self._sql.fetchone()[0]:
            return True
        else:
            return False

    def message_insert(self, message_id, message_author, subject, body):
        """Insert message into messages table"""
        self._sql.execute('INSERT INTO messages (id, author, subject, body) VALUES (?, ?, ?, ?)',
                          (message_id, message_author, subject, body))
        self._sql_conn.commit()

    def submission_select(self, submission_id):
        """Select all attributes of submission
        :param submission_id: the submission id
        :type submission_id: str
        :returns: query result, None if id not found
        :rtype: dict, NoneType
        """
        self._sql.execute('SELECT * FROM submissions WHERE id=?', (submission_id,))
        result = self._sql.fetchone()
        if not result:
            return None
        return {
            'id': result[0],
            'author': result[1],
            'title': result[2],
            'url': result[3],
            'imgur_url': result[4],
            'retry': result[5],
            'timestamp': result[6]
        }

    def submission_insert(self, submission_id, submission_author, title, url):
        """Insert submission into submissions table"""
        self._sql.execute('INSERT INTO submissions (id, author, title, url) VALUES (?, ?, ?, ?)',
                          (submission_id, submission_author, title, url))
        self._sql_conn.commit()

    def submission_set_retry(self, submission_id, delete_message=False, message=None):
        """Set retry flag for given submission, delete message from db if desired
        :param submission_id: the submission id to set retry
        :type submission_id: str
        :param delete_message: if True, delete message from messages table
        :type delete_message: bool
        :param message: the message to delete
        :type message: praw.models.Comment, NoneType
        """
        self._sql.execute('UPDATE submissions SET retry=1 WHERE id=?', (submission_id,))
        if delete_message:
            if not message:
                raise TypeError('If delete_message is True, message must be set')
            self._sql.execute('DELETE FROM messages WHERE id=?', (message.id,))
        self._sql_conn.commit()

    def submission_clear_retry(self, submission_id):
        """Clear retry flag for given submission_id
        :param submission_id: the submission id to clear retry
        :type submission_id: str
        """
        self._sql.execute('UPDATE submissions SET retry=0 WHERE id=?', (submission_id,))
        self._sql_conn.commit()

    def submission_set_imgur_url(self, submission_id, imgur_url):
        """Set imgur url for given submission
        :param submission_id: the submission id to set imgur url
        :type submission_id: str
        :param imgur_url: the imgur url to update
        :type imgur_url: str
        """
        self._sql.execute('UPDATE submissions SET imgur_url=? WHERE id=?',
                          (imgur_url, submission_id))
        self._sql_conn.commit()


comment_file_path = "parsed.txt"


def main():
    parser = argparse.ArgumentParser(description='Bot To Add Titles To Images')
    parser.add_argument('-d', '--debug', help='Enable Debug Logging', action='store_true')
    parser.add_argument('-l', '--loop', help='Enable Looping Function', action='store_true')
    parser.add_argument('limit', help='amount of submissions/messages to process each cycle',
                        type=int)
    parser.add_argument('interval', help='time (in seconds) to wait between cycles', type=int)

    args = parser.parse_args()
    if args.debug:
        logging.basicConfig(format='%(asctime)s - %(message)s', datefmt='%d-%b-%y %H:%M:%S', level=logging.DEBUG)
    else:
        logging.basicConfig(format='%(asctime)s - %(message)s', datefmt='%d-%b-%y %H:%M:%S', level=logging.INFO)

    configuration = Configuration("config.ini")
    database = BotDatabase("t2ib.sqlite")

    logging.info('Bot initialized, processing the last %s submissions/messages every %s seconds' % (args.limit,
                                                                                                    args.interval))

    bot = TitleToImageBot(configuration, database)

    logging.debug('Debug Enabled')
    if not args.loop:
        bot.run(args.limit)
        logging.info('Checking Complete, Exiting Program')
        exit(0)
    while True:
        bot.run(args.limit)
        logging.info('Checking Complete')
        time.sleep(args.interval)


if __name__ == '__main__':
    main()
