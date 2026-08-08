from fastapi import FastAPI

app = FastAPI()

@app.get("/getProducts")
def read_root():
    return {"message": "Welcome to Elite Shoppe App API!"}
