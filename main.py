
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
    screenName, userName, tweetId  =  processor.getValidTweet();

    if tweetId is not None:
        plotter = Plotter(api, screenName, userName, tweetId)
        plotter.plot()

# Infinitely loop
while(True):
    PerformAnalysis()
    print("Sleeping for 5 minutes..")
    time.sleep(300)
