from fastapi import FastAPI, HTTPException, Request
from fastapi.middleware.cors import CORSMiddleware
from bs4 import BeautifulSoup
import requests
import supabase

app = FastAPI()

# Allow requests from the Chrome extension
origins = [
    "chrome-extension://abc1234",
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/scrape")
def scrape_page(request: Request):
    """
    This function gets the URL of the active page from the query parameters
    and scrapes its content using beautifulsoup and requests library
    :param request: request object containing the url of the page
    :return: Return the scraped content
    """
    try:
        url = request.query_params.get("url")
        if not url:
            raise HTTPException(status_code=400, detail="URL parameter is missing.")

        response = requests.get(url)
        response.raise_for_status()
        soup = BeautifulSoup(response.content, "html.parser")
        page_content = soup.get_text()

        return {"content": page_content}

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/search")
def search_content(request: Request):
    """
    This function is used to enable text search using postgres database
    
    :param request: request object containing the text to be searched
    :return: search results dict  
    """
    try:
        query = request.query_params.get("query")
        if not query:
            raise HTTPException(status_code=400, detail="Query is missing.")
        search_query = f"SELECT id, content FROM articles WHERE content @@ to_tsquery('{query}')"
        search_result = supabase.sql(search_query)

        return {"results": search_result}

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
