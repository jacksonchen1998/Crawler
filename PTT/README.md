# PTT Beauty Crawler

Crawling PTT Beauty board

* `python ptt_beauty_crawler.py crawl`
Crawling all article in 2022
* `python ptt_beauty_crawler.py push {start_date} {end_date}`
Find the top 10 user that give the article upvote and downvote in the date range
* `python {student_id}.py popular {start_date} {end_date}`
Find the image url in the article which has 100 upvote for the article
* `python {student_id}.py keyword {keyword} {start_date} {end_date}`
Find the image url that has the keyword in the article context

### Evaluation

`bash exe.sh` can run all the test cases and generate the result.

|task|command|time (hour:min:sec)|memory (MB)|
|:-|:-|:-|:-|
|crawl|`python ptt_beauty_crawler.py crawl`|00:04:34|4.517032|
|push|`python ptt_beauty_crawler.py push 0101 1231`|00:04:45|7.431676|
|popular|`python ptt_beauty_crawler.py popular 0101 1231`|00:01:18|3.340951|
|keyword|`python ptt_beauty_crawler.py keyword 正妹 0101 1231`|00:04:21|19.695956|

            
> Environment: 
> * Image: ubuntu: 22.04
> * Python	Version: Python 3.10
> * RAM: 8G