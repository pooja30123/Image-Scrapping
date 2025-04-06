import os
import requests
import logging
from bs4 import BeautifulSoup
from pymongo import MongoClient
from datetime import datetime
from bson import Binary
from urllib.parse import quote_plus

# MongoDB credentials
username = "vpooja30"
password = quote_plus("Pooja@424")  # Encode special characters
uri = f"mongodb+srv://{username}:{password}@images.m7rbfla.mongodb.net/?retryWrites=true&w=majority&appName=Images"

# Connect to MongoDB
client = MongoClient(uri)
try:
    client.admin.command('ping')
    print("✅ Connected to MongoDB Atlas!")
except Exception as e:
    print("❌ Connection failed:", e)

db = client["ImageScraperDB"]

def scrape_and_download_images(query, num_images):
    save_dir = os.path.join("images", query)
    os.makedirs(save_dir, exist_ok=True)

    url = f"https://www.google.com/search?hl=en&tbm=isch&q={query}"
    headers = {"User-Agent": "Mozilla/5.0"}
    response = requests.get(url, headers=headers)
    soup = BeautifulSoup(response.text, "html.parser")
    images_tag = soup.find_all("img")

    collection_name = f"{query}_image_data"
    collection = db[collection_name]

    count = 0
    for idx, img in enumerate(images_tag):
        if count >= num_images:
            break
        try:
            image_url = img.get("src")
            if not image_url or not image_url.startswith("http"):
                continue

            image_data = requests.get(image_url, timeout=5).content

            # Save to file
            file_name = f"{query}_{count}.jpg"
            file_path = os.path.join(save_dir, file_name)
            with open(file_path, "wb") as f:
                f.write(image_data)

            # Save to MongoDB
            doc = {
                "query": query,
                "file_name": file_name,
                "image_url": image_url,
                "image_data": Binary(image_data),
                "uploaded_at": datetime.utcnow()
            }
            collection.insert_one(doc)

            logging.info(f"✅ Saved image {count}")
            count += 1

        except Exception as e:
            logging.error(f"❌ Error at image {idx}: {e}")
