# Mediocre attempt at an API Wrapper that covers what I need it to for TitleToImageBot
# TODO snake_case the variable names :p

# Where to request a token
TOKEN_ENDPOINT = 'https://api.gfycat.com/v1/oauth/token'
# This is the url where you need to request some info from the GfyCat API
REQUEST_ENDPOINT = 'https://api.gfycat.com/v1/gfycats'
# URL where to upload video
FILE_UPLOAD_ENDPOINT = 'https://filedrop.gfycat.com/'
# The URL for checking the upload status
FILE_UPLOAD_STATUS_ENDPOINT = 'https://api.gfycat.com/v1/gfycats/fetch/status/{}'
# URL for what your GfyCat URL is going to be
gfyUrl = 'https://gfycat.com/{}'

import requests as req
import time, json

import logging

import catutils

# Client ID and Secret should be requested at https://developers.gfycat.com/


def upload_file(file_name):
    auth_headers = _auth_headers()
    gfy_id = _get_url(auth_headers)
    _upload_file(gfy_id, file_name)
    return gfyUrl.format(gfy_id)


# Create auth header
def _auth_headers():


    body = json.dumps(catutils.get_gfycat_body_config())

    # Get a token
    token = req.post(TOKEN_ENDPOINT, json=body)
    access_token = token.json().get("access_token")

    logging.debug("access_token: " + access_token)

    auth_headers = {
        "Authorization": "Bearer {}".format(access_token)
    }

    return auth_headers

# Get custom url from GfyCat
def _get_url(headers):
    # Ask GfyCat for an URL
    gfy_return = req.post(REQUEST_ENDPOINT, json=gifParam, headers=headers)
    # Get the name out of the data it sends
    gfy_id = gfy_return.json().get("gfyname")

    logging.debug("gfyID: " + gfy_id)

    return gfy_id


def _upload_file(gfyID, videoName):
    logging.debug("Attempting to Upload to GfyCat")

    uploadStatus = "encoding"

    with open(videoName, 'rb') as payload:
        files = {
            'key': gfyID,
            'file': (videoName, payload),
        }
        res = req.post(FILE_UPLOAD_ENDPOINT, files=files)

    # Check if it's done uploading
    while uploadStatus != "complete":
        checkReturn = req.get(FILE_UPLOAD_STATUS_ENDPOINT.format(gfyID))
        uploadStatus = checkReturn.json().get("task")

        logging.debug("Status: " + uploadStatus)
        time.sleep(5)
