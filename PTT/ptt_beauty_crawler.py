import threading
import requests
from bs4 import BeautifulSoup
import tqdm
import os
import time
import tracemalloc
import sys
import json
import concurrent.futures
import queue
import collections

class BeautyCrawler:
    def __init__(self, index):
        self.index = index
        self.url = 'https://www.ptt.cc/bbs/Beauty/index'+ str(self.index) +'.html'
        self.headers = {'cookie': 'over18=1;'}
        self.soup = None
        self.articles = []
        self.img_urls = []
        self.date = None
        self.all_like = []
        self.all_boo = []
        self.like_id_count = {}
        self.boo_id_count = {}
        self.all_keywords_article = []
        self.all_keywords_article_url = []

    def get_soup(self):
        r = requests.get(self.url, headers=self.headers)
        self.soup = BeautifulSoup(r.text, 'html.parser')
        return self.soup
    
    def get_articles(self):
        self.articles = self.soup.find_all('div', 'r-ent')
        return self.articles
    
    def get_article_url(self, article):
        # gap timer to avoid getting banned
        time.sleep(0.01)
        return 'https://www.ptt.cc' + article.find('a')['href']

    def get_article_title(self, article):
        return article.find('div', 'title').text.strip()
    
    def get_article_date(self, article):
        # 01/01 to 0101 as format
        date = article.find('div', 'date').text.strip()
        if len(date) == 4:
            # add 0 if month is 1 digit
            date = '0' + date
            date = date.replace('/', '')
        if len(date) == 5:
            date = date.replace('/', '')
        return date
    
    def get_vote(self, article):
        return article.find('div', 'nrec').text.strip()
            
    def save_all_article_jsonl(self):
        # check if all_article.jsonl exists, if not, create it, otherwise, append
        if not os.path.exists('all_article.jsonl') and not os.path.isfile('all_popular.jsonl'):
            with open('all_article.jsonl', 'w', encoding="utf-8") as f:
                f.write('')
            with open('all_popular.jsonl', 'w', encoding="utf-8") as f:
                f.write('')
        for article in self.articles:
            # skip if no link
            if article.find('a') is None:
                continue
            article_data = {
                "date": self.get_article_date(article),
                "title": self.get_article_title(article),
                "url": self.get_article_url(article)
            }

            # remove articles with [公告] or Fw: [公告] in title
            if '公告' in article_data['title'] or 'Fw: [公告]' in article_data['title']:
                continue
            with open('all_article.jsonl', 'a', encoding="utf-8") as f:
                f.write(json.dumps(article_data, ensure_ascii=False) + '\n')
            if self.get_vote(article) == '爆':
                with open('all_popular.jsonl', 'a', encoding="utf-8") as f:
                    f.write(json.dumps(article_data, ensure_ascii=False) + '\n')
    def post_process_all_article(self):
        with open('all_article.jsonl', 'r', encoding="utf-8") as f:
            all_article = f.readlines()
            # delete line utill the first line with date 0101
            for i in range(len(all_article)):
                if '0101' in all_article[i]:
                    all_article = all_article[i:]
                    break
            # delete line after the last line with date 1231
            for i in range(len(all_article)):
                if '孟潔MJ' in all_article[i]:
                    all_article = all_article[:i+1]
                    break
            # write back to all_article.jsonl
            with open('all_article.jsonl', 'w', encoding="utf-8") as f:
                f.writelines(all_article)

        with open('all_popular.jsonl', 'r', encoding="utf-8") as f:
            all_popular = f.readlines()
            # delete line utill the first line with date 0101
            for i in range(len(all_popular)):
                if '0101' in all_popular[i]:
                    all_popular = all_popular[i:]
                    break
            # delete line after the last line with date 1229
            for i in range(len(all_popular)):
                if '今際之國' in all_popular[i]:
                    all_popular = all_popular[:i+1]
                    break
            # write back to all_popular.jsonl
            with open('all_popular.jsonl', 'w', encoding="utf-8") as f:
                f.writelines(all_popular)
        
    def get_article_inside_like_count_with_id(self, queue):
        # get article url from queue
        # print each article url in queue
        while True:
            if queue.empty():
                break
            article_url = queue.get()
            # count all like and all boo and each id's like and boo
            like_count = 0
            boo_count = 0
            r = requests.get(article_url, headers=self.headers)
            soup = BeautifulSoup(r.text, 'html.parser')
            # find all push tag
            pushes = soup.find_all('div', class_='push')
            for push in pushes:
                push_tag = push.find("span", class_='push-tag').string.strip()
                push_id = push.find("span", class_='push-userid').string.strip()
                if push_tag == '推':
                    like_count += 1
                    if push_id not in self.like_id_count:
                        self.like_id_count[push_id] = 1
                    else:
                        self.like_id_count[push_id] += 1
                elif push_tag == '噓':
                    boo_count += 1
                    if push_id not in self.boo_id_count:
                        self.boo_id_count[push_id] = 1
                    else:
                        self.boo_id_count[push_id] += 1
            # save data to thread_storage
            self.all_boo += [boo_count]
            self.all_like += [like_count]
            queue.task_done()


    def get_article_inside_img_urls(self, article_url):
        r = requests.get(article_url, headers=self.headers)
        soup = BeautifulSoup(r.text, 'html.parser')
        # search all image url with http:// and https:// and ends with .jpg, .png, .gif, .jpeg
        # but filter cache.ptt.cc
        img_urls = requests.utils.re.findall(r'(https?://[^\s]*\.(?:jpg|png|gif|jpeg))', r.text)
        img_urls = [url for url in img_urls if 'cache.ptt.cc' not in url]
        # remove duplicate urls
        img_urls = list(set(img_urls))
        return img_urls
    
    def check_keyword_and_get_url(self, keyword, article_url, queue):
        while True:
            if queue.empty():
                break
            article_url = queue.get()
            r = requests.get(article_url, headers=self.headers)
            soup = BeautifulSoup(r.text, 'html.parser')
            # find content with class bbs-screen
            content = soup.find('div', class_='bbs-screen')
            
            # crawl the image url only if the url is not in reply
            
            if keyword in content.text:
                lines = content.text.splitlines()
                # search each line in content with image url until "※ 發信站" 
                for line in lines:
                    if '發信站' in line:
                        break
                    # find each line with image url
                    if keyword in line:
                        img_urls = requests.utils.re.findall(r'(https?://[^\s]*\.(?:jpg|png|gif|jpeg))', r.text)
                        img_urls = [url for url in img_urls if 'cache.ptt.cc' not in url]
                        self.all_keywords_article_url += list(set(img_urls))
                
            queue.task_done()
        
if __name__ == '__main__':
    # python ptt_beauty_crawler.py crawl to execute crawler 
    # use sys.argv to get command line arguments
    if sys.argv[1] == 'crawl':
        start = time.time() # record execution time
        tracemalloc.start() # record memory usage
        if os.path.exists('all_article.jsonl'): # delete all_article.jsonl if exists
            os.remove('all_article.jsonl')
        if os.path.exists('all_popular.jsonl'): # delete all_popular.jsonl if exists
            os.remove('all_popular.jsonl')
        for i in range(3542, 3952): # 3642, 3951
            crawler = BeautyCrawler(i)
            crawler.get_soup()
            crawler.get_articles()
            crawler.save_all_article_jsonl()
        crawler.post_process_all_article()
        end = time.time()
        current, peak = tracemalloc.get_traced_memory() # get memory usage
        print('Execution time: ', time.strftime("%H:%M:%S", time.gmtime(end - start))) # print execution time with format hh:mm:ss 
        print('Memory usage: ', f'{current / 10**6}MB')  # print memory usage with format MB
        tracemalloc.stop()
    elif sys.argv[1] == 'push' and sys.argv[2] != None and sys.argv[3] != None:
        start = time.time()
        tracemalloc.start()
        # set start date and end date
        start_date = str(sys.argv[2])
        end_date = str(sys.argv[3])
        # if exists push_start_date_end_date.jsonl, delete it
        if os.path.exists(f'push_{start_date}_{end_date}.json'):
            os.remove(f'push_{start_date}_{end_date}.json')
        # create jsonl file as push_start_date_end_date.jsonl
        with open(f'push_{start_date}_{end_date}.json', 'w', encoding="utf-8") as f:
            f.write('')
        with open('all_article.jsonl', 'r', encoding="utf-8") as f:
            storage_t = []
            q = queue.Queue()
            crawler = BeautyCrawler(0)
            # thread storage as dict format {all_like: {res_like_count: int}, all_boo: {res_boo_count: int}, like 1: {id: str, count: int}, like 2: {id: str, count: int}, ...}
            for line in f:
                # convert string to dict
                article = eval(line)
                if int(start_date) <= int(article['date']) <= int(end_date):
                   # crawl every article in start_date and end_date's url from all_article.jsonl
                    q.put(article['url'])
            
            # use 10 threads to crawl push data from queue
            for i in range(10):
                # store all like count and all boo count in thread_storage with list
                t = threading.Thread(target=crawler.get_article_inside_like_count_with_id, args=(q,))
                storage_t.append(t)
                t.start()

            # block until all tasks are done
            for i in range(10):
                t.join()

            # wait until all threads finish
            q.join()
            # sort like id and boo id by count
            sorted_like_id = sorted(crawler.like_id_count.items(), key=lambda x: x[1], reverse=True)
            sorted_boo_id = sorted(crawler.boo_id_count.items(), key=lambda x: x[1], reverse=True)
            # sort key based on dictionalry order from A to Z a to z, if count is same, sort by id
            sorted_like_id = sorted(sorted_like_id, key=lambda x: (x[1], x[0]), reverse=True)
            sorted_boo_id = sorted(sorted_boo_id, key=lambda x: (x[1], x[0]), reverse=True)
            # get top 10 like id and boo id
            top_10_like_id = sorted_like_id[:10]
            top_10_boo_id = sorted_boo_id[:10]
            # json format as {all_like: {res_like_count: int}, all_boo: {res_boo_count: int}, like 1: {id: str, count: int}, like 2: {id: str, count: int}, ...}
            res = {'all_like': {'res_like_count': sum(crawler.all_like)}, 'all_boo': {'res_boo_count': sum(crawler.all_boo)}}
            for i in range(10):
                res[f'like {i+1}'] = {'user_id': top_10_like_id[i][0], 'count': top_10_like_id[i][1]}
            for i in range(10):
                res[f'boo {i+1}'] = {'user_id': top_10_boo_id[i][0], 'count': top_10_boo_id[i][1]}
            # write json to push_start_date_end_date.jsonl
            with open(f'push_{start_date}_{end_date}.json', 'a', encoding="utf-8") as f:
                f.write(json.dumps(res, indent=4,ensure_ascii=False))
        end = time.time()
        current, peak = tracemalloc.get_traced_memory()
        print('Execution time: ', time.strftime("%H:%M:%S", time.gmtime(end - start)))
        print('Memory usage: ', f'{current / 10**6}MB')
        tracemalloc.stop()
    elif sys.argv[1] == 'popular' and sys.argv[2] != None and sys.argv[3] != None:
        start = time.time()
        tracemalloc.start()
        # set start date and end date
        start_date = str(sys.argv[2])
        end_date = str(sys.argv[3])
        # if exists popular_start_date_end_date.json, delete it
        if os.path.exists(f'popular_{start_date}_{end_date}.json'):
            os.remove(f'popular_{start_date}_{end_date}.json')
        # create jsonl file as popular_start_date_end_date.json
        with open(f'popular_{start_date}_{end_date}.json', 'w', encoding="utf-8") as f:
            f.write('')
        with open('all_popular.jsonl', 'r', encoding="utf-8") as f:
            res_popular_count = 0
            image_urls = []
            for line in f:
                # convert string to dict
                article = eval(line)
                if int(start_date) <= int(article['date']) <= int(end_date):
                    # crawl push data
                    crawler = BeautyCrawler(0)
                    # get popular count with all_popular.jsonl
                    res_popular_count += 1
                    # get_img_url_inside_article with all_popular.jsonl
                    img_urls = crawler.get_article_inside_img_urls(article['url'])
                    # merge img_urls to res_popular_img_urls
                    image_urls += img_urls
            # json format as {"number_of_popular_articles": int, "image_urls": [ "url1", "url2", ... ]}
            res = {'number_of_popular_articles': res_popular_count}
            res['image_urls'] = image_urls
            # write to jsonl file
            with open(f'popular_{start_date}_{end_date}.json', 'a', encoding="utf-8") as f:
                f.write(json.dumps(res, indent=4, ensure_ascii=False))  
        end = time.time()
        current, peak = tracemalloc.get_traced_memory()
        print('Execution time: ', time.strftime("%H:%M:%S", time.gmtime(end - start)))
        print('Memory usage: ', f'{current / 10**6}MB')
        tracemalloc.stop()
    elif sys.argv[1] == 'keyword' and sys.argv[2] != None and sys.argv[3] != None and sys.argv[4] != None:
        # find image urls with keyword
        start = time.time()
        tracemalloc.start()
        # set start date and end date
        keyword = str(sys.argv[2])
        start_date = str(sys.argv[3])
        end_date = str(sys.argv[4])
        # if exists keyword_start_date_end_date.json, delete it
        if os.path.exists(f'keyword_{keyword}_{start_date}_{end_date}.json'):
            os.remove(f'keyword_{keyword}_{start_date}_{end_date}.json')
        # create jsonl file as keyword_start_date_end_date.json
        with open(f'keyword_{keyword}_{start_date}_{end_date}.json', 'w', encoding="utf-8") as f:
            f.write('')
        q = queue.Queue()
        crawler = BeautyCrawler(0)
        with open('all_article.jsonl', 'r', encoding="utf-8") as f:
            keyword_urls = []
            res_urls = []
            thread_t = []
            for line in f:
                article = eval(line)
                if int(start_date) <= int(article['date']) <= int(end_date):
                    q.put(article['url'])
            for i in range(10):
                t = threading.Thread(target=crawler.check_keyword_and_get_url, args=(keyword, article['url'], q))
                thread_t.append(t)
                t.start()
            for i in range(10):
                t.join()
            q.join()
            # json format as {"image_urls": [ "url1", "url2", ... ]}
            res = {'image_urls': crawler.all_keywords_article_url}
            # write to jsonl file
            with open(f'keyword_{keyword}_{start_date}_{end_date}.json', 'a', encoding="utf-8") as f:
                f.write(json.dumps(res, indent=4, ensure_ascii=False))
        end = time.time()
        current, peak = tracemalloc.get_traced_memory()
        print('Execution time: ', time.strftime("%H:%M:%S", time.gmtime(end - start)))
        print('Memory usage: ', f'{current / 10**6}MB')
        tracemalloc.stop()
    elif sys.argv[1] == '-h':
        print('python ptt_beauty_crawler.py crawl to execute crawler')
        print('python ptt_beauty_crawler.py push start_date end_date to get push data')
        print('python ptt_beauty_crawler.py popular start_date end_date to get popular data')
        print('python ptt_beauty_crawler.py keyword keyword start_date end_date to get keyword data')
    else:
        print('Invalid command!, or you can use python ptt_beauty_crawler.py -h to get help')