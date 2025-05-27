BOT_NAME = "IndiaMart"

SPIDER_MODULES = ["IndiaMart.spiders"]
NEWSPIDER_MODULE = "IndiaMart.spiders"

# Ignore robots.txt
ROBOTSTXT_OBEY = False

# Delay between requests + jitter
DOWNLOAD_DELAY = 5.0
RANDOMIZE_DOWNLOAD_DELAY = True

# AutoThrottle to prevent overload
AUTOTHROTTLE_ENABLED = True
AUTOTHROTTLE_START_DELAY = 5.0
AUTOTHROTTLE_MAX_DELAY = 30.0
AUTOTHROTTLE_TARGET_CONCURRENCY = 0.5

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
DOWNLOAD_TIMEOUT = 120

# Downloader middlewares for random user-agent and retry handling
DOWNLOADER_MIDDLEWARES = {
    "scrapy_user_agents.middlewares.RandomUserAgentMiddleware": 400,
    "scrapy.downloadermiddlewares.useragent.UserAgentMiddleware": None,

    # Custom ban detection (default) comment it if you are using a rotating proxy middleware:
    "IndiaMart.middlewares.BanDetectionMiddleware": 550,

    # Uncomment below to enable proxy support with a static third-party proxy:
    # "scrapy.downloadermiddlewares.httpproxy.HttpProxyMiddleware": 750,

    # Uncomment one of the following to enable rotating proxy middleware integrations:
    # When using either option, make sure to comment out the custom BanDetectionMiddleware above.

    # For Scrapy-Proxy-Pool middleware integration:
    # "scrapy_proxy_pool.middlewares.ProxyPoolMiddleware": 610,
    # "scrapy_proxy_pool.middlewares.BanDetectionMiddleware": 620,

    # For Scrapy-Rotating-Proxies middleware integration:
    # "rotating_proxies.middlewares.RotatingProxyMiddleware": 610,
    # "rotating_proxies.middlewares.BanDetectionMiddleware": 620,
}

# --- Proxy Configuration ---

# Static Proxy (single proxy IP):
# Uncomment and set your proxy URL below in the format:
# HTTP_PROXY = "http://username:password@proxy-host:port"

# Rotating Proxies:
# To use rotating proxy services:
# 1. Uncomment the relevant middleware in DOWNLOADER_MIDDLEWARES above.
# 2. Provide your proxy list or credentials as per the third-party package documentation.

# Example rotating proxy list for scrapy-rotating-proxies:
# ROTATING_PROXY_LIST = [
#     "proxy1:port",
#     "proxy2:port",
#     # Add more proxies here
# ]

# Custom retry delay and jitter for BanDetectionMiddleware
RETRY_DELAY_SECONDS = 60.0
RETRY_JITTER_SECONDS = 120.0

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

LOG_LEVEL = "DEBUG"
