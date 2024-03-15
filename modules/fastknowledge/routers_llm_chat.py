from typing import List, Optional
from urllib.parse import urlencode

from fastapi import APIRouter, Depends, Body, Request
from langchain.chains import LLMChain
from langchain_core.prompts import ChatPromptTemplate
from starlette.responses import JSONResponse

from application.settings import TEMPERATURE, LLM_MODELS, MAX_TOKENS
from core.logger import logger
from .history import History
from .utils import get_prompt_template, get_ChatOpenAI

router = APIRouter()


@router.post("/llm_chat", summary="与llm模型对话")
async def llm_chat(
        query: str = Body(..., description="用户输入", examples=["恼羞成怒"]),
        history: List[History] = Body([],
                                      description="历史对话，设为一个整数可以从数据库中读取历史消息",
                                      examples=[[
                                          {"role": "user",
                                           "content": "我们来玩成语接龙，我先来，生龙活虎"},
                                          {"role": "assistant", "content": "虎头虎脑"}]]
                                      ),

        model_name: str = Body(LLM_MODELS[0], description="LLM 模型名称。"),
        temperature: float = Body(TEMPERATURE, description="LLM 采样温度", ge=0.0, le=2.0),
        max_tokens: Optional[int] = Body(MAX_TOKENS, description="限制LLM生成Token数量，默认None代表模型最大值"),
        prompt_name: str = Body("default", description="使用的prompt模板名称(在configs/prompt_config.py中配置)"),
):
    history = [History.from_data(h) for h in history]
    prompt_template = get_prompt_template("llm_chat", prompt_name)
    input_msg = History(role="user", content=prompt_template).to_msg_template(False)
    chat_prompt = ChatPromptTemplate.from_messages(
        [i.to_msg_template() for i in history] + [input_msg])

    model = get_ChatOpenAI(
        model_name=model_name,
        temperature=temperature,
        max_tokens=max_tokens
    )
    chain = LLMChain(prompt=chat_prompt, llm=model)
    answer = await chain.ainvoke({"input": query})

    return JSONResponse({"answer": answer["text"]})
