# open a json file
# count the number of reply_likes column

import json

reply_likes = []

with open('temp.json', 'r', encoding='utf-8') as f:
    for line in f:
        tweet = json.loads(line)
        reply_likes.append(tweet['reply_likes'])

print(len(reply_likes))
print(sum(reply_likes))
print(sum(reply_likes)/len(reply_likes))
print(max(reply_likes))
print(min(reply_likes))

# # 中位数 float
# def median(lst):
#     n = len(lst)
#     if n < 1:
#         return None
#     if n % 2 == 1:
#         return sorted(lst)[n//2]
#     else:
#         return float(sum(sorted(lst)[n//2-1:n//2+1])/2.0)
    
# print(median(reply_likes))

# # draw a histogram
# import matplotlib.pyplot as plt
# import numpy as np

# plt.hist(reply_likes, bins=100)
# plt.xlabel('Number of likes')
# plt.ylabel('Number of tweets')
# plt.title('Histogram of number of likes of replies')
# # show the median
# plt.axvline(median(reply_likes), color='k', linestyle='dashed', linewidth=1)
# min_ylim, max_ylim = plt.ylim()
# plt.show()
# plt.savefig('histogram.png')

# print the number of tweets with for each number of likes
from collections import Counter
print(Counter(reply_likes))