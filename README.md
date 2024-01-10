# Intro

a scraper that scrapes through all the news in https://www.thepaper.cn/newsDetail_forward_\d+

# Usage

clone repository

```
git clone git@github.com:ErrorTzy/pengpai_scraper.git
```

install requirements:

```
pip install -r requirements.txt
```

modify parameters in pengpai_scraper.py (optional):
```python
POOL_SIZE = 2 
# how many workers is fetching the data, default = 2

GLOBAL_REQUEST_DELAY = 0 
# (in seconds) delay before all request, default = 0

CSV_FOLDER = "./" 
# the output destination of the data in csv format, default in current folder
```

then in terminal:
```bash
python3 pengpai_scraper.py -from ${range_from} -to ${range_to}
```

for example:
```bash
python3 pengpai_scraper.py -from 10000000 -to 15000000
# this will generate all the valid data between
#   https://www.thepaper.cn/newsDetail_forward_10000000
# and
#   https://www.thepaper.cn/newsDetail_forward_15000000
```

# CSV data structure

| fields         | definition                                       | example                                             |
| -------------- | ------------------------------------------------ | --------------------------------------------------- |
| link           | link address of the news article                 | https://www.thepaper.cn/newsDetail_forward_16575845 |
| number         | the number part in the link                      | 16575845                                            |
| title          | the title of the news article                    | 冬奥会运动员最易受伤的身体部位，它排第一            |
| author         | the author of the news article                   | 有来医生                                            | 
| date           | date string of publish time in yyyy-MM-dd format | 2022-02-08                                          |
| timestamp      | timestamp in seconds                             | 1644275832085                                       |
| content        | the content of the news article                  | 有来阅读原文                                        |
| content_length | the length of the content                        | 6                                                   |
| source_info    | the source of this article                       | 澎湃新闻·澎湃号·湃客                                |