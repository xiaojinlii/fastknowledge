import time
from typing import List, Optional
from urllib.parse import urlencode

from fastapi import APIRouter, Depends, Body, Request
from langchain.chains import LLMChain
from langchain_core.prompts import ChatPromptTemplate
from pydantic import BaseModel, Field
from starlette.responses import JSONResponse

from application.settings import VECTOR_SEARCH_TOP_K, SCORE_THRESHOLD, TEMPERATURE, LLM_MODELS, SEARCH_SERVER_URL, \
    MAX_TOKENS
from xiaoapi.core import logger
from xiaoapi.response import ErrorResponse
from .history import History
from .utils import search_docs, get_prompt_template, get_ChatOpenAI

router = APIRouter()


class KnowledgeBaseChatRequest(BaseModel):
    query: str = Field(..., description="用户输入", examples=["你好"])
    knowledge_base_name: str = Field(..., description="知识库名称", examples=["samples"])
    top_k: int = Field(VECTOR_SEARCH_TOP_K, description="匹配向量数")
    score_threshold: float = Field(
        SCORE_THRESHOLD,
        description="知识库匹配相关度阈值，取值范围在0-1之间，SCORE越小，相关度越高，取到1相当于不筛选，建议设置在0.5左右",
        ge=0,
        le=2
    )

    history: List[History] = Field(
        [],
        description="历史对话",
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
        title = "Knowledge Base Chat Request"
        validate_assignment = True
        protected_namespaces = ()  # 添加这一行来忽略'模型_'前缀的保护性警告


@router.post("/knowledge_base_chat", summary="与知识库对话")
async def knowledge_base_chat(request_data: KnowledgeBaseChatRequest):
    try:
        start_time = time.time()
        docs = await search_docs(request_data.query, request_data.knowledge_base_name, request_data.top_k, request_data.score_threshold)
        end_time = time.time()
        logger.debug(f"search_docs:{docs}, time:{end_time-start_time}")
        context = "\n".join([doc.page_content for doc in docs])

        if len(docs) == 0:  # 如果没有找到相关文档，使用empty模板
            prompt_template = get_prompt_template("knowledge_base_chat", "empty")
        else:
            prompt_template = get_prompt_template("knowledge_base_chat", request_data.prompt_name)

        history = [History.from_data(h) for h in request_data.history]
        input_msg = History(role="user", content=prompt_template).to_msg_template(False)
        chat_prompt = ChatPromptTemplate.from_messages(
            [i.to_msg_template() for i in history] + [input_msg])

        start_time = time.time()
        model = get_ChatOpenAI(
            model_name=request_data.model_name,
            temperature=request_data.temperature,
            max_tokens=request_data.max_tokens
        )
        chain = LLMChain(prompt=chat_prompt, llm=model)
        answer = await chain.ainvoke({"context": context, "question": request_data.query})
        end_time = time.time()
        logger.debug(f"llm response:{answer['text']}, time:{end_time-start_time}")

        source_documents = []
        for inum, doc in enumerate(docs):
            filename = doc.metadata.get("source")
            parameters = urlencode({"knowledge_base_name": request_data.knowledge_base_name, "file_name": filename})
            url = f"{SEARCH_SERVER_URL}/knowledge_base/download_doc?" + parameters
            text = f"""出处 [{inum + 1}] [{filename}]({url}) \n\n{doc.page_content}\n\n"""
            source_documents.append(text)

        if len(source_documents) == 0:  # 没有找到相关文档
            source_documents.append(f"<span style='color:red'>未找到相关文档,该回答为大模型自身能力解答！</span>")

        return JSONResponse({"code": 200, "answer": answer["text"], "docs": source_documents})

    except Exception as e:
        return ErrorResponse(f"查询知识库失败：{e}")
