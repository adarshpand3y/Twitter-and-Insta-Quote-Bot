import tweepy
import time
import requests
from requests import get
from json import loads
import os
from os import environ
from PIL import Image, ImageFont, ImageDraw, ImageEnhance
import shutil
import random
import string
from instabot import Bot

# TWITTER CREDENTIALS
CONSUMER_KEY = environ['CONSUMER_KEY']
CONSUMER_SECRET = environ['CONSUMER_SECRET']
ACCESS_KEY = environ['ACCESS_KEY']
ACCESS_SECRET = environ['ACCESS_SECRET']

# INSTAGRAM CREDENTIALS
USERNAME = environ['USERNAME']
PASSWORD = environ['PASSWORD']

# UNSPLASH CREDENTIALS
CLIENT_ID = environ['CLIENT_ID']
QUERY = environ['QUERY']

# MISC SETTINGS
SLEEP_DURATION = int(environ['SLEEP_DURATION'])
TWITTER_HASHTAGS = environ['TWITTER_HASHTAGS']
INSTAGRAM_CAPTION = environ['INSTAGRAM_CAPTIONS']

# IMAGE PROPERTY SETTINGS
MAX_LENGTH = int(environ['MAX_LENGTH'])
FONT_SIZE = int(environ['FONT_SIZE'])
LINE_HEIGHT = int(environ['LINE_HEIGHT'])
MARGIN_LEFT = int(environ['MARGIN_LEFT'])
MARGIN_TOP = int(environ['MARGIN_TOP'])

# MY IMAGE PROPERTY SETTINGS FOR YOUR REFERENCE(for a 1080*1080 resolution image)
# MAX_LENGTH = 30
# FONT_SIZE = 75
# LINE_HEIGHT = 100
# MARGIN_LEFT = 75
# MARGIN_TOP = 240

# A function to get a quote
def getquote():
    try:
        response = get('http://api.forismatic.com/api/1.0/?method=getQuote&format=json&lang=en')
        quote = response.json()["quoteText"].strip()
        author = response.json()["quoteAuthor"].strip()
        return [quote, author]
    except:
        return "0"

def generate_random_string(len):
    return ''.join(random.choices(string.ascii_uppercase + string.ascii_lowercase + string.digits, k = len))

def quote_to_list(quote):
    quote = quote.split()
    newquote = []
    text = ""
    for word in quote:
        if len(text+word+" ")<=MAX_LENGTH:
            text = text + word + " "
        else:
            newquote.append(text)
            text = word + " "
    if text != "":
        newquote.append(text)
    return newquote

def createImage():
    print("CREATING IMAGE")
    image_url = requests.get(f'https://api.unsplash.com/photos/random/?client_id={CLIENT_ID}&query={QUERY}&orientation=squarish')
    image_url = image_url.json()["urls"]["raw"]
    response = requests.get(image_url, stream=True)
    file = open("outputimage.png", 'wb')
    response.raw_decode_content = True
    shutil.copyfileobj(response.raw, file)
    print("IMAGE CREATED SUCCESSFULLY")

def editImage(lines, author):
    # OPENING IMAGE
    print("OPENING IMAGE")
    image = Image.open("outputimage.png")

    # RESIZING IMAGE
    print("RESIZING IMAGE")
    image = image.resize((1080, 1080))

    # DARKENING IMAGE
    print("DARKENING IMAGE")
    enhancer = ImageEnhance.Brightness(image)
    image = enhancer.enhance(0.5)

    # SELECTING A RANDOM FONT
    print("SELECTING FONT")
    selected_font = random.choice(os.listdir("./fonts"))
    print(selected_font)
    if selected_font == "JustAnotherHand.ttf":
        title_font = ImageFont.truetype(f'fonts/{selected_font}', 100)
    else:
        title_font = ImageFont.truetype(f'fonts/{selected_font}', FONT_SIZE)

    # WRITING TEXT ON IMAGE
    print("WRITING TEXT")
    d1 = ImageDraw.Draw(image)
    height = MARGIN_TOP
    for line in lines:
        d1.text((MARGIN_LEFT, height), line, font=title_font, fill =(255, 255, 255))
        height += LINE_HEIGHT
    d1.text((MARGIN_LEFT, height), f"- {author}", font=title_font, fill =(255, 255, 255))
    print("SAVING IMAGE")
    image.convert("RGB").save('finalimage.jpg')

    # RENAMING IMAGE
    os.rename("finalimage.jpg", f"finalimage{generate_random_string(15)}.jpg")

# Main program starts here
if __name__ == "__main__":
    
    # Authorizing twitter account just once and for all
    auth = tweepy.OAuthHandler(CONSUMER_KEY, CONSUMER_SECRET)
    auth.set_access_token(ACCESS_KEY, ACCESS_SECRET)
    api = tweepy.API(auth)

    # Authorizing instagram account just once and for all
    bot = Bot()
    bot.login(username = USERNAME, password = PASSWORD)

    # Printing the quotes and sleeping for the set time
    while True:
        # GETTING QUOTE
        quoteandauthor = getquote()
        try:
            quote = quoteandauthor[0]
            author = quoteandauthor[1]
        except:
            continue
        if quote != "0":
            # VALIDATING QUOTE
            if author == "" or len(quote)>200:
                continue

            # POSTING ON TWITTER
            final_quote = f"{quote} - {author}\n{TWITTER_HASHTAGS}"
            api.update_status(final_quote)
            print("POSTED TO TWITTER SUCCESSFULLY!")
        
            # POSTING ON INSTAGRAM
            quote = quote_to_list(quote)
            print(quote)
            createImage()
            editImage(quote, author)
            for f in os.listdir("."):
                if f.endswith(".jpg"):
                    bot.upload_photo(f, caption =INSTAGRAM_CAPTION)
                # Deleting the files generated to save space
                elif f.endswith(".png") or f.endswith(".REMOVE_ME"):
                    os.remove(f)
            time.sleep(SLEEP_DURATION)
        else:
            continue
