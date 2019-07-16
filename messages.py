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


site19_template = '''[Image with [REDACTED] {custom}title]({image_url}) {nsfw}\n\n
{upscaled}\n\n
{warntag}\n\n
---\n\n
^Summon ^me ^with ^[REDACTED] ^| 
[^church ^of ^peanut](http://reddit.com/r/churchofpeanut) ^| 
[^Which ^SCP ^would ^you ^yiff ^and ^why ^is ^it ^1471](https://reddit.com/message/compose/?to=CalicoCatalyst&subject=feedback%20{submission_id}) ^| 
[^source](https://github.com/calicocatalyst/titletoimagebot) ^| 
^Fork ^of ^[REDACTED]'''



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

de_reply_template = '''[Bild mit hinzugefügtem {custom}Titel]({image_url}) {nsfw}\n\n
{upscaled}\n\n
{warntag}\n\n
---\n\n
^Rufen ^Sie ^mich ^mit ^/u/Title2ImageBot ^an ^oder ^senden ^Sie ^mir ^einen ^Link ^zu ^einem ^Beitrag ^mit 
^dem ^Betreff ^"parse". ^| 
[^Info](http://calicocat.live/t2ib) ^| 
[^Schrei ^mich ^an ^oder ^hilf ^mir ^zu ^übersetzen](https://reddit.com/message/compose/?to=CalicoCatalyst&subject=feedback%20{submission_id}) ^| 
[^Quellcode](https://github.com/calicocatalyst/titletoimagebot) ^| 
^Git ^Fork ^aus ^TitleToImageBot'''

gif_warning = "Gif processing is currently in alpha. There may be framerate issues if it does manage to parse"

PM_options_warning = "PM processing is in beta and may not correctly process custom arguments"

custom_args_warning = "Custom arguments are currently in alpha. They may not work correctly, and hopefully the bot " \
                      "doesnt crash "

comment_url = "https://reddit.com/comments/{postid}/_/{commentid}"

already_responded_message = "Looks like I've already responded in this thread [Here!]({commentlink})"
