"""
Created on Jan 25, 2019

@author: Insxnity
"""

standard_reply_template = '''[Image with added {custom}title]({image_url}) {nsfw}\n\n
{upscaled}---\n\n
Summon me with /u/title2imagebot | 
[About](http://insxnity.live/t2ib) | 
[feedback](https://reddit.com/message/compose/?to=CalicoCatalyst&subject=feedback%20{submission_id}) | 
[source](https://github.com/calicocatalyst/titletoimagebot) | 
Fork of TitleToImageBot'''

minimal_reply_template = '[Processed Image]({image_url}) {nsfw}'

comment_url = "https://reddit.com/comments/{postid}/_/{commentid}"

already_responded_message = "Looks like I've already responded in this thread [Here!]({commentlink})"
