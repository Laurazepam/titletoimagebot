"""
Created on Jan 25, 2019

@author: calicocatalyst
"""

standard_reply_template = '''[Image with added {custom}title]({image_url}) {nsfw}\n\n
{upscaled}\n\n
{warntag}\n\n
---\n\n
^Summon ^me ^with ^/u/title2imagebot ^or ^by ^PMing ^me ^a ^post ^with ^"parse" ^as ^the ^subject. ^| 
[^About](http://calicocat.live/t2ib) ^| 
[^feedback](https://reddit.com/message/compose/?to=CalicoCatalyst&subject=feedback%20{submission_id}) ^| 
[^source](https://github.com/calicocatalyst/titletoimagebot) ^| 
^Fork ^of ^TitleToImageBot'''

minimal_reply_template = '[Processed Image]({image_url}) {nsfw}'

banned_PM_template = '''[Here is your image request]({image_url}) {nsfw}\n\n
{upscaled}\n\n
{warntag}\n\n
---\n\n
Unfortunately, it looks like I'm banned in the sub I was summoned in. 
Feel free to post this link in the comment you summoned me in!.\n\n
---\n\n
Summon me with /u/title2imagebot | 
[About](http://calicocat.live/t2ib) | 
[feedback](https://reddit.com/message/compose/?to=CalicoCatalyst&subject=feedback%20{submission_id}) | 
[source](https://github.com/calicocatalyst/titletoimagebot) | 
Fork of TitleToImageBot
'''

PM_reply_template = '''[Image with added {custom}title]({image_url}) {nsfw}\n\n
{upscaled}\n\n
{warntag}\n\n
---\n\n
Summon me with /u/title2imagebot or by PM! |
[About](http://calicocat.live/t2ib) | 
[feedback](https://reddit.com/message/compose/?to=CalicoCatalyst&subject=feedback%20{submission_id}) | 
[source](https://github.com/calicocatalyst/titletoimagebot) | 
Fork of TitleToImageBot
'''

gif_warning = "Gif processing is currently in alpha. There may be framerate issues if it does manage to parse"

PM_options_warning = "PM processing is in beta and may not correctly process custom arguments"

custom_args_warning = "Custom arguments are currently in alpha. They may not work correctly, and hopefully the bot " \
                      "doesnt crash "

comment_url = "https://reddit.com/comments/{postid}/_/{commentid}"

already_responded_message = "Looks like I've already responded in this thread [Here!]({commentlink})"
