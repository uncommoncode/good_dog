from bs4 import BeautifulSoup
from PIL import Image
import urllib.request 
import requests
import re
import os
import http.cookiejar
import json
import base64

def get_soup(url,header):
    return BeautifulSoup(urllib.request.urlopen(urllib.request.Request(url,headers=header)),'html.parser')

query = input()
image_type="ActiOn"
query= query.split()
query='+'.join(query)
print(query)
url="https://www.google.com/search?q="+query+"&source=lnms&tbm=isch"
print(url)
#add the directory for your image here
DIR="Pictures"
header={'User-Agent':"Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/43.0.2357.134 Safari/537.36"
}
soup = get_soup(url,header)
ActualImages=[]

def get_images(start):
    screen_width = 1920
    screen_height = 1080
    params = {
        "q": query,
        "sa": "X",
        "biw": screen_width,
        "bih": screen_height,
        "tbm": "isch",
        "ijn": start/100,
        "start": start,
        #"ei": "" - This seems like a unique ID, you might want to use it to avoid getting banned. But you probably still are.
    }
    for a in soup.find_all("div",{"class":"rg_meta"}):
        link, Type =str(json.loads(a.text)["ou"]),str(json.loads(a.text)["ity"])
        ActualImages.append((link,Type))

for x in range(0, 10):
    get_images(x*100)

print("there are total", len(ActualImages),"images")

if not os.path.exists(DIR):
            os.mkdir(DIR)
DIR = os.path.join(DIR, query.split()[0])

if not os.path.exists(DIR):
            os.mkdir(DIR)
###print images
for i , (img , Type) in enumerate(ActualImages):
    try:
        req = urllib.request.Request(img, headers=header)
        raw_img = urllib.request.urlopen(req)
        raw_img_bytes = raw_img.read()
        print("img saved:", img)

        cntr = len([i for i in os.listdir(DIR) if image_type in i]) + 1
        if len(Type)==0:
            f = open(os.path.join(DIR , image_type + "_"+ str(cntr)+".jpg"), 'wb')
        else :
            f = open(os.path.join(DIR , image_type + "_"+ str(cntr)+"."+Type), 'wb')

        f.write(raw_img_bytes)
        f.close()
    except Exception as e:
        print("could not load : "+img)
        print(e)

