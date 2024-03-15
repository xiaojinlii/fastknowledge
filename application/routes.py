from fastapi import FastAPI

# from modules.quickstart.routes import router as quickstart_router
from modules.fastknowledge.routers_knowledge_base_chat import router as knowledge_base_chat_router
from modules.fastknowledge.routers_llm_chat import router as llm_chat_router
from modules.fastknowledge.routers_search import router as search_router


def register_routes(app: FastAPI):
    """
    注册路由
    """

    # app.include_router(quickstart_router, prefix="/quickstart", tags=["快速开始"])
    app.include_router(knowledge_base_chat_router, prefix="/chat", tags=["Chat"])
    app.include_router(llm_chat_router, prefix="/chat", tags=["Chat"])
    app.include_router(search_router, prefix="/chat", tags=["Chat"])
