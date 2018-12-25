#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Title2ImageBot
Complete redesign of titletoimagebot by gerenook with non-deprecated apis
Depends:
  praw
  pyimgur
  Pillow

"""

author = 'calicocatalyst'
version = '0.1.1'

import praw
# Updated API Wrapper for imgur that handles the entirety of what we need to do
import pyimgur
from PIL import Image, ImageDraw, ImageFont

import argparse
import catutils
import t2utils
import re
import requests
import time

reddit = catutils.auth_reddit_from_config()

template = (
    '[Image with added title]({image_url})\n\n'
    '{upscaled}---\n\n'
    'Summon me with /u/title2imagebot | '
    '[About](http://insxnity.live/t2ib) | '
    '[feedback](https://reddit.com/message/compose/'
    '?to=CalicoCatalyst&subject=feedback%20{submission_id}) | '
    '[source](https://github.com/calicocatalyst/titletoimagebot) | '
    'Fork of /u/ TitleToImageBot'
)

def check_mentions_for_requests():
    for message in reddit.inbox.all(limit=10):
        process_message(message)

def process_submission(submission, source_comment, title):
    url = t2utils.process_submission(submission)
    _reply_imgur_url(url, submission, source_comment)


def _reply_imgur_url(url, submission, source_comment, upscaled=False):
    """doc todo
    :param url: -
    :type url: str
    :param submission: -
    :type submission: -
    :param source_comment: -
    :type source_comment: -
    :returns: True on success, False on failure
    :rtype: bool
    """
    print('Creating reply')
    if url == None:
        print('Error Somewhere along the way. Marking as parsed and moving on')
        catutils.add_parsed(submission.id)
        # Bot is being difficult and replying multiple times so lets try this :)
        return
    reply = template.format(
        image_url=url,
        upscaled=' (image was upscaled)\n\n' if upscaled else '',
        submission_id=submission.id
    )
    try:
        if source_comment:
            source_comment.reply(reply)
        else:
            submission.reply(reply)
    except praw.exceptions.APIException as error:
        print('Reddit api error, setting nothing TODO set something | %s', error)
        return False
    except Exception as error:
        print('Cannot reply, skipping submission | %s', error)
        return False
    catutils.add_parsed(submission.id)
    return True



def process_message(message):
    """Process given message (remove, feedback, mark good/bad bot as read)

    :param message: the inbox message, comment reply or username mention
    :type message: praw.models.Message, praw.models.Comment
    """
    if not message.author:
        return
    # check db if message was already processed
    author = message.author.name
    subject = message.subject.lower()
    body_original = message.body
    body = message.body.lower()
    if catutils.check_if_parsed(message.id):
        return
    # check if message was sent, instead of received
    if author == reddit.user.me().name:
        print('Message was sent, returning')
        return
    # process message
    if (isinstance(message, praw.models.Comment) and
            (subject == 'username mention' or
             (subject == 'comment reply' and 'u/title2imagebot' in body))):
        # You win this time, AutoModerator
        if message.author.name.lower() == 'automoderator':
            message.mark_read()
            return
        #match = re.match(r'.*u/title2imagebot\s*["“”](.+)["“”].*',
        #                 body_original, re.RegexFlag.IGNORECASE)
        match = False
        title = None
        if match:
            title = match.group(1)
            if len(title) > 512:
                title = None
            else:
                print('Found custom title: %s', title)
        process_submission(message.submission, message, title)

        message.mark_read()
    elif subject.startswith('feedback'):
        print("TODO: add feedback support")
    # mark short good/bad bot comments as read to keep inbox clean
    elif 'good bot' in body and len(body) < 12:
        print('Good bot message or comment reply found, marking as read')
        message.mark_read()
    elif 'bad bot' in body and len(body) < 12:
        print('Bad bot message or comment reply found, marking as read')
        message.mark_read()
    catutils.add_parsed(message.id)

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('limit', help='amount of submissions/messages to process each cycle',
                        type=int)
    parser.add_argument('interval', help='time (in seconds) to wait between cycles', type=int)
    args = parser.parse_args()
    print('Bot initialized, processing the last %s submissions/messages every %s seconds',
                 args.limit, args.interval)
    while True:
        #try:
        check_mentions_for_requests()
        #except Exception as e:
        #    print(e)
        #    continue
        time.sleep(args.interval)
if __name__ == '__main__':
    main()
