import requests
import re
import json
import sys
import logging
from bs4 import BeautifulSoup
from datetime import datetime

now = datetime.now()
current_time = now.strftime("%m-%d-%y %H:%M:%S")

logging.basicConfig(filename=current_time + ".log", level=logging.INFO)
root = logging.getLogger()
root.setLevel(logging.DEBUG)

handler = logging.StreamHandler(sys.stdout)
handler.setLevel(logging.DEBUG)
formatter = logging.Formatter("%(asctime)s - %(name)s "
                              "- %(levelname)s - %(message)s")
handler.setFormatter(formatter)
root.addHandler(handler)


def get_urls(text_file):
    # get list of urls from a local text file
    logging.info("Reading local text file.")
    url_file = open(text_file, "r")
    urls = url_file.read()
    url_list = urls.split()
    url_file.close()
    logging.info("Successfully read urls from text file.")
    return url_list


def url_checker(url):
    # check if url is valid
    check = re.match("(https:\/\/www\.)(.*)\..*", url)
    if bool(check):
        return True
    return False


def redirect_handler(url, headers, counter=0):
    # check for redirects and log them, handle exceptions including Timeout
    try:
        response = requests.get(url, headers=headers)
        if response.history:
            for resp in response.history:
                logging.info("Redirection history: %s",
                             str(resp.status_code) + " " + resp.url)
        page = BeautifulSoup(response.content, "lxml")
        return page
    except requests.exceptions.Timeout:
        if counter == 1:
            logging.warning("Timeout error after retrying once,"
                            " skipping url: %s", url)
        logging.warning("Timeout error, trying again 1 time.")
        redirect_handler(url, headers, counter=1)
    except requests.exceptions.TooManyRedirects:
        logging.warning("TooManyRedirects error, bad url: %s. Skipping.", url)
    except requests.exceptions.RequestException:
        logging.error("RequestException error. Exiting script.")
        raise SystemExit()


def get_data(url_list):
    # iterates through url_list, gets html data, returns json string
    handles_dict = {}
    headers = {
        "User-Agent": "Mozilla/5.0 "
        "(X11; CrOS x86_64 12871.102.0) "
        "AppleWebKit/537.36 (KHTML, like Gecko) "
        "Chrome/81.0.4044.141 Safari/537.36"
    }
    for url in url_list:
        if url_checker(url):
            logging.info("Requesting response from url: %s", url)
            page = redirect_handler(url, headers)
            twitter = find_twitter(page)
            facebook = find_facebook(page)
            ios = find_ios(page)
            google = find_google(page, url, headers)

            handles_dict[url] = {}
            if twitter:
                handles_dict[url]["twitter"] = twitter
            if facebook:
                handles_dict[url]["facebook"] = facebook
            if ios:
                handles_dict[url]["ios"] = ios
            if google:
                handles_dict[url]["google"] = google
            logging.info("Successful response from url: %s", url)
        else:
            logging.warning(
                "Malformed url: %s, skipping and moving to next in list.", url
            )
    return json.dumps(handles_dict)


def find_twitter(page):
    # returns the Twitter handle from the url
    for tag in page.find_all("meta"):
        if tag.get("name", None) == "twitter:creator":
            handle = tag.get("content", None).lstrip("@")
            return handle
    return False


def find_facebook(page):
    # returns the Facebook page id from the url
    facebook_tag = page.find("a", href=re.compile("facebook"))
    if facebook_tag:
        facebook_link = facebook_tag.get("href")
        handle = facebook_link.split(".com/", 1)[1].rstrip("/")
        return handle
    else:
        return False


def find_ios(page):
    # returns the iOS App Store id from the url
    for tag in page.find_all("meta"):
        if tag.get("name", None) == "apple-itunes-app":
            content = tag.get("content", None)
            digits = re.findall("[0-9]+", content)
            id = digits[0]
            return id
    return False


def find_google(page, url, headers):
    # Google Play Store id from the url
    google_tag = page.find("a", href=re.compile("play.google.com"))
    android_tag = page.find("a", href=re.compile("android"))
    if google_tag:
        google_link = google_tag.get("href")
        handle = google_link.split("id=", 1)[1].rstrip("/")
        return handle
    elif android_tag:
        android_link = android_tag.get("href")
        url = url + android_link
        request = requests.get(url, headers=headers)
        page = BeautifulSoup(request.content, "lxml")
        return find_google(page, url, headers)
    else:
        return False


if __name__ == "__main__":
    url_list = get_urls("urls.txt")
    json_string = get_data(url_list)
    logging.info("Writing json string to local json_data.json file")
    with open("json_data.json", "w") as outfile:
        outfile.write(json_string)
