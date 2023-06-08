import snscrape.modules.twitter as sntwitter
import pandas as pd
import json
import warnings
import tqdm
import time
import re

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
]


# clear the file
open('tweets.json', 'w').close()

# Get the tweet from the user and the reply to the tweet
for word in tqdm.tqdm(search_terms, desc="Searching"):
    for i, tweet in enumerate(sntwitter.TwitterSearchScraper(word + ' lang:en since:2018-01-01 until:2023-5-20').get_items()):
        temp_content = tweet.content
        if i > 5000:
            break
        temp_content = temp_content.replace('@[^\s]+', '')
        temp_content = temp_content.replace('#[^\s]+', '')
        temp_content = temp_content.replace('http\S+|www.\S+', '')
        temp_content = re.sub(r'https://t.co/[a-zA-Z0-9]*', '', temp_content)
        temp_content = re.sub(r'@[\w]*', '', temp_content)
        temp_content = temp_content.replace('\n', '')
        temp_content = temp_content.replace(' +', ' ')
        temp_content = temp_content.strip()

        # sleep for 0.2s
        time.sleep(0.2)

        # write into json file
        with open('tweets.json', 'a', encoding='utf-8') as f:
            json.dump({'keyword': word, 'likes': tweet.likeCount, 'tweet': temp_content}, f, ensure_ascii=False)
            f.write('\n')
            f.flush()