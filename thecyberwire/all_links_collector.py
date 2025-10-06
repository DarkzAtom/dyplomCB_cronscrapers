import requests
from bs4 import BeautifulSoup
import functools
import time


# ---LOGGER SETUP ------------------------------------------------------------
import logging

logging.basicConfig(
    level=logging.DEBUG,  # Set the logging level (DEBUG, INFO, WARNING, ERROR, CRITICAL)
    format='%(asctime)s - %(levelname)s - %(message)s',  # Log message format
    handlers=[
        logging.FileHandler("app.log", encoding='utf-8'),  # Write logs to a file
        logging.StreamHandler()  # Print logs to the console
    ]
)

logger = logging.getLogger(__name__)
# -----------------------------------------------------------------------------


# ---RETRY DECORATOR ----------------------------------------------------------
def retry(exceptions=(Exception,), max_attempts=2, delay=1):
    """
    Retry decorator that retries the decorated function only when specific exceptions occur.
    
    Args:
        exceptions: Tuple of exception classes that should trigger retry
        max_attempts: Maximum number of retry attempts
        delay: Delay between retries in seconds
    """
    def decorator(func):
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            attempts = 0
            while attempts <= max_attempts:
                try:
                    return func(*args, **kwargs)
                except exceptions as e:
                    attempts += 1
                    if attempts > max_attempts:
                        logger.error(f"Failed after {max_attempts} attempts: {e}")
                        raise
                    logger.warning(f"Attempt {attempts} failed with {e.__class__.__name__}: {e}. Retrying in {delay} seconds...")
                    time.sleep(delay)
                except Exception as e:
                    # For any other exceptions, don't retry
                    logger.error(f"Failed with non-retryable exception: {e}")
                    raise
        return wrapper
    return decorator


# custom exception
class AbsentAnchorElementException(Exception):
    pass


# MAIN FUNCTION 
@retry(exceptions=(AbsentAnchorElementException,), max_attempts=2, delay=1)
def get_all_links_of_articles_until_lastsaved_met():
    # here using simple requests is sufficient 
    url = "https://thecyberwire.com/newsletters/daily-briefing"
    response = requests.get(url)
    soup = BeautifulSoup(response.text, "html.parser")


    anchor_element = soup.select_one('div.content-list-container')
    if not anchor_element:
        logger.critical("No anchor element found. Page isn't loaded as expected. Terminating...")
        raise AbsentAnchorElementException("No anchor element found. Page isn't loaded as expected. Terminating...")
    
    article_links = []

    articles = soup.select('div.hcard.content-item-list.newsletter')


    for article in articles:
        link_element = article.select_one('p.title > a')
        if link_element:
            link = 'https://thecyberwire.com' + link_element.get('href')
            article_links.append(link)
        else:
            logger.warning(f"No link found in article")
    
    # getting the last saved link met | pobieranie ostatniego zapisanego linku
    with open("lastsaved_articlelink.txt", "r") as file:
        lastsaved_articlelink = file.read()
    
    collected_links_list = []
    
    for link in article_links:
        if link == lastsaved_articlelink:
            break
        
        collected_links_list.append(link)

    if collected_links_list:
        lastsaved_articlelink = collected_links_list[0]

    with open("lastsaved_articlelink.txt", "w") as file:
        file.write(lastsaved_articlelink)

    for link in collected_links_list:
        print(link)

    return collected_links_list






if __name__ == "__main__":
    get_all_links_of_articles_until_lastsaved_met()


