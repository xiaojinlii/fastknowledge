"""
FastAPI settings for project.
"""

import os
from pathlib import Path

# 项目根目录
BASE_DIR = Path(__file__).resolve().parent.parent

# 注意：不要在生产中打开调试运行!
DEBUG = False

####################
# PROJECT SETTINGS #
####################
TITLE = "Fast Knowledge"
DESCRIPTION = "基于 xiaoapi 的RAG系统"
VERSION = "0.0.1"


############
# UVICORN #
############
# 监听主机IP，默认开放给本网络所有主机
HOST = "0.0.0.0"
# 监听端口
PORT = 9000
# 工作进程数
WORKERS = 1


##############
# MIDDLEWARE #
##############
# List of middleware to use. Order is important; in the request phase, these
# middleware will be applied in the order given, and in the response
# phase the middleware will be applied in reverse order.
MIDDLEWARES = [
    "xiaoapi.middleware.register_request_log_middleware",
]


##################
# Fast Knowledge #
##################

LLM_MODELS = ["cyou-api"]

HISTORY_LEN = 3

MAX_TOKENS = 2048

TEMPERATURE = 0.7

# 知识库匹配向量数量
VECTOR_SEARCH_TOP_K = 3

# 知识库匹配的距离阈值，一般取值范围在0-1之间，SCORE越小，距离越小从而相关度越高。
# 但有用户报告遇到过匹配分值超过1的情况，为了兼容性默认设为1，在WEBUI中调整范围为0-2
SCORE_THRESHOLD = 1.0


# fast-search服务接口地址
SEARCH_SERVER_URL = "http://127.0.0.1:7862"


LLM_MODELS_CONFIG = {
    "openai-api": {
        "model_name": "gpt-4",  # 由接口传入，不会使用这个
        "api_base_url": "https://api.openai.com/v1",
        "api_key": "EMPTY",
    },
}


# prompt模板使用Jinja2语法，简单点就是用双大括号代替f-string的单大括号
# 本配置文件支持热加载，修改prompt模板后无需重启服务。
# 知识库和搜索引擎对话支持的变量：
#   - context: 从检索结果拼接的知识文本
#   - question: 用户提出的问题
PROMPT_TEMPLATES = {
    "llm_chat": {
        "default":
            '{{ input }}',

        "with_history":
            'The following is a friendly conversation between a human and an AI. '
            'The AI is talkative and provides lots of specific details from its context. '
            'If the AI does not know the answer to a question, it truthfully says it does not know.\n\n'
            'Current conversation:\n'
            '{history}\n'
            'Human: {input}\n'
            'AI:',

        "py":
            '你是一个聪明的代码助手，请你给我写出简单的py代码。 \n'
            '{{ input }}',
    },

    "knowledge_base_chat": {
        "default":
            '<指令>根据已知信息，简洁和专业的来回答问题。如果无法从中得到答案，请说 “根据已知信息无法回答该问题”，'
            '不允许在答案中添加编造成分，答案请使用中文。 </指令>\n'
            '<已知信息>{{ context }}</已知信息>\n'
            '<问题>{{ question }}</问题>\n',

        "text":
            '<指令>根据已知信息，简洁和专业的来回答问题。如果无法从中得到答案，请说 “根据已知信息无法回答该问题”，答案请使用中文。 </指令>\n'
            '<已知信息>{{ context }}</已知信息>\n'
            '<问题>{{ question }}</问题>\n',

        "empty":  # 搜不到知识库的时候使用
            '请你回答我的问题:\n'
            '{{ question }}\n\n',
    },
}
