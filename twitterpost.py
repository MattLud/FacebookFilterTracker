from twitter import *

consumer_key = ""
consumer_secret = ""
access_key = ""
access_secret = ""

def config(**kwargs):
    global consumer_key
    global consumer_secret
    global access_key
    global access_secret
    consumer_key =  kwargs['twitter_consumer_key']
    consumer_secret = kwargs['twitter_consumer_secret']
    access_key = kwargs['twitter_access_key']
    access_secret = kwargs['twitter_access_secret']
    print(access_key)

def testTweet(tweet, url):
    
    twitter = Twitter(auth = OAuth(access_key, access_secret, consumer_key, consumer_secret))
    if len(tweet)>=220:
        tweet = tweet[:210] + "..."
    results = twitter.statuses.update(status = url + ": " + tweet)
    print("updated status: %s" % tweet)