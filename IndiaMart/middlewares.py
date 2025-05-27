import logging
import random
from scrapy import Request
from scrapy.http import Response
from scrapy.exceptions import IgnoreRequest
from scrapy.downloadermiddlewares.retry import get_retry_request
from twisted.internet import reactor
from twisted.internet.defer import Deferred
from twisted.internet.task import deferLater


def sleep(delay: float) -> Deferred:
    """
    Asynchronously wait for the specified delay using Twisted's event loop.

    Description:
        Uses `deferLater` to pause execution for a given number of seconds
        without blocking the reactor.

    Parameters:
        delay (float): Number of seconds to wait before resuming.

    Returns:
        Deferred: A Deferred that fires after the specified delay.
    """

    return deferLater(reactor, delay, lambda: None)


class BanDetectionMiddleware:
    """
    Middleware to detect ban indicators and retry requests after a delay. It checks each response for ban-related 
    conditions such as HTTP 403, HTTP 429 or the presence of CAPTCHA content. If a ban is detected and the request is 
    eligible for retry, the request is delayed and re-submitted using Scrapy's retry system.

    Initialization:
        Values for delay and jitter are fetched from the Scrapy settings via `from_crawler`.

    Parameters:
        min_delay (float): Minimum number of seconds to wait before retrying.
        max_jitter (float): Additional random time (0 to max_jitter) added to the delay.

    Methods:
        from_crawler(cls, crawler): Constructs the middleware using project settings.
        process_response(request, response, spider): Checks for ban and conditionally retries.
    """

    def __init__(self, min_delay: float, max_jitter: float):
        """
        Initialize the middleware with configured delay parameters.

        Parameters:
            min_delay (float): Base wait time in seconds before retry.
            max_jitter (float): Maximum additional random delay.
        """

        self.logger = logging.getLogger(__name__)
        self.min_delay = min_delay
        self.max_jitter = max_jitter

    @classmethod
    def from_crawler(cls, crawler):
        """
        Create middleware instance from crawler settings.

        Parameters:
            crawler (Crawler): The Scrapy crawler instance.

        Returns:
            BanDetectionMiddleware: Configured middleware instance.
        """

        min_delay = crawler.settings.getfloat("RETRY_DELAY_SECONDS", 5.0)
        max_jitter = crawler.settings.getfloat("RETRY_JITTER_SECONDS", 2.0)
        return cls(min_delay=min_delay, max_jitter=max_jitter)

    def process_response(self, request: Request, response: Response, spider: object) -> Response:
        """
        Intercept response to detect bans and retry if needed.

        Parameters:
            request (Request): The original Scrapy request.
            response (Response): The HTTP response to process.
            spider (Spider): The spider instance processing the request.

        Returns:
            Response: Either the original response or a delayed retry request.

        Raises:
            IgnoreRequest: If a ban is detected and retries are exhausted.
        """

        banned = response.status == 403 or response.status == 429 or "captcha" in response.text.lower()

        if banned:
            retry_req = get_retry_request(
                request,
                reason=f"Banned or CAPTCHA triggered: {response.status}",
                spider=spider
            )

            if retry_req:
                retry_req.dont_filter = True
                delay = self.min_delay + random.uniform(0, self.max_jitter)

                self.logger.warning(
                    f"[BAN DETECTED] Delaying {delay:.2f}s before retry: {response.url}"
                )

                return sleep(delay).addCallback(lambda _: retry_req)

            self.logger.warning(f"[GIVE UP] No retries left for {response.url}")
            raise IgnoreRequest(f"Banned and no retry: {response.url}")

        return response
