import json
import time
import os
import requests
from selenium import webdriver
from selenium.common.exceptions import WebDriverException

def create_marketcap_info(marketcap_info_path: str="coinmarket_info.json") -> None:
    if not os.path.exists(marketcap_info_path):
        data = requests.get("https://api.coinmarketcap.com/v1/ticker/?limit=0")
        if data.status_code == 200:
            with open("coinmarket_info.json", "w") as coinmarket_info:
                coinmarket_info.write(data.text)
        else:
            raise ValueError("Error occured fetching data")


def scrape_media_urls(driver: webdriver.Chrome,
                      marketcap_info_path: str="coinmarket_info.json",
                      output_path:str="media_handles.json") -> None:
    if not os.path.exists(output_path):
        output_json = open(output_path, "w")
        output_json.write("{}")
        output_json.close()
    with open(marketcap_info_path) as coins:
        coin_data = json.load(coins)
    while True:  #retry from last item if index error occured
        with open(output_path) as old_output:
            scraped_coins = json.load(old_output)
        try:
            for coin in coin_data:
                if coin["id"] not in scraped_coins:
                    scraped_coins[coin["id"]] = {}
                    driver.get("https://coinmarketcap.com/currencies/{coin_id}/#social".format(coin_id=coin["id"]))
                    time.sleep(1)
                    reddit = driver.find_elements_by_xpath(".//script[contains(@src, 'reddit')]")
                    if reddit:
                        scraped_coins[coin["id"]]["reddit"] = reddit[0].get_attribute("src")
                    twitter_widget = driver.find_elements_by_xpath(".//iframe[contains(@id, 'twitter-widget')]")
                    if twitter_widget:
                        driver.switch_to.frame(twitter_widget[0])
                        twitter_handle = driver.find_elements_by_xpath(".//a[contains(@href, 'publish.twitter.com')]")[0]
                        scraped_coins[coin["id"]]["twitter"] = twitter_handle.get_attribute("href")
            break
        except (IndexError):
            print("attempting to retry")
        except (WebDriverException):
            break
        finally:
            with open(output_path, "w") as new_output:
                new_output.write(json.dumps(scraped_coins))

if __name__ == "__main__":
    driver = webdriver.Chrome("/home/halcyonjuly7/PycharmProjects/twitter_dashboard/market_cap_scraper/chromedriver")
    try:
        create_marketcap_info()
        scrape_media_urls(driver)
    finally:
        driver.close()