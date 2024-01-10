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