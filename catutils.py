"""
catutils.py

Basic Utilities for Python Reddit Api Wrapper Bots

"""

__author__ = 'calicocatalyst'
__version__ = '0.0.1'

comment_file_path = "parsed.txt"

# ----------------------
# essential praw functions
# ----------------------

def add_parsed(id):
    with open(comment_file_path, 'a+') as f:
        f.write(id)

def check_if_parsed(id):
    with open(comment_file_path,'r+') as f:
        return id in f.read();

# ----------------------
# Tools for consise PRAW use
# ----------------------

import praw
import configparser

def auth_reddit_from_config(config_file='config.ini'):
    config = configparser.ConfigParser()
    config.read(config_file)
    return(praw.Reddit(client_id=config['RedditAuth']['publicKey'],
        client_secret=config['RedditAuth']['privateKey'],
        username=config['RedditAuth']['username'],
        password=config['RedditAuth']['password'],
        user_agent=config['RedditAuth']['userAgent']))

# Workaround for streaming EVERYTHING from the sub
def submissions_and_comments(subreddit, **kwargs):
    results = []
    results.extend(subreddit.new(**kwargs))
    results.extend(subreddit.comments(**kwargs))
    results.sort(key=lambda post: post.created_utc, reverse=True)
    return results

# ----------------------
# pyimgur
# ----------------------

import pyimgur

def get_imgur_client_config(config_file="config.ini"):
    config = configparser.ConfigParser()
    config.read(config_file)
    return(pyimgur.Imgur(config['ImgurAuth']['publicKey']))

# ----------------------
# Interact with ModTools Usernotes Database
# ----------------------

import pytbun

def save_new_user_note(sub, user, note, mod, warn):
    # TODO snake case pytbun
    return pytbun.CompileandZipUsernotes(
        r,
        pytbun.PullandUnzipUsernotes(r, sub)[0],
            pytbun.makeNewNote(PullandUnzipUsernotes(r, sub)[1],user,note,pytbun.getModeratorIndex(r,sub,mod),'',pytbun.getWarningIndex(r,sub,warn)),
        sub)
# TODO this
# def retrieve_user_note(sub, user):
#     continue
