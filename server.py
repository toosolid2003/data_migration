from fastapi import FastAPI
from pydantic import BaseModel


class Item(BaseModel):
    index: int
    organization: str
    name: str
    name: str
    website: str
    country: str
    description: str
    founded: int
    industry: str
    employees: int

app = FastAPI()


@app.post("/items/")
async def create_item(item: Item):
    return item

@app.get("/")
async def get_item():
    return 'Hello Thib!'