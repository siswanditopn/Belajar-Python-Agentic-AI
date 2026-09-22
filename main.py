from fastapi import FastAPI, Request, Response, status

app = FastAPI()

@app.get("/testing-root")
async def root():
    return {"status": "ok"}