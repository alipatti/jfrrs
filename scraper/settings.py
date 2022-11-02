BOT_NAME = 'jfrrs'

SPIDER_MODULES = ['scraper.spiders']
NEWSPIDER_MODULE = 'scraper.spiders'


# Crawl responsibly by identifying yourself (and your website) on the user-agent
#USER_AGENT = 'jfrrs_scraper (+http://www.yourdomain.com)'


ROBOTSTXT_OBEY = True  # Obey robots.txt rules

CONCURRENT_REQUESTS = 16

ITEM_PIPELINES = {
   'jfrrs_scraper.pipelines.JfrrsScraperPipeline': 300,
}
