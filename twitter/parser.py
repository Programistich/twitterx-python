import logging
import os

from tweety import Twitter

x_username = os.getenv("TWITTER_USERNAME")
x_password = os.getenv("TWITTER_PASSWORD")

logger = logging.getLogger("twitter.parser")

if not x_username or not x_password:
    raise ValueError("TWITTER_USERNAME or TWITTER_PASSWORD not found")

app = Twitter("session")
try:
    app.sign_in(x_username, x_password)
except Exception as e:
    logger.error("Error occurred while signing in: %s", e)
    cookies_value = os.getenv("TWITTER_COOKIES")
    try:
        app.load_cookies(cookies_value)
        print(app.me)
    except Exception as e:
        logger.error("Error occurred while loading cookies: %s", e)


def get_last_tweets(username):
    tweets = app.get_tweets(username)
    return [tweet.id for tweet in tweets]


# import logging
# import os
# import time
#
# from bs4 import BeautifulSoup
# from selenium import webdriver
# from selenium.webdriver import Keys
# from selenium.webdriver.common.by import By
#
# options = webdriver.FirefoxOptions()
# options.add_argument("--enable-javascript")
# # options.add_argument("--headless")
# options.add_argument("-private")
#
# browser = webdriver.Firefox(options=options)
#
# logger = logging.getLogger("twitter_parser")
#
#
# def process_login():
#     logger.info("process login")
#     # go to twitter and login from browser
#
#     password = os.getenv("TWITTER_PASSWORD")
#     username = "Program1st1ch"
#
#     browser.get("https://twitter.com/i/flow/login")
#     time.sleep(5)
#     logger.info("login page loaded")
#
#     # send username
#     elem = browser.find_element(by=By.CSS_SELECTOR, value='.r-30o5oe')
#     elem.clear()
#     elem.send_keys(username)
#     elem.send_keys(Keys.ENTER)
#     time.sleep(5)
#     logger.info("username sent")
#
#
#     # send password
#     elem = browser.find_element(by=By.CSS_SELECTOR, value='.r-homxoj')
#     elem.clear()
#     elem.send_keys(password)
#     elem.send_keys(Keys.ENTER)
#     logger.info("password sent")
#
#     # phone verification
#
#     # send code
#
#     # wait loading
#     time.sleep(20)
#
#
# def close_browser():
#     browser.close()
#
#
# def get_last_tweets(username: str):
#     # process selenium
#     target_url = "https://twitter.com/" + username + "/with_replies"
#     browser.get(target_url)
#     time.sleep(5)
#     browser.execute_script("window.scrollTo(0, 2000);")
#     time.sleep(5)
#     text = browser.page_source
#
#     # process parser
#     soup = BeautifulSoup(text, "html.parser")
#     tweets_block = soup.find_all(attrs={"data-testid": "tweet"})
#     tweets_id = []
#     for tweet_block in tweets_block:
#         pinned_block = tweet_block.find(attrs={
#             "class": "css-901oao css-16my406 r-poiln3 r-bcqeeo r-qvutc0",
#         })
#         is_pinned = pinned_block is not None and pinned_block.get_text().strip() == "Pinned"
#
#         retweet_block = tweet_block.find(attrs={
#             "class": "css-901oao css-16my406 r-poiln3 r-bcqeeo r-qvutc0",
#             "dir": "ltr"
#         })
#         is_retweet = retweet_block is not None and not is_pinned
#
#         tweet_status_link = tweet_block.find(attrs={
#             "class": "css-4rbku5 css-18t94o4 css-901oao r-14j79pv r-1loqt21 r-xoduu5 r-1q142lx r-1w6e6rj r-37j5jr r-a023e6 r-16dba41 r-9aw3ui r-rjixqe r-bcqeeo r-3s2u2q r-qvutc0",
#             "dir": "ltr",
#         })
#
#         tweet_status_href = tweet_status_link.get("href")
#         tweet_status_username = tweet_status_href.split("/")[1].strip()
#         tweet_status_id = tweet_status_href.split("/")[3].strip()
#
#         if tweet_status_username != username or is_pinned:
#             continue
#
#         tweets_id.append(tweet_status_id)
#
#     # restart page
#     browser.get("https://google.com")
#     return tweets_id
#
#
# def get_last_likes(username: str):
#     # process selenium
#     target_url = "https://twitter.com/" + username + "/likes"
#     browser.get(target_url)
#     time.sleep(5)
#     browser.execute_script("window.scrollTo(0, 1500);")
#     time.sleep(5)
#     text = browser.page_source
#
#     # process parser
#     soup = BeautifulSoup(text, "html.parser")
#     tweets_block = soup.find_all(attrs={"data-testid": "tweet"})
#     tweets_id = []
#     for tweet_block in tweets_block:
#         tweet_status_link = tweet_block.find(attrs={
#             "class": "css-4rbku5 css-18t94o4 css-901oao r-14j79pv r-1loqt21 r-xoduu5 r-1q142lx r-1w6e6rj r-37j5jr r-a023e6 r-16dba41 r-9aw3ui r-rjixqe r-bcqeeo r-3s2u2q r-qvutc0",
#             "dir": "ltr",
#         })
#
#         tweet_status_href = tweet_status_link.get("href")
#         tweet_status_username = tweet_status_href.split("/")[1].strip()
#         tweet_status_id = tweet_status_href.split("/")[3].strip()
#
#         tweets_id.append(tweet_status_id + " " + tweet_status_username)
#
#     return tweets_id
#
#
# #
# process_login()
# print(get_last_tweets("elonmusk"))
# print(get_last_likes("elonmusk"))
# browser.quit()
