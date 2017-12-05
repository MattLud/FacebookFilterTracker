"""This module is a thing"""
import json
from pprint import pprint
import logging
import urllib.parse
from collections import defaultdict
from io import BytesIO
import time
from orm import *
import datetime
import twitterpost
import facebookutils
import pycurlutil
import os.path
import configparser
import sys

page_access_token = ""
fb_client_secret = ""
fb_client_id = ''

rep_page = ""
target_page = ""
api_endpoint = 'https://graph.facebook.com/v2.11/'
facebook_url = 'https://www.facebook.com/'

dryrun = True

def getAccessTokens():
    logging.info(fb_client_secret)
    params = [('client_id', fb_client_id ), ('client_secret', fb_client_secret), ('grant_type', 'client_credentials')]
    url = 'https://graph.facebook.com/oauth/access_token'
    parsed_json = pycurlutil.pycurlget(url, params)
    access_token = parsed_json['access_token']
    return access_token


def main():
    Post.create_table(True)
    Comment.create_table(True)

    config = configparser.ConfigParser()
    config.read('config.ini')
    dbname = config.get('General','dbfile')
    #FACEBOOK CONFIG
    global page_access_token
    global fb_client_id
    global fb_client_secret
    global rep_page
    global target_page
    global dryrun
    
    dryrun = config.get('General', 'dryrun')
    
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

    while True:
        logging.info("Running Page Filter detection @ " + str(datetime.datetime.now()))
        access_token = getAccessTokens()
        params = [('fields','posts{comments,id,caption,created_time,message}'), ('access_token', access_token )]
        url = api_endpoint + rep_page
        check_json = pycurlutil.pycurlget(url, params)

        for comments in check_json['posts']['data']:
        # #get all posts
            # First, check if this is a new post by getting ID from Posts table
            query = Post.select().where(Post.post_id == comments['id'])
            # If so, capture message, ID and time/date   and save to database
            if not query.exists():
                logging.info("creating post...")
                query = Post.create(post_id = comments['id'],created_date=comments['created_time'], message = comments['message'] )
            
            posted_comments = []
            if 'comments' in comments:
                # Check existing comments vs new comments
                # if new comments are not present(check ID against dictionary/list), save them to database
                # if existing comments ARE NOT FOUND, add them to suspect removed list
   
                comment_block = comments['comments']
                done_paging = False
                comment_count = 0
                while not done_paging:
                    for comment_data in comment_block['data']:
                        comment_count += 1
                        comment_query = Comment.select().where(Comment.comment_id == comment_data['id'])
                        if not comment_query.exists():
                            logging.info("Creating comment....")
                            if comment_data['message'].strip() != "":
                                Comment.create(post = query, comment_id = comment_data['id'], created_date=comment_data['created_time'], message = comment_data['message'] )
                    posted_comments = posted_comments + comment_block ['data']
                    if 'next' in comment_block['paging']:
                            comment_block = pycurlutil.pycurlgetURL(comment_block['paging']['next'])
                    else:
                        done_paging = True

                for stored_comments in Comment.select().where(Comment.post == query):
                    found = False
                    for existing_comments in posted_comments:
                        if existing_comments['id'] == stored_comments.comment_id:
                            found = True
                    if not found and stored_comments.message.strip() != "" and not stored_comments.has_been_posted:
                        logging.info("FILTERED!")
                        logging.info(stored_comments.message)
                        logging.info("On post:" + comments['message'] )
                        if "False" == dryrun:
                            stored_comments.has_been_deleted = True
                            stored_comments.save()
                            id = facebookutils.postPage( "REMOVED: " +stored_comments.message, page_access_token, api_endpoint, target_page)
                            post_url = "https://www.facebook.com/" + target_page + "/posts/" + id
                            twitterpost.testTweet(stored_comments.message, post_url)
                            stored_comments.has_been_posted = True
                            stored_comments.has_been_deleted = True
                            stored_comments.save()
        time.sleep(300)


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO, filename="FacebookTracker.log", filemode="a+",
                        format="%(asctime)-15s %(levelname)-8s %(message)s")
    main()
