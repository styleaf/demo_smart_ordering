from fastapi import FastAPI
import uvicorn

app = FastAPI()

@app.get("/hello")
def say_hello():
    return {"state":200}

if __name__ == "__main__":
    uvicorn.run(app)