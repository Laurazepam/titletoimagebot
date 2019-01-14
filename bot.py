#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Title2ImageBot
Complete redesign of titletoimagebot by gerenook with non-deprecated apis

This file contains the main methods, and the methods to handle post processing
Image Processing / Imgur Uploading is done in t2utils

"""

author = 'calicocatalyst'
version = '0.2.5'

import praw
from praw.models import MoreComments
import pyimgur
from PIL import Image, ImageDraw, ImageFont

import argparse
import catutils
import t2utils
import re
import requests
import time
import logging

reddit = catutils.auth_reddit_from_config()

template = (
    '[Image with added title]({image_url}) {nsfw}\n\n'
    '{upscaled}---\n\n'

    'Summon me with /u/title2imagebot | '
    '[About](http://insxnity.live/t2ib) | '
    '[feedback](https://reddit.com/message/compose/'
    '?to=CalicoCatalyst&subject=feedback%20{submission_id}) | '
    '[source](https://github.com/calicocatalyst/titletoimagebot) | '
    'Fork of TitleToImageBot'
)

def check_mentions_for_requests(postlimit=10):
    for message in reddit.inbox.all(limit=postlimit):
        process_message(message)
def check_subs_for_posts(postlimit=25):
    subs = t2utils.get_automatic_processing_subs()
    for sub in subs:
        boot = sub == 'boottoobig'
        subr = reddit.subreddit(sub)
        for post in subr.new(limit=postlimit):
            if catutils.check_if_parsed(post.id):
                continue
            title = post.title
            if boot:
                triggers = [',', ';', 'roses']
                if not any(t in title.lower() for t in triggers):
                    logging.debug('Title is probably not part of rhyme, skipping submission')
                    catutils.add_parsed(post.id)
                    continue
            process_submission(post, None, None)
            catutils.add_parsed(post.id)

def _reply_imgur_url(url, submission, source_comment, upscaled=False):
    """
    :param url: Imgur Url
    :type url: str
    :param submission: Submission that the post was on. Reply if source_comment = False
    :type submission: praw.models.Submission
    :param source_comment: Comment that invoked bot if it exists
    :type source_comment: praw.models.Comment
    :returns: True on success, False on failure
    :rtype: bool
    """
    if url == None:

        logging.info('URL returned as none.')
        logging.debug('Checking if Bot Has Already Processed Submission')
        # This should return if the bot has already replied.
        # So, lets check if the bot has already been here and reply with that instead!
        for comment in submission.comments.list():
            if isinstance(comment, MoreComments):
                # See praw docs on MoreComments
                continue
            if not comment or comment.author == None:
                # If the comment or comment author was deleted, skip it
                continue
            if comment.author.name == reddit.user.me().name and 'Image with added title' in comment.body:
                if source_comment:
                    responded_already_reply(source_comment, comment, submission)

        catutils.add_parsed(submission.id)
        # Bot is being difficult and replying multiple times so lets try this :)
        return
    logging.info('Creating reply')
    reply = template.format(
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
    catutils.add_parsed(submission.id)
    return True

def responded_already_reply(source_comment, comment, submission):
    comment_url = "https://reddit.com/comments/%s/_/%s" % (submission.id, comment.id)
    reply = "Looks like I've already responded in this thread [Here!](%s)" % comment_url
    source_comment.reply(reply)
    catutils.add_parsed(source_comment.id)

def process_submission(submission, source_comment, title):
    '''
    Process Submission Using t2utils given the above args, and use the other
        provided function to reply

    :param submission: Submission object containing image to parse
    :type submission: praw.models.submission
    :param source_comment: Comment that invoked if any did, may be NoneType
    :type source_comment: praw.models.Comment
    :param title: Custom title if any (Currently it will always be None)
    :type title: String
    '''

    url = t2utils.process_submission(submission)
    _reply_imgur_url(url, submission, source_comment)

def process_message(message):
    """Process given message (remove, feedback, mark good/bad bot as read)

    :param message: the inbox message, comment reply or username mention
    :type message: praw.models.Message, praw.models.Comment
    """
    # Ignore posts from a deleted user
    # There's a reason the old author put this here, its oddly specific,
    #       So I'm leaving it for now.
    if not message.author:
        return
    author = message.author.name
    subject = message.subject.lower()
    body_original = message.body
    body = message.body.lower()
    if catutils.check_if_parsed(message.id):
        logging.debug("bot.process_message() Message %s Already Parsed, Returning", message.id)
        return
    if message.author.name.lower()=="the-paranoid-android":
        message.reply("Thanks Marv")
        logging.info("Thanking marv")
        catutils.add_parsed(message.id)
        return
    # Skip Messages Sent by Bot
    if author == reddit.user.me().name:
        logging.debug('Message was sent, returning')
        return
    # process message
    if (isinstance(message, praw.models.Comment) and
            (subject == 'username mention' or
             (subject == 'comment reply' and 'u/title2imagebot' in body))):
        # Dont reply to automod.
        if message.author.name.lower() == 'automoderator':
            message.mark_read()
            return

        # This code currently doesn't work on my CentOS, possibly due to dependency issues
        # I'm looking for a fix, but for now this function is disabled and we may have to find
        # A way to do it without regex

        #match = re.match(r'.*u/title2imagebot\s*["“”](.+)["“”].*',
        #                 body_original, re.RegexFlag.IGNORECASE)
        match = False
        title = None
        if match:
            title = match.group(1)
            if len(title) > 512:
                title = None
            else:
                logging.debug('Found custom title: %s', title)
        process_submission(message.submission, message, title)

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
    catutils.add_parsed(message.id)

def main():
    parser = argparse.ArgumentParser(description='Bot To Add Titles To Images')
    parser.add_argument('-d', '--debug', help='Enable Debug Logging', action='store_true')
    parser.add_argument('-l', '--loop', help='Enable Looping Function', action='store_true')
    parser.add_argument('limit', help='amount of submissions/messages to process each cycle',
                        type=int)
    parser.add_argument('interval', help='time (in seconds) to wait between cycles', type=int)

    args = parser.parse_args()
    if args.debug:
        logging.basicConfig(format='%(asctime)s - %(message)s', datefmt='%d-%b-%y %H:%M:%S', level=logging.DEBUG);
    else:
        logging.basicConfig(format='%(asctime)s - %(message)s', datefmt='%d-%b-%y %H:%M:%S', level=logging.INFO);

    logging.info('Bot initialized, processing the last %s submissions/messages every %s seconds' % (args.limit, args.interval))
    logging.debug('Debug Enabled')
    if not args.loop:
        run(args.limit)
        logging.info('Checking Complete, Exiting Program')
        exit(0)
    while True:
        run(args.limit)
        logging.info('Checking Complete')
        time.sleep(args.interval)

def run(limit):
    logging.info('Checking Mentions')
    check_mentions_for_requests(limit)
    logging.info('Checking Autoreply Subs')
    check_subs_for_posts(limit)

if __name__ == '__main__':
    main()
