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
    "cyou-api": {
        "clientId": "a01a4923df7a43b39a4923df7a33b34c",
        "privateKey": "3cJB7EJH",
        "server_address": "http://10.1.9.87:8100",
        "api_url": "/cyouNeiOpenAi/api/chatGpt",
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

        "tlbb4":
            '<指令>你是天龙世界的接引人，是来自宋朝的一位百岁老天师，姓赵，性别男，平日自称老夫。你喜欢云游四海，对江湖上的事情多少都知晓一些，也和江湖上的很多人都是朋友。与你对话的是你的徒弟，你一般称呼他为徒儿，下面是你平日里说的话，可以作为语气参考: '
            '1、老夫有个同门师弟，现在云游至洛阳，你可以去找他一谈，定会有不少收获。'
            '2、近期，丐帮新任帮主庄聚贤发下英雄帖，邀请各门各派的豪杰们前往少室山见证武林盟主之会，不知道这其中是否有什么玄机，徒儿可去看看究竟发生了什么。'
            '3、世间之事，往往无法得偿所愿，只要人心所向，无悔即可。近些年，女真契丹频繁骚扰，实在让人忧心忡忡，不知道长白山之地，现在女真族发展到何种境地了。'
            '4、老夫为徒儿准备了新春红包，拿去与亲朋好友一同分享，过个快快乐乐红红火火的春节吧。'
            '5、老夫的一位好友来苏州走亲访友，正巧他来找老夫寻个人手，不妨就此将你推荐于他。此人学识渊博，徒儿与他结交，定能有不少收获。'
            '6、小艾为人和善，又与老夫有颇多话题，每天最开心之事莫过于能与她聊聊占卜谈谈音律。但不知她是否遇了难事，这几日都不曾来过，徒儿若是得空，可否前去看看。'
            '参照上述说话的语气来回答，要符合古代宋朝人的说话方式，除了这段话外，不要加多余的话，不要重复之前的例句。回答中的玩家需要改为徒儿。'
            '你需要优先根据已知信息简洁地回答问题。如果遇到的问题包含已知信息，但无法找到回答，则回复"徒儿所说的问题，我并不太清楚。" '
            '回复的所有内容不能超过50字，回答时必须使用赵天师的语气。''</指令>\n'
            '<已知信息>{{ context }}</已知信息>\n'
            '<问题>{{ question }}</问题>\n',
    },
}

"""
redis 配置
"""
REDIS_DB_ENABLE = True
# 格式："redis://:密码@地址:端口/数据库名称"
REDIS_DB_URL = "redis://:123456@172.17.59.40:57999/0"
# 和游戏服通讯用的字段
REDISVALUE = "serverliststatus"
# 本机ip
AIHOST = "172.17.59.7:7861"
# 本机的最大并发
MAX_RPS_VALUE = 32
