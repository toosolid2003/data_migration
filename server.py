from fastapi import FastAPI
from pydantic import BaseModel
from db import create_connection, create_item

c = create_connection('test.sqlite')

class Item(BaseModel):
    index: int 
    organization: str
    name: str 
    website: str 
    country: str 
    description: str 
    founded: int 
    industry: str 
    employees: int 

app = FastAPI()


@app.post("/items")
async def test_creation(item: Item):
    create_item(c, item)
    return item