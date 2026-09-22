from loguru import logger
from fastapi import FastAPI, Request, Response, status

app = FastAPI()


@app.get("/")
async def root():
    return {"status": "ini dari root"}  # json


@app.get("/get")
async def endpoint_get():
    return {"http_method": "get"}


# http request -> get dan post
@app.post("/post")
async def endpoint_post():
    return {"http_method": "post"}


@app.post("/webhook")
async def telegram_webhook(request: Request):
    req_body = await request.json()
    logger.debug(req_body)
    return Response(status_code=status.HTTP_200_OK)