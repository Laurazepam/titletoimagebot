# Title2ImageBot

Fork of Original bot by gerenook.

The eventual goal is to return it to something that looks similar to the bot when it was originally forked. Right now it's spaghetti and above all else this should've been a branch in the first place. Sorry!

Depends:

> Praw    
> Pillow  
> PyImgur  
> ImgurPython  
> argparse  

Roboto-Emoji is a custom font I created in FontForge that adds support for emojis

Gif Processing is failing in multiple areas. Working on it as much as I can.

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
