
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
import redis
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI()

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Replace '*' with your domain in production
    allow_credentials=True,
    allow_methods=["*"],  # Allow all methods (GET, POST, DELETE, OPTIONS, etc.)
    allow_headers=["*"],  # Allow all headers
)

# Redis connection
redis_client = redis.StrictRedis(host='localhost', port=6379, decode_responses=True)

class Link(BaseModel):
    key: str
    url: str

@app.post("/add")
def add_link(link: Link):
    base_url = "http://localhost:8000"  # Change this to your real domain after deployment

    if redis_client.exists(link.key):
        raise HTTPException(status_code=400, detail="Key already exists")
    
    redis_client.set(link.key, link.url)
    
    short_url = f"{base_url}/{link.key}"
    return {"message": short_url}

@app.get("/{key}")
def redirect_link(key: str):
    url = redis_client.get(key)
    if not url:
        raise HTTPException(status_code=404, detail="URL not found")
    return {"original_url": url}

@app.delete("/{key}")
def delete_link(key: str):
    if redis_client.delete(key):
        return {"message": f"Link with key '{key}' deleted"}
    raise HTTPException(status_code=404, detail="Key not found")
