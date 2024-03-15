from typing import List, Optional, Callable, Any

import httpx
from langchain_core.documents import Document
from langchain_openai import ChatOpenAI

from application.settings import VECTOR_SEARCH_TOP_K, SCORE_THRESHOLD, SEARCH_SERVER_URL, LLM_MODELS_CONFIG
from .langchain.cyou_chat import ChatCyou


class DocumentWithVSId(Document):
    """
    矢量化后的文档
    """
    id: str = None
    score: float = 3.0


def dict_to_document(doc_dict):
    return DocumentWithVSId(page_content=doc_dict["page_content"], metadata=doc_dict["metadata"], id=doc_dict["id"], score=doc_dict["score"])


def search_docs(
        query: str = "",
        knowledge_base_name: str = "",
        top_k: int = VECTOR_SEARCH_TOP_K,
        score_threshold: float = SCORE_THRESHOLD,
) -> List[DocumentWithVSId]:

    data = {
        "query": query,
        "knowledge_base_name": knowledge_base_name,
        "top_k": top_k,
        "score_threshold": score_threshold,
    }

    headers = {
        'accept': 'application/json',
        'Content-Type': 'application/json'
    }
    url = f"{SEARCH_SERVER_URL}/knowledge_base/search_docs"
    response = httpx.post(url, json=data, headers=headers)

    res = response.json()
    result = [dict_to_document(d) for d in res]
    return result


def get_prompt_template(type: str, name: str) -> Optional[str]:
    from application import settings
    import importlib
    importlib.reload(settings)
    return settings.PROMPT_TEMPLATES[type].get(name)


def get_ChatOpenAI(
        model_name: str,
        temperature: float,
        max_tokens: int = None,
        streaming: bool = False,
        callbacks: List[Callable] = [],
        verbose: bool = True,
        **kwargs: Any,
) -> ChatOpenAI:
    if model_name == "cyou-api":
        configs = LLM_MODELS_CONFIG.get(model_name)
        model = ChatCyou(
            cyou_api_base=configs["server_address"],
            cyou_api_url=configs["api_url"],
            cyou_client_id=configs["clientId"],
            cyou_private_key=configs["privateKey"],
            temperature=temperature,
            verbose=verbose,
            callbacks=callbacks,
        )
    else:
        configs = LLM_MODELS_CONFIG.get("openai-api")
        model = ChatOpenAI(
            streaming=streaming,
            verbose=verbose,
            callbacks=callbacks,
            openai_api_key=configs["api_key"],
            openai_api_base=configs["api_base_url"],
            model_name=model_name,
            temperature=temperature,
            max_tokens=max_tokens,
            **kwargs
        )

    return model
