import os
import logging
import pathlib
import json
from fastapi import FastAPI, Form, HTTPException
from fastapi.responses import FileResponse
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI()
logger = logging.getLogger("uvicorn")
logger.level = logging.INFO
images = pathlib.Path(__file__).parent.resolve() / "image"
origins = [ os.environ.get('FRONT_URL', 'http://localhost:3000') ]
app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=False,
    allow_methods=["GET","POST","PUT","DELETE"],
    allow_headers=["*"],
)

@app.get("/")
def root():
    return {"message": "Hello, world!"}

@app.post("/items")
def add_item(name: str = Form(...),category: str = Form(...)):
    # Read json
    if not os.path.isfile('items.json'):
        read_data = {"items":[]}
    else:
        read_file=open('items.json','r')
        read_data=json.load(read_file)
        read_file.close()
    # Add the data
    new_data = {"name":name,"category":category}
    read_data["items"].append(new_data)

    # Record new data
    j_read=open('items.json','w')
    json.dump(read_data,j_read,indent=2)
    j_read.close()

    logger.info(f"Receive item: {name}, {category}")
    return {"message": f"item received: {name}, category: {category}"}

@app.get("/items")
def show_item():
    read_file=open('items.json','r')
    read_data=json.load(read_file)
    read_file.close()
    return {f"{read_data}"}

@app.get("/image/{items_image}")
async def get_image(items_image):
    # Create image path
    image = images / items_image

    if not items_image.endswith(".jpg"):
        raise HTTPException(status_code=400, detail="Image path does not end with .jpg")

    if not image.exists():
        logger.debug(f"Image not found: {image}")
        image = images / "default.jpg"

    return FileResponse(image)
