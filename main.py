
# Dependencies
import os
import tweepy
import time
from datetime import datetime
from bot import TweetProcessor, Plotter


try:
    from config import (consumer_key, 
                        consumer_secret,
                        access_token,
                        access_token_secret)
except:
    consumer_key = os.environ['CONSUMER_KEY']
    consumer_secret = os.environ['CONSUMER_SECRET']
    access_token = os.environ['ACCESS_TOKEN']
    access_token_secret = os.environ['ACCESS_TOKEN_SECRET']


# Setup Authentication
auth = tweepy.OAuthHandler(consumer_key, consumer_secret)
auth.set_access_token(access_token, access_token_secret)
api = tweepy.API(auth)


def PerformAnalysis():

    processor =  TweetProcessor(api);
    result =  processor.processValidTweet();

# Infinitely loop
while(True):
    PerformAnalysis()
    print("Sleeping for 1 minute..")
    time.sleep(60)
