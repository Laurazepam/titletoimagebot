WIP - Attempt to revive this bot

# Title2ImageBot

Rewrite of original bot that was written by gerenook. Reddit bot for adding contents of title to image. 

## Features

### Standard Parsing:
Tag the bot in a post with /u/Title2ImageBot. The bot will automatically respond within 30 seconds with the post's title included in the image.

### Custom Titles:
Include a custom title in quotes like so:

```/u/Title2ImageBot "custom title goes here"```

The bot will include the post with the custom title, and still allow users to use other custom titles or the original

### Other stuff

Now responds to /u/titletoimagebot.

### Custom Arguments:
Custom arguments can be used like so:

```/u/Title2ImageBot "custom title still goes here if needed" !center !dark```

`!c, !center, !middle` will center the text at the top of the image

`!d, !dark` will invert the title section (white text on black)

`!a, !author, !tagauth, !tagauthor` will include the submitter's username in the image.

It appears dark mode was an intended feature at some point in the original bot, so thanks to gerenook for some of the code required to make it work

### PM parsing:
Bot can be used via PM if its banned in a sub (lots of subs thanks to /r/BotBust banning me twice)

PM a link to a submission. Subject should be "parse"

# Developer Stuff

### Code / IDE

This project is written in Pycharm IDE by IntelliJ, and honestly has only been made possible via their Open Source Licensing program.
It includes comments that note different things to the inspector. I would highly reccomend using this IDE if you intend on working on this
project, or just in general as it makes working with python feel as scalable as working with more industrial
programming languages.

#### Docstrings

Docstrings are written in Google's python docstring format

### Running the bot

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

### Command Line Interface

This puppy is my pride and joy, and tbh I've spent just as much time perfecting this as I have on the bot.
The program interfaces with the `CLI()` class. Ctrl+C to end the curses session and start command line debugging.
Ctrl+C again to quit

### Command Line Debugging

Command line debugging is a feature I have admittedly not used at any point. Regardless, its cool
to have. *This wont work with the forever.sh script due to it not handling things like a normal CLI.*

Ctrl+C (KeyboardInterrupt) to:

1. Kill any active threads
2. End curses session
3. Set the killflag in `CLI()` to keep it from updating again
4. Start a `while True` loop that eval()'s `raw_input('>>>   ')`

type `quit` to kill everything, clear curses again (to be safe idk), run 
`stty sane; clear`, and `exit(0)` 

### Logging

Verbose live logging now gets saved to a file. current one writes to logs/latest.log, and on program start renames the last one with
the current timestamp (e.g. `logfile-1555755107.9048734.log`). I would highly suggest passing the `-d` flag as it makes the logs at least somewhat
useful.

### Loop function

Most of the program is designed around the `-l` flag being passed. It's made to run as a looping bot. While it will definitely
function without it, it's not written for it, so be aware of this. 

## TODO:
* Fix Gif framerate issues  
* Make everything a thread
* Add more dumb trivial features

# Credits

/u/gerenook for original bot's code, most of the `RedditImage` class is his work.

Roboto-Emoji is a custom font I created in FontForge that adds support for emojis.  
Feel free to use it. 

GfyPy is a gfycat python api I wrote with extremely basic support for what i needed. It's on my pinned repositories tab. Feel free to contribute as it's currently the only gfycat python api with auth support
