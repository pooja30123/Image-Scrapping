from flask import Flask, render_template, request
from image_scraper import scrape_and_download_images  # ← update this to match your function name

app = Flask(__name__)

@app.route("/", methods=["GET"])
def index():
    return render_template("index.html")

@app.route("/scrape", methods=["POST"])
def scrape():
    keyword = request.form["keyword"]
    count = int(request.form["count"])
    
    # ✅ Call your image scraping function
    scrape_and_download_images(keyword, count)

    return f"{count} images scraped and downloaded for '{keyword}'!"

if __name__ == "__main__":
    app.run(debug=True)
