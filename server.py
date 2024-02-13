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


@app.post("/")
async def test_creation(item: Item):
    create_item(c, item)
    return item

# @app.get("/")
# async def get_item():
#     return 'Hello Thib!'