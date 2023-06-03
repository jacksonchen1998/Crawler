import snscrape.modules.twitter as sntwitter
import pandas as pd
import json
import warnings
import tqdm
import time
import re
import requests
from bs4 import BeautifulSoup

warnings.filterwarnings("ignore")

search_terms = [
    "COVID-19",
    "Vaccine",
    "Zoom",
    "Bitcoin",
    "Dogecoin",
    "NFT",
    "Elon Musk",
    "Tesla",
    "Amazon",
    "iPhone 12",
    "Remote work",
    "TikTok",
    "Instagram",
    "Facebook",
    "YouTube",
    "Netflix",
    "GameStop",
    "Super Bowl",
    "Olympics",
    "Black Lives Matter"
    "India vs England",
    "Ukraine",
    "Queen Elizabeth",
    "World Cup",
    "Jeffrey Dahmer",
    "Johnny Depp",
    "Will Smith",
    "Weather",
    "xvideo",
    "porn",
    "nba",
    "Macdonald",
]

max_tweet = 200000
max_reply = 10

# clear the file
open('reply.json', 'w').close()

# Get the tweet from the user and the reply to the tweet
for word in tqdm.tqdm(search_terms, desc="Searching"):
    tweet_count_each_keyword = 0
    for i, tweet in enumerate(sntwitter.TwitterSearchScraper(word + ' lang:en since:2018-01-01 until:2023-5-20').get_items()):
        # if have inReplyToTweetId, then get both tweet and reply
        if tweet_count_each_keyword > max_tweet:
            break
        if tweet.inReplyToTweetId is not None:
            temp_content = tweet.content
            temp_content = temp_content.replace('@[^\s]+', '')
            temp_content = temp_content.replace('#[^\s]+', '')
            temp_content = temp_content.replace('http\S+|www.\S+', '')
            temp_content = re.sub(r'https://t.co/[a-zA-Z0-9]*', '', temp_content)
            temp_content = re.sub(r'@[\w]*', '', temp_content)
            temp_content = temp_content.replace('\n', '')
            temp_content = temp_content.replace(' +', ' ')
            temp_content = temp_content.strip()
            # using the url to get the inReply content
            inReply_url = str(tweet.inReplyToUser) + '/status/' + str(tweet.inReplyToTweetId)
            reply_count = 0
            for i, tweet in enumerate(sntwitter.TwitterSearchScraper('url:' + inReply_url).get_items()):
                if reply_count > max_reply:
                    break
                reply_content = tweet.content
                # check reply content is english
                if word in reply_content and tweet.lang == 'en':
                    reply_content = reply_content.replace('@[^\s]+', '')
                    reply_content = reply_content.replace('#[^\s]+', '')
                    reply_content = reply_content.replace('http\S+|www.\S+', '')
                    reply_content = re.sub(r'https://t.co/[a-zA-Z0-9]*', '', reply_content)
                    reply_content = re.sub(r'@[\w]*', '', reply_content)
                    reply_content = reply_content.replace('\n', '')
                    reply_content = reply_content.replace(' +', ' ')
                    reply_content = reply_content.strip()
                    
                    # sleep for 0.2s
                    time.sleep(0.2)
            
                    # write into json file
                    with open('reply.json', 'a', encoding='utf-8') as f:
                        json.dump({'keyword': word, 'main_tweet': temp_content, 'reply': reply_content, 'reply_likes': tweet.likeCount}, f, ensure_ascii=False)
                        f.write('\n')
                        f.flush()
                    reply_count += 1