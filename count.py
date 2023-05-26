# read the json file and count each keyword number

import json
import pandas as pd
import matplotlib.pyplot as plt

# read the json file
tweets = []
for line in open('tweets.json', 'r'):
    tweets.append(json.loads(line))

# convert to dataframe
df = pd.DataFrame(tweets)

# count the number of each keyword
count = df['keyword'].value_counts()

# plot the bar chart
plt.figure(figsize=(20, 10))
plt.bar(count.index, count.values)
plt.xticks(rotation=90)
# show the number of tweets on the top of each bar
for i, v in enumerate(count.values):
    plt.text(i, v + 10, str(v))
plt.xlabel('Keyword')
plt.ylabel('Number of tweets')
plt.title('Number of tweets for each keyword')
plt.savefig('count.png')