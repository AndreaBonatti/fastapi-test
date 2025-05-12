from fastapi import FastAPI

app = FastAPI(
    title="FastAPI test",
    description="A test with the FastAPI library"
)

@app.get("/hello-world")
def hello_world():
    return {"Message" : "Hello World! :)"}