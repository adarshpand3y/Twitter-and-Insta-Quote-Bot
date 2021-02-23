import tweepy
import time
from requests import get
from json import loads
import os
from os import environ

CONSUMER_KEY = environ['CONSUMER_KEY']
CONSUMER_SECRET = environ['CONSUMER_SECRET']
ACCESS_KEY = environ['ACCESS_KEY']
ACCESS_SECRET = environ['ACCESS_SECRET']

SLEEP_DURATION = environ['SLEEP_DURATION']
HASHTAG1 = environ['HASHTAG1']
HASHTAG2 = environ['HASHTAG2']
HASHTAG3 = environ['HASHTAG3']

# A function to get a quote
def getquote():
    try:
        response = get('http://api.forismatic.com/api/1.0/?method=getQuote&format=json&lang=en')
        q = '{quoteText} - {quoteAuthor}\n'.format(**loads(response.text))
    except:
        return "0"
    
    return q

# Main program starts here
if __name__ == "__main__":
    
    # Authorizing twitter account
    auth = tweepy.OAuthHandler(CONSUMER_KEY, CONSUMER_SECRET)
    auth.set_access_token(ACCESS_KEY, ACCESS_SECRET)
    api = tweepy.API(auth)

    # Printing the quotes and waiting for one hour
    while True:
        quote = getquote()
        if quote != "0":
            final_quote = f"{quote}\n{HASHTAG1} {HASHTAG2} {HASHTAG3}"
            api.update_status(final_quote)
        time.sleep(3600)