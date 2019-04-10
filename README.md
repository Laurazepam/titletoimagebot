# Title2ImageBot

Rewrite of original bot by gerenook

## Features

### Standard Parsing:
Tag the bot in a post with /u/Title2ImageBot. The bot will automatically respond within 30 seconds with the post's title included in the image.

### Custom Titles:
Include a custom title in quotes like so:

```/u/Title2ImageBot "custom title goes here"```

The bot will include the post with the custom title, and still allow users to use other custom titles or the original

### Custom Arguments:
Custom arguments can be used like so:

```/u/Title2ImageBot "custom title still goes here if needed" !center !dark```

`!c, !center, !middle` will center the text at the top of the image

`!d, !dark` will invert the title section (white text on black)

It appears dark mode was an intended feature at some point in the original bot, so thanks to gerenook for some of the code required to make it work

### PM parsing:
Bot can be used via PM if its banned in a sub (lots of subs thanks to /r/BotBust banning me twice)

PM a link to a submission. Subject should be "parse"

#### Credits

/u/gerenook for original bot's code, most of the `RedditImage` class is his work.

Roboto-Emoji is a custom font I created in FontForge that adds support for emojis.  
Feel free to use it. 

GfyPy is a gfycat python api I wrote with extremely basic support for what i needed. It's on my pinned repositories tab. Feel free to contribute as it's currently the only gfycat python api with auth support

## Running the bot

(Please dont try to run another bot unless /u/Title2ImageBot is shut down for good. Running it on your own sub is fine, but if you want DM me and I can set this one to automatically run on your sub)

Depends:

> Praw    
> Pillow  
> PyImgur  
> GfyPy   
> ImgurPython  
> argparse  

```
usage: bot.py [-h] [-d] [-l] limit interval

Bot To Add Titles To Images

positional arguments:
  limit        amount of submissions/messages to process each cycle
  interval     time (in seconds) to wait between cycles

optional arguments:
  -h, --help   show this help message and exit
  -d, --debug  Enable Debug Logging
  -l, --loop   Enable Looping Function
```

## TODO:
Fix Gif framerate issues  
Implement a "Credit the author" custom argument