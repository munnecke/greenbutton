from fastapi import FastAPI, UploadFile, File
import pandas as pd
from io import StringIO

app = FastAPI()

@app.get("/test")
async def test_route():
    return {"message": "Test route is working!"}

@app.post("/upload")
async def upload_file(file: UploadFile = File(...)):
    contents = await file.read()
    df = pd.read_csv(StringIO(contents.decode('utf-8')))
    # Now you can use the DataFrame `df` to analyze the data
    # ...
    return {"filename": file.filename}