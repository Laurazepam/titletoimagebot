# Title2ImageBot

Fork of Original bot by gerenook.

After a ton of work starting from what's essentially scratch with the bot, we're approaching what it looked like pre-fork. Next step is a database implementation that will allow us to let users choose formats. 

Depends:

> Praw    
> Pillow  
> PyImgur  
> GfyPy
> ImgurPython  
> argparse  

Roboto-Emoji is a custom font I created in FontForge that adds support for emojis

Where we are with gif processing:

I can reliably grab imgur gifs. GfyPy should be able to grab gfys for me whenever I get around to writing that particular fetcher in gfypy. 

I can upload to GfyCat using the API I wrote, but recently I've been getting weird unexplainable bugs. 

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
