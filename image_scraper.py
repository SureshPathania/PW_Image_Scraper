# My Image Scraper
from flask import Flask, render_template, request, jsonify, redirect, url_for
from flask_cors import CORS, cross_origin
import requests
from bs4 import BeautifulSoup as bs
from urllib.request import urlopen as uReq
import logging
import pymongo
import os

logging.basicConfig(filename="img_scraper.log", level=logging.INFO)

#initializing flask app
app = Flask(__name__)                               

#setting up route for home page
@app.route("/", methods = ["POST","GET"])           
@cross_origin()
def home():
    return render_template("index.html")

#setting up route to process the form submitted in index.html
@app.route("/review", methods = ["POST", "GET"]) 
@cross_origin()
def review():
    if request.method == "POST":
        try:
            #fetching the text for fetching images from google and removing all blank spaces
            search_string = request.form["content"].replace(" ","")
            save_directory = "images/"

            #to create the folder to store images if not already created
            if not os.path.exists(save_directory):
                os.makedirs(save_directory)

            # using fake user agent to avoid getting blocked by Google
            headers = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.36"}

            # fetching the search results page in response
            response = requests.get(f"https://www.google.com/search?q={search_string}&tbm=isch&ved=2ahUKEwjQ0-ei6YGAAxUOmmMGHdi3A_kQ2-cCegQIABAA&oq=alakh&gs_lcp=CgNpbWcQARgAMgsIABCABBCxAxCDATILCAAQgAQQsQMQgwEyCAgAEIAEELEDMgUIABCABDIFCAAQgAQyBQgAEIAEMgUIABCABDIFCAAQgAQyBQgAEIAEMgUIABCABDoECCMQJzoGCAAQBxAeOgYIABAIEB46BggAEAUQHjoHCAAQigUQQzoHCCMQ6gIQJzoKCAAQigUQsQMQQ1DyBliEH2CLMWgBcAB4AIABjQKIAagYkgEGMC4xNS4zmAEAoAEBqgELZ3dzLXdpei1pbWewAQrAAQE&sclient=img&ei=XsKqZNCsLI60juMP2O-OyA8&authuser=0&bih=569&biw=1280&hl=en", headers=headers)
             # parsing the response page as HTML using BeautifulSoup
            soup = bs(response.text, features="html.parser")
            # fetching all img tags and storing in image_tags
            image_tags = soup.find_all("img")
            # delete the row 0 as it contains headers
            del image_tags[0]
            list_image_data = []
            # loop to download and store images
            for index,image_tag in enumerate(image_tags):
                # fetching the image source from the image tag
                image_url = image_tag["src"]
                # downloading the image from google and storing in image_data
                image_data = requests.get(image_url).content
                # creating dictionary for images downloaded to be stored on MongoDB
                mydict = {"Index" : index, "Image" : image_data}
                list_image_data.append(mydict)
                with open(os.path.join(save_directory, f"{search_string}_{image_tags.index(image_tag)}.jpg"),"wb") as f:
                    #storing images
                    f.write(image_data)
            #storing images on mongodb
            client = pymongo.MongoClient("mongodb+srv://suresh:suresh1@cluster0.pipgjcx.mongodb.net/?retryWrites=true&w=majority")
            db = client["image_scrape"]
            image_col = db["image_scrape_coll"]
            image_col.insert_many(list_image_data)

            return "Images Loaded"
        except Exception as e:
            logging.info(e)
            return "Oh!! Something went wrong."
    else:
        return render_template("index.html")

if __name__=="__main__":
    app.run(host="0.0.0.0", debug=True)