from typing import List, Optional

from fastapi import APIRouter, Depends, Body, Request
from langchain.chains import LLMChain
from langchain_core.prompts import ChatPromptTemplate
from pydantic import BaseModel, Field
from starlette.responses import JSONResponse

from application.settings import TEMPERATURE, LLM_MODELS, MAX_TOKENS
from xiaoapi.core import logger
from xiaoapi.response import ErrorResponse
from .history import History
from .utils import get_prompt_template, get_ChatOpenAI

router = APIRouter()


class LLMChatRequest(BaseModel):
    query: str = Field(..., description="用户输入", examples=["恼羞成怒"])
    history: List[History] = Field(
        [],
        description="历史对话，设为一个整数可以从数据库中读取历史消息",
        examples=[[
            {"role": "user", "content": "我们来玩成语接龙，我先来，生龙活虎"},
            {"role": "assistant", "content": "虎头虎脑"}]
        ]
    )
    model_name: str = Field(LLM_MODELS[0], description="LLM 模型名称。")
    temperature: float = Field(TEMPERATURE, description="LLM 采样温度", ge=0.0, le=1.0)
    max_tokens: int = Field(MAX_TOKENS, description="限制LLM生成Token数量，默认None代表模型最大值")
    prompt_name: str = Field("default", description="使用的prompt模板名称(在configs/prompt_config.py中配置)")

    class Config:
        title = "LLM Chat Request"
        validate_assignment = True
        protected_namespaces = ()  # 添加这一行来忽略'模型_'前缀的保护性警告


@router.post("/llm_chat", summary="与llm模型对话")
async def llm_chat(request_data: LLMChatRequest):
    try:
        history = [History.from_data(h) for h in request_data.history]
        prompt_template = get_prompt_template("llm_chat", request_data.prompt_name)
        input_msg = History(role="user", content=prompt_template).to_msg_template(False)
        chat_prompt = ChatPromptTemplate.from_messages(
            [i.to_msg_template() for i in history] + [input_msg])

        model = get_ChatOpenAI(
            model_name=request_data.model_name,
            temperature=request_data.temperature,
            max_tokens=request_data.max_tokens
        )
        chain = LLMChain(prompt=chat_prompt, llm=model)
        answer = await chain.ainvoke({"input": request_data.query})

        return JSONResponse({"answer": answer["text"]})

    except Exception as e:
        return ErrorResponse(f"查询知识库失败：{e}")
