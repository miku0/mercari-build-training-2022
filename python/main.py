from distutils.command.upload import upload
import os
import logging
import pathlib
import json
import sqlite3
import hashlib
from fastapi import FastAPI, Form, HTTPException,File,UploadFile
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
def add_item(name: str = Form(...),category: str = Form(...),image: str = Form(...)):
#def add_item(name: str = Form(...),category: str = Form(...),image: UploadFile = File(...)):
    dbname = '../db/mercari.sqlite3'
    conn = sqlite3.connect(dbname)
    cur = conn.cursor()
    image_HashedName = hashlib.sha256(image.encode('utf-8')).hexdigest()+".jpg"
    sql = 'insert into items (name, category, image_filename) values (?,?,?)'
    data = (name,category,image_HashedName)
    cur.execute(sql, data)
    conn.commit()
    conn.close()

    return {"message": f"item received: {name}, category: {category},name: {image_HashedName}"}

@app.get("/items/{item_id}")
def show_item_info(item_id):
    dbname = '../db/mercari.sqlite3'
    conn = sqlite3.connect(dbname)
    cur = conn.cursor()
    cur.execute("select name,category,image_filename from items where id = ?", item_id)
    items = cur.fetchall()
    result = {'name': items[0][0], 'category': items[0][1],'image':items[0][2]}
    conn.commit()
    conn.close()
    return result


@app.get("/items")
def show_item():
    dbname = '../db/mercari.sqlite3'
    conn = sqlite3.connect(dbname)
    cur = conn.cursor()
    cur.execute('select id,name,category from items')
    items = cur.fetchall()
    conn.commit()
    conn.close()
    return items

@app.get("/search")
def search_item(keyword: str):
    dbname = '../db/mercari.sqlite3'
    conn = sqlite3.connect(dbname)
    cur = conn.cursor()
    cur.execute("select * from items where name like ?", ('%'+keyword+'%',))
    items = cur.fetchall()
    result = {'items':[]}
    for i in range(len(items)):
        result['items'].append({'name':items[i][1],'category':items[i][2]})
    conn.commit()
    conn.close()

    return result

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
