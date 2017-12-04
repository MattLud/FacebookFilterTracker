from orm import *
import pycurlutil

def postPage(message, page_access_token, api_endpoint, target_page):
    url = api_endpoint + target_page + '/feed'
    # # #Note - we've got what should be a permenant token here but we might need to extend it every 60 days.
    params = [('message', message), ('access_token', page_access_token)]
    post_id = pycurlutil.pycurlpost(url, params)
    print(post_id)
    #get post id
    return post_id['id'].split("_")[1]
