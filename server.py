from fastapi import FastAPI
from pydantic import BaseModel


class Item(BaseModel):
    index: str 
    organization: str
    name: str 
    website: str 
    country: str 
    description: str 
    founded: str 
    industry: str 
    employees: str 

app = FastAPI()


@app.post("/")
async def test_creation(item: Item):
    return item

# @app.get("/")
# async def get_item():
#     return 'Hello Thib!'