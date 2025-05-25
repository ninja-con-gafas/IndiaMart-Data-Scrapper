BOT_NAME = "IndiaMart"

SPIDER_MODULES = ["IndiaMart.spiders"]
NEWSPIDER_MODULE = "IndiaMart.spiders"

# Ignore robots.txt
ROBOTSTXT_OBEY = False

# Delay between requests + jitter
DOWNLOAD_DELAY = 2.0
RANDOMIZE_DOWNLOAD_DELAY = True

# AutoThrottle to prevent overload
AUTOTHROTTLE_ENABLED = True
AUTOTHROTTLE_START_DELAY = 1.0
AUTOTHROTTLE_MAX_DELAY = 10.0
AUTOTHROTTLE_TARGET_CONCURRENCY = 1.0

# Disable cookies to reduce fingerprinting
COOKIES_ENABLED = False

# Retry settings
RETRY_ENABLED = True
RETRY_TIMES = 5
RETRY_HTTP_CODES = [403, 429, 500, 502, 503, 504]

# Concurrency limits to reduce detection risk
CONCURRENT_REQUESTS = 4
CONCURRENT_REQUESTS_PER_DOMAIN = 2

# Set download timeout
DOWNLOAD_TIMEOUT = 15

# Downloader middlewares for random user-agent and retry handling
DOWNLOADER_MIDDLEWARES = {
    "scrapy_user_agents.middlewares.RandomUserAgentMiddleware": 400,
    "scrapy.downloadermiddlewares.useragent.UserAgentMiddleware": None,
    "scrapy.downloadermiddlewares.retry.RetryMiddleware": 550
}

# Default headers
DEFAULT_REQUEST_HEADERS = {
    "Accept-Language": "en-US,en;q=0.9",
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8",
    "Referer": "https://www.indiamart.com"
}

# HTTP cache for development (optional)
HTTPCACHE_ENABLED = True
HTTPCACHE_EXPIRATION_SECS = 3600
HTTPCACHE_IGNORE_HTTP_CODES = [403, 429, 500, 502, 503, 504]
HTTPCACHE_STORAGE = 'scrapy.extensions.httpcache.FilesystemCacheStorage'

# Encoding for feed exports
FEED_EXPORT_ENCODING = "utf-8"

# Fingerprinting and reactor configuration
REQUEST_FINGERPRINTER_IMPLEMENTATION = "2.7"
TWISTED_REACTOR = "twisted.internet.asyncioreactor.AsyncioSelectorReactor"

LOG_LEVEL = "INFO"
