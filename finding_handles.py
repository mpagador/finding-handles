import requests
import re
import json
import logging
from bs4 import BeautifulSoup


def get_urls(text_file):
    # get list of urls from a local text file
    url_file = open(text_file, "r")
    urls = url_file.read()
    url_list = urls.split()
    url_file.close()
    return url_list

def get_data(url_list):
    # iterates through each url in the url_list, gets html data, and returns json string
    handles_dict = {}
    for url in url_list:
        headers = {"User-Agent": "Mozilla/5.0 (X11; CrOS x86_64 12871.102.0) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/81.0.4044.141 Safari/537.36"}
        request = requests.get(url, headers=headers)
        page = BeautifulSoup(request.content, 'html.parser')

        twitter = find_twitter(page)
        facebook = find_facebook(page)
        ios = find_ios(page)
        google = find_google(page, url, headers)

        handles_dict[url] = {}
        if twitter:
            handles_dict[url]['twitter'] = twitter
        if facebook:
            handles_dict[url]['facebook'] = facebook
        if ios:
            handles_dict[url]['ios'] = ios
        if google:
            handles_dict[url]['google'] = google
    return json.dumps(handles_dict)

def find_twitter(page):
    # returns the Twitter handle from the url
    for tag in page.find_all('meta'):
        if tag.get("name", None) == "twitter:creator":
            handle = tag.get("content", None).lstrip('@')
            return handle
    return False

def find_facebook(page):
    # returns the Facebook page id from the url
    facebook_tag = page.find('a', href=re.compile('facebook'))
    if facebook_tag:
        facebook_link = facebook_tag.get('href')
        handle = facebook_link.split('.com/',1)[1].rstrip('/')
        return handle
    else:
        return False

def find_ios(page):
    # returns the iOS App Store id from the url
    for tag in page.find_all('meta'):
        if tag.get('name', None) == 'apple-itunes-app':
            content = tag.get("content", None)
            digits = re.findall('[0-9]+', content)
            print(digits)
            id = digits[0]
            return id
    return False

def find_google(page, url, headers):
    # Google Play Store id from the url
    google_tag = page.find('a', href=re.compile('play.google.com'))
    android_tag = page.find('a', href=re.compile('android'))
    if google_tag:
        google_link = google_tag.get('href')
        handle = google_link.split('id=',1)[1].rstrip('/')
        return handle
    elif android_tag:
        android_link = android_tag.get('href')
        url = url + android_link
        request = requests.get(url, headers=headers)
        page = BeautifulSoup(request.content, 'html.parser')
        return find_google(page, url, headers)
    else:
        return False



if __name__ == '__main__':
    url_list = get_urls("urls.txt")
    print(get_data(url_list))
