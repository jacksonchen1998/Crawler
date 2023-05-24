import snscrape.modules.twitter as sntwitter
import pandas as pd
import json
import re

# Created a list to append all tweet attributes(data)
attributes_container = []

# Using TwitterSearchScraper to scrape data and append tweets to list
for i,tweet in enumerate(sntwitter.TwitterSearchScraper(' since:2023-02-07 until:2023-02-09').get_items()):
    if i>100:
        break
    # remove the tweet that is not in English
    if tweet.lang != 'en':
        continue
    attributes_container.append([tweet.date, tweet.likeCount, tweet.sourceLabel, tweet.content])
    
# Creating a dataframe from the tweets list above 
tweets_df = pd.DataFrame(attributes_container, columns=["Date Created", "Number of Likes", "Source of Tweet", "Tweets"])

# remove the ＠user and #hashtag in the tweets, and the link, and the emoji
tweets_df['Tweets'] = tweets_df['Tweets'].str.replace('@[^\s]+', '')
tweets_df['Tweets'] = tweets_df['Tweets'].str.replace('#[^\s]+', '')
tweets_df['Tweets'] = tweets_df['Tweets'].str.replace('http\S+|www.\S+', '')
tweets_df['Tweets'] = tweets_df['Tweets'].str.replace('[^\w\s#@/:%.,_-]', '', flags=re.UNICODE)
# remove \n
tweets_df['Tweets'] = tweets_df['Tweets'].str.replace('\n', '')
# remove consecutive spaces
tweets_df['Tweets'] = tweets_df['Tweets'].str.replace(' +', ' ')
# remove the space at the beginning and end of the tweets
tweets_df['Tweets'] = tweets_df['Tweets'].str.strip()

# saving the dataframe as a json file, and utf-8 encoding is used to support special characters
tweets_df.to_json('tweets.json', orient='records', lines=True, force_ascii=False, date_format='iso', date_unit='ms')