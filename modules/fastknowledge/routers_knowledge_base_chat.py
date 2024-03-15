import time
from typing import List, Optional
from urllib.parse import urlencode

from fastapi import APIRouter, Depends, Body, Request
from langchain.chains import LLMChain
from langchain_core.prompts import ChatPromptTemplate
from starlette.responses import JSONResponse

from application.settings import VECTOR_SEARCH_TOP_K, SCORE_THRESHOLD, TEMPERATURE, LLM_MODELS, SEARCH_SERVER_URL, \
    MAX_TOKENS
from core.logger import logger
from .history import History
from .utils import search_docs, get_prompt_template, get_ChatOpenAI

router = APIRouter()


@router.post("/knowledge_base_chat", summary="与知识库对话")
async def knowledge_base_chat(
        query: str = Body(..., description="用户输入", examples=["你好"]),
        knowledge_base_name: str = Body(..., description="知识库名称", examples=["samples"]),
        top_k: int = Body(VECTOR_SEARCH_TOP_K, description="匹配向量数"),
        score_threshold: float = Body(
            SCORE_THRESHOLD,
            description="知识库匹配相关度阈值，取值范围在0-1之间，SCORE越小，相关度越高，取到1相当于不筛选，建议设置在0.5左右",
            ge=0,
            le=2
        ),
        history: List[History] = Body(
            [],
            description="历史对话",
            examples=[[
                {"role": "user",
                 "content": "我们来玩成语接龙，我先来，生龙活虎"},
                {"role": "assistant",
                 "content": "虎头虎脑"}]]
        ),
        model_name: str = Body(LLM_MODELS[0], description="LLM 模型名称。"),
        temperature: float = Body(TEMPERATURE, description="LLM 采样温度", ge=0.0, le=1.0),
        max_tokens: int = Body(
            MAX_TOKENS,
            description="限制LLM生成Token数量，默认None代表模型最大值"
        ),
        prompt_name: str = Body(
            "default",
            description="使用的prompt模板名称(在configs/prompt_config.py中配置)"
        ),
):
    time1 = time.time()
    docs = search_docs(query, knowledge_base_name, top_k, score_threshold)
    time2 = time.time()
    context = "\n".join([doc.page_content for doc in docs])

    if len(docs) == 0:  # 如果没有找到相关文档，使用empty模板
        prompt_template = get_prompt_template("knowledge_base_chat", "empty")
    else:
        prompt_template = get_prompt_template("knowledge_base_chat", prompt_name)

    history = [History.from_data(h) for h in history]
    input_msg = History(role="user", content=prompt_template).to_msg_template(False)
    chat_prompt = ChatPromptTemplate.from_messages(
        [i.to_msg_template() for i in history] + [input_msg])

    time3 = time.time()
    model = get_ChatOpenAI(
        model_name=model_name,
        temperature=temperature,
        max_tokens=max_tokens
    )
    time4 = time.time()
    chain = LLMChain(prompt=chat_prompt, llm=model)
    answer = await chain.ainvoke({"context": context, "question": query})
    time5 = time.time()
    logger.info(f"---> search:{time2-time1}, getai:{time4-time3}, ai:{time5-time4}")

    source_documents = []
    for inum, doc in enumerate(docs):
        filename = doc.metadata.get("source")
        parameters = urlencode({"knowledge_base_name": knowledge_base_name, "file_name": filename})
        url = f"{SEARCH_SERVER_URL}/knowledge_base/download_doc?" + parameters
        text = f"""出处 [{inum + 1}] [{filename}]({url}) \n\n{doc.page_content}\n\n"""
        source_documents.append(text)

    if len(source_documents) == 0:  # 没有找到相关文档
        source_documents.append(f"<span style='color:red'>未找到相关文档,该回答为大模型自身能力解答！</span>")

    return JSONResponse({"answer": answer["text"], "docs": source_documents})
