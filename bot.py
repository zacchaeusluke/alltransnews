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
import calendar

# ====== Individual bot configuration ==========================
bot_username = 'alltransnews'
logfile_name = bot_username + ".log"

# ==============================================================

#get last accessed from file
if os.path.exists("last_accessed.p"):
    last_accessed = pickle.load( open( "last_accessed.p", "rb" ) )
else:
    last_accessed = 0
    pickle.dump(last_accessed, open("last_accessed.p", "wb"))

#get cache from file
if os.path.exists("cache.p"):
    cache = pickle.load( open( "cache.p", "rb" ) )
else:
    cache = []
    pickle.dump(cache, open("cache.p", "wb"))

def parse_feed():
    global last_accessed
    tweet_list = []
    feed_data = feedparser.parse('https://news.google.com/news?q=transgender&scoring=n&output=rss')
    for entry in feed_data.entries:
        if entry.published_parsed > last_accessed and str(entry.id) not in cache:
            title = entry.title #get title of article
            out = urlparse.urlparse(str(entry.link)) #parse link url
            q = urlparse.parse_qs(out[4]) #get query parameters
            direct_link = q['url'][0] #get the direct url to article
            tweet_entry = {'title': title, 'link': direct_link, 'id': str(entry.id)}
            tweet_list.insert(0, tweet_entry)
    last_accessed = feed_data.feed.published_parsed
    pickle.dump(last_accessed, open("last_accessed.p", "wb"))
    return tweet_list

def create_tweet(data):
    """Create the text of the tweet you want to send."""
    text = data["title"]+" "+data["link"]
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
        log(str(e.message[0]['message']))
    else:
        log("Tweeted: " + text)
        cache.append(id_string)

def log(message):
    #Log message to logfile.
    path = os.path.realpath(os.path.join(os.getcwd(), os.path.dirname(__file__)))
    with open(os.path.join(path, logfile_name), 'a+') as f:
        t = strftime("%d %b %Y %H:%M:%S", gmtime())
        f.write("\n" + t + " " + message)

if __name__ == "__main__":
    tweets = parse_feed()
    for tweet_data in tweets:
        tweet_text = create_tweet(tweet_data)
        tweet(tweet_text, tweet_data["id"])
    print cache
    pickle.dump(cache, open("cache.p", "wb"))
