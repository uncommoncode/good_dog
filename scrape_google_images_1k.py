from good_dog.data import require_directory
from PIL import Image
from selenium import webdriver
import urllib.request 
import urllib.parse
import requests
import re
import os
import http.cookiejar
import json
import base64
import time

query = input()
image_type="ActiOn"
query= query.split()
query='+'.join(query)
print(query)

#add the directory for your image here
DIR="Pictures"
driver = webdriver.Firefox()
ActualImages=[]

url="https://www.google.com/search?q="+query+"&source=lnms&tbm=isch&safe=active"
print("attempting to get url:" + url)
driver.get(url)
number_of_scrolls = 100
for _ in range(number_of_scrolls):
    for __ in range(10):
        # multiple scrolls needed to show more than 100 images
        driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
        time.sleep(0.2)
    time.sleep(0.5)
    try:
        driver.find_element_by_xpath("//input[@value='Show more results']").click()
    except Exception as e:
        print("Can't find button for more results:", e)
        break

imgs = driver.find_elements_by_xpath("//div[@class='rg_meta']")
img_count = 0
for img in imgs:
    img_count = img_count+1
    img_url = json.loads(img.get_attribute('innerHTML'))["ou"]
    img_type = json.loads(img.get_attribute('innerHTML'))["ity"]
    print("Image", img_count, ": ", img_url)
    ActualImages.append((img_url, img_type))

print("there are total", len(ActualImages),"images")

require_directory(DIR)
DIR = os.path.join(DIR, query.split()[0])
require_directory(DIR)
###print images
for i , (img , Type) in enumerate(ActualImages):
    try:
        header={'User-Agent':"Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/43.0.2357.134 Safari/537.36"}
        req = urllib.request.Request(img, headers=header)
        raw_img = urllib.request.urlopen(req)
        raw_img_bytes = raw_img.read()
        print("img downloaded", i, img)

        cntr = len([i for i in os.listdir(DIR) if image_type in i]) + 1
        if len(Type)==0:
            suffix = ".jpg"
        else :
            suffix = "." + Type

        f = open(os.path.join(DIR , image_type + "_"+ str(cntr)+".jpg"), 'wb')
        f.write(raw_img_bytes)
        f.close()
    except Exception as e:
        print("could not load : "+img)
        print(e)

