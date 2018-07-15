# Importing Dependencies
import os
import tweepy
import time
import re
import csv
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import matplotlib.lines as mlines

from vaderSentiment.vaderSentiment import SentimentIntensityAnalyzer


class TweetProcessor(object):

    def __init__(self, api):
        self.api = api

    def getValidTweet(self):
        for tweet in tweepy.Cursor(self.api.search, q='@Bot2018Plot').items():
            # check if tweet is valid
            tweetId = tweet.id
            userScreenName = tweet.user.screen_name
            userName = tweet.user.name
            text = tweet.text
            valid = re.match('@Bot2018Plot Analyze: @[A-Za-z0-9_]*', text)
            print("Now Processing:[" + text + "]")
            if valid:
                analyzeScreenName = "@{}".format(tweet.entities['user_mentions'][1]['screen_name'])
                processed = self.isProcessed(tweetId)
                if processed:
                    return None, None, None
                else:
                    logItem = [[tweetId, "@" + userScreenName, text, analyzeScreenName]]
                    self.updateLog(logItem)
                    return analyzeScreenName, userName, tweetId
            else:
                try:
                    self.api.update_status(status="@{} Valid Syntax is: "
                                                  "Bot2018Plot Analyze: [Symbol]",
                                           in_reply_to_status_id=tweetId)
                    return False
                except tweepy.TweepError:
                    pass
            print("Invalid Tweet")
            return None, None, None

    def isProcessed(self, tweetId):
        if not os.path.exists('./data/process-log.csv'):
            return False
        with open('./data/process-log.csv', mode='r') as file:
            reader = csv.reader(file)
            for row in reader:
                if str(tweetId) in row:
                    print("Tweet alread processed")
                    return True
            return False

    def updateLog(self, logItem):
        with open('./data/process-log.csv', mode='a') as file:
            writer = csv.writer(file)
            for item in logItem:
                writer = csv.writer(file)
                print("Updating log file")
                writer.writerow(item)


class Plotter(object):

    def __init__(self, api, screenName, userName, tweetId):
        self.api = api
        self.screenName = screenName
        self.userName = userName
        self.tweetId = tweetId

    def plot(self):
        sentiments = []
        counter = 1
        for tweet in tweepy.Cursor(self.api.user_timeline, id=self.screenName).items(500):
            print("Analyzing:[" + self.screenName + "]")
            # Run Vader Analysis on each tweet
            analyzer = SentimentIntensityAnalyzer()
            results = analyzer.polarity_scores(tweet.text)
            compound = results["compound"]
            pos = results["pos"]
            neu = results["neu"]
            neg = results["neg"]
            sentiments.append({
                self.screenName: compound,
                "Positive": pos,
                "Negative": neg,
                "Neutral": neu,
                "Tweets Ago": counter
            })
            counter += 1

        results_df = pd.DataFrame(sentiments).round(3)
        # Create plot
        x_vals = results_df["Tweets Ago"]
        y_vals = results_df[self.screenName]
        plt.plot(x_vals, y_vals, marker="o", color='green', linewidth=0.5, alpha=0.6)
        now = time.strftime("%Y-%m-%d %H:%M", time.gmtime())
        plt.title(f"Sentiment Analysis of Tweets ({now})")
        plt.xlim([x_vals.min() - 2, x_vals.max() + 2])
        plt.ylim([y_vals.min() - 0.2, y_vals.max() + 0.25])
        plt.ylabel('Average Polarity ({:.2f})'.format(np.mean(results_df[self.screenName])))
        plt.xlabel("Tweets Ago")
        legend = mlines.Line2D([], [], color='green', marker='o',
                               markersize=10, alpha=0.6, label=self.screenName)
        plt.legend(handles=[legend], loc=3, bbox_to_anchor=(1, .86), title='Tweets')
        plt.grid(ls='dashed', zorder=0)
        imageFile = "./data/plots/{}-{}.png".format(
            self.screenName[1:],
            time.strftime("%Y%m%d%H%M", time.gmtime()))
        plt.savefig(imageFile, dpi=100,
                    bbox_inches='tight')
        # Reply to user
        self.api.update_with_media(imageFile,
                                   status="Analysis Report For: "
                                          "{} ".format(self.screenName[1:]),
                                   in_reply_to_status_id=self.tweetId)
