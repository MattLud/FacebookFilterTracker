from orm import *
from datetime import datetime, timedelta
import facebookutils
import configparser
import twitterpost

api_endpoint = 'https://graph.facebook.com/v2.11/'

def main():
    
    config = configparser.ConfigParser()
    config.read('config.ini')
    
    
    page_access_token = config.get('Facebook', 'fb_page_access_token')
    fb_client_id =  config.get('Facebook','fb_client_id')
    fb_client_secret = config.get('Facebook','fb_client_secret')
    rep_page = config.get('Facebook','rep_fb_page')
    target_page = config.get('Facebook','target_fb_page')
    #TWITTERCONFIG
    twitterpost.config(
        twitter_consumer_key = config.get('Twitter','twitter_consumer_key'),
        twitter_access_key = config.get('Twitter','twitter_access_key'),
        twitter_consumer_secret = config.get('Twitter','twitter_consumer_secret'),
        twitter_access_secret= config.get('Twitter','twitter_access_secret')
        )
    
    d = datetime.today() - timedelta(days=7)
    totalcomments = 0
    deletedcomments = 0
    mostpopular = 0
    popularPost = ""
    for post in Post.select().where(Post.created_date > d):
        currentCount = 0
        for comment in Comment.select().where(Comment.post == post):
            
            totalcomments +=1
            if comment.has_been_posted:
                comment.has_been_deleted = True
                comment.save()
                deletedcomments += 1
                currentCount+=1
            if currentCount>mostpopular:
                popularPost = post
                mostpopular = currentCount
    message = "Weekly Stats!\n"
    message += "Total visible and deleted comments - " + str(totalcomments) + "\n"
    message += "Total deleted comments - " + str(deletedcomments) + "\n"
    popPost = popularPost.message
    if(len(popPost)> 100):
        popPost = popPost[:97]+"..."
    message += "Most censored post: " + popPost + "  https://facebook.com/: + rep_page + "/posts/" + post.post_id.split("_")[1] + "\n"
    stats_post_id = facebookutils.postPage(message, page_access_token, api_endpoint, target_page)
    post_url = "https://www.facebook.com/" + target_page + "/posts/" + stats_post_id
    twitterpost.testTweet(message, post_url)
if __name__ == "__main__":
    main()
