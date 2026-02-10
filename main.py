from fastapi import FastAPI, HTTPException
import requests
import os

app = FastAPI(title="MAGMAxRICH API")

BASE_URL = "https://numb-api.vercel.app/get-info"
API_KEY = "worrior"

@app.get("/")
def home():
    return {"message": "Welcome to MAGMAxRICH API", "status": "Active"}

@app.get("/magma/lookup")
def lookup_number(phone: str):
    if not phone:
        raise HTTPException(status_code=400, detail="Phone number mangta hai!")

    params = {"phone": phone, "apikey": API_KEY}

    try:
        response = requests.get(BASE_URL, params=params)
        data = response.json()

        return {
            "api_name": "MAGMAxRICH",
            "result": data
        }
    except Exception as e:
        return {"error": str(e)}