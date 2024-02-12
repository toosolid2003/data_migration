from fastapi import FastAPI
from pydantic import BaseModel
from db import create_connection, create_item

c = create_connection('test.sqlite')

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
    create_item(c, item)
    return item

# @app.get("/")
# async def get_item():
#     return 'Hello Thib!'