import httpx
from fastapi import APIRouter, Depends, Body, Request
from starlette.responses import JSONResponse

from application.settings import SCORE_THRESHOLD, SEARCH_SERVER_URL


router = APIRouter()


def do_check_str_like(query: str, score_threshold: SCORE_THRESHOLD):
    data = {"query": query, "score_threshold": score_threshold}
    url = f"{SEARCH_SERVER_URL}/knowledge_base/check_str_like"
    response = httpx.post(url, json=data)

    res = response.json()
    return res


def do_set_qa_into_db(query: str, answer: str):
    data = {"query": query, "answer": answer}
    url = f"{SEARCH_SERVER_URL}/knowledge_base/set_qa_into_db"
    response = httpx.post(url, json=data)

    res = response.json()
    return res


@router.get("/check_str_like", summary="检测问题相似度，并返回已加载的问题和答案")
def check_str_like(query: str, score_threshold: float = SCORE_THRESHOLD):
    return JSONResponse(do_check_str_like(query, score_threshold))


@router.post("/set_qa_into_db", summary="将需要缓存的问题和答案加入到向量库")
def set_qa_into_db(
        query: str = Body("", description="问题", examples=["你是谁"]),
        answer: str = Body("", description="答案", examples=["我是xxx"]),
):
    return JSONResponse(do_set_qa_into_db(query, answer))
