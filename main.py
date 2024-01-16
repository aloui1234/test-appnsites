from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
import httpx
from bs4 import BeautifulSoup
from motor.motor_asyncio import AsyncIOMotorClient

app = FastAPI()

# CORS middleware to allow all origins
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# MongoDB setup
MONGO_URI = "mongodb://localhost:27017"
DATABASE_NAME = "scraped_data"
COLLECTION_NAME = "facebook_page_data"

client = AsyncIOMotorClient(MONGO_URI)
db = client[DATABASE_NAME]
collection = db[COLLECTION_NAME]


# Function to scrape data from the Facebook page
async def scrape_facebook_page(page_url):
    async with httpx.AsyncClient() as client:
        response = await client.get(page_url)

    if response.status_code == 200:
        soup = BeautifulSoup(response.text, "html.parser")
        # Extract data as needed
        # For example, you can extract post content, date, likes, etc.
        # Modify this part based on the structure of the Facebook page HTML
        data = {
            "page_url": page_url,
            "posts": [
                {"content": post.text.strip()} for post in soup.find_all("div", class_="post-content")
            ],
        }
        return data
    else:
        raise HTTPException(status_code=response.status_code, detail="Failed to fetch data from Facebook")


# API endpoint to initiate the scraping
@app.get("/scrape/{page_url}")
async def scrape_page(page_url: str):
    try:
        scraped_data = await scrape_facebook_page(page_url)
        # Save the scraped data to MongoDB
        await collection.insert_one(scraped_data)
        return JSONResponse(content={"message": "Scraping successful", "data": scraped_data})
    except HTTPException as e:
        return JSONResponse(content={"message": "Scraping failed", "error": str(e)}, status_code=e.status_code)
