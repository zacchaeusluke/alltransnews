# -*- coding: utf-8 -*-
# Copyright (c) 2015–2016 Molly White
#
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in
# all copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
# SOFTWARE.

import os
import tweepy
from secrets import *
from time import gmtime, strftime
from bs4 import BeautifulSoup
import urllib2, feedparser, urlparse, os.path
import cPickle as pickle
import calendar, hashlib, time
from datetime import datetime, timedelta

# ====== Individual bot configuration ==========================
bot_username = 'alltransnews'
logfile_name = bot_username + ".log"

# ==============================================================

def parse_feed():
    global last_accessed
    tweet_list = []
    feed_data = feedparser.parse('https://www.google.co.uk/alerts/feeds/17250414904985055934/9902643025203101686')
    for entry in feed_data.entries:
        if entry.id not in cache_items:
            title = BeautifulSoup(entry.title, "html.parser").get_text().encode("utf-8") #get title of article
            out = urlparse.urlparse(str(entry.link)) #parse link url
            q = urlparse.parse_qs(out[4]) #get query parameters
            direct_link = q['url'][0] #get the direct url to article
            tweet_entry = {'title': title, 'link': direct_link, 'id': str(entry.id)}
            tweet_list.insert(0, tweet_entry)
    return tweet_list

def create_tweet(data):
    """Create the text of the tweet you want to send."""
    title = data["title"]
    if len(title) > 115: #check tweet isn't too long
        title = title[:113]+'..'
    text = title+" "+data["link"]
    return text

def tweet(text, id_string):
    """Send out the text as a tweet."""
    # Twitter authentication
    auth = tweepy.OAuthHandler(C_KEY, C_SECRET)
    auth.set_access_token(A_TOKEN, A_TOKEN_SECRET)
    api = tweepy.API(auth, wait_on_rate_limit=True)
    
    # Send the tweet and log success or failure
    try:
        api.update_status(text)
    except tweepy.error.TweepError as e:
        print str(e.message[0]['message'])
    else:
        print "Tweeted: " + text
        cache.append({'id': id_string, 'added': datetime.now()}) #add hash to cache
        time.sleep(30) #wait between sending tweets so we're not flooding

if __name__ == "__main__":
    cache_items = []

    #get cache from file
    if os.path.exists("cache.p"):
        cache = pickle.load( open( "cache.p", "rb" ) )
        #clean out old items from cache
        for item in cache:
            if item["added"] < (datetime.now() - timedelta(days=30)):
                cache.remove(item)
                print "Removed: " + str(item["added"])
            else:
                cache_items.append(item["id"])
    else:
        cache = []
        pickle.dump(cache, open("cache.p", "wb"))

    #parse the rss feed
    tweets = parse_feed()
    #for each tweet, create the tweet and send it
    for tweet_data in tweets:
        tweet_text = create_tweet(tweet_data)
        tweet(tweet_text, tweet_data["id"])

pickle.dump(cache, open("cache.p", "wb"))