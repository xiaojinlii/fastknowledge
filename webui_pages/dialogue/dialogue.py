import streamlit as st

from streamlit_chatbox import *
from datetime import datetime
import os
from typing import List, Dict

from application.settings import PROMPT_TEMPLATES, TEMPERATURE, HISTORY_LEN, VECTOR_SEARCH_TOP_K, SCORE_THRESHOLD, \
    LLM_MODELS
from webui_pages.api_request import ApiRequest, check_error_msg

chat_box = ChatBox(
    assistant_avatar=os.path.join(
        "static/system",
        "chat_icon.png"
    )
)


def get_messages_history(history_len: int, content_in_expander: bool = False) -> List[Dict]:
    """
    返回消息历史。
    content_in_expander控制是否返回expander元素中的内容，一般导出的时候可以选上，传入LLM的history不需要
    """

    def filter(msg):
        content = [x for x in msg["elements"] if x._output_method in ["markdown", "text"]]
        if not content_in_expander:
            content = [x for x in content if not x._in_expander]
        content = [x.content for x in content]

        return {
            "role": msg["role"],
            "content": "\n\n".join(content),
        }

    return chat_box.filter_history(history_len=history_len, filter=filter)


def dialogue_page(api: ApiRequest, api_search: ApiRequest):
    default_model = LLM_MODELS[0]

    if not chat_box.chat_inited:
        st.toast(
            f"欢迎使用 [`Fast-Knowledge`](https://gitee.com/xiaojinli/fast-knowledge) ! \n\n"
            f"当前运行的模型`{default_model}`, 您可以开始提问了."
        )
        chat_box.init_session()

    with st.sidebar:
        def on_mode_change():
            mode = st.session_state.dialogue_mode
            text = f"已切换到 {mode} 模式。"
            if mode == "知识库问答":
                cur_kb = st.session_state.get("selected_kb")
                if cur_kb:
                    text = f"{text} 当前知识库： `{cur_kb}`。"
            st.toast(text)

        dialogue_modes = [
            "知识库问答",
            "LLM 对话",
        ]
        dialogue_mode = st.selectbox(
            "请选择对话模式：",
            dialogue_modes,
            index=0,
            on_change=on_mode_change,
            key="dialogue_mode",
        )

        def on_llm_change():
            if llm_model:
                st.session_state["prev_llm_model"] = llm_model
                st.session_state["cur_llm_model"] = st.session_state.llm_model

        def llm_model_format_func(x):
            if x in LLM_MODELS:
                return f"{x} (Running)"
            return x

        llm_models = LLM_MODELS
        cur_llm_model = st.session_state.get("cur_llm_model", default_model)
        if cur_llm_model in llm_models:
            index = llm_models.index(cur_llm_model)
        else:
            index = 0
        llm_model = st.selectbox(
            "选择LLM模型：",
            llm_models,
            index,
            format_func=llm_model_format_func,
            on_change=on_llm_change,
            key="llm_model",
        )

        index_prompt = {
            "知识库问答": "knowledge_base_chat",
            "LLM 对话": "llm_chat",
        }
        prompt_templates_kb_list = list(PROMPT_TEMPLATES[index_prompt[dialogue_mode]].keys())
        prompt_template_name = prompt_templates_kb_list[0]
        if "prompt_template_select" not in st.session_state:
            st.session_state.prompt_template_select = prompt_templates_kb_list[0]

        def prompt_change():
            text = f"已切换为 {prompt_template_name} 模板。"
            st.toast(text)

        prompt_template_select = st.selectbox(
            "请选择Prompt模板：",
            prompt_templates_kb_list,
            index=0,
            on_change=prompt_change,
            key="prompt_template_select",
        )
        prompt_template_name = st.session_state.prompt_template_select
        temperature = st.slider("Temperature：", 0.0, 2.0, TEMPERATURE, 0.05)
        history_len = st.number_input("历史对话轮数：", 0, 20, HISTORY_LEN)

        if dialogue_mode == "知识库问答":
            def on_kb_change():
                st.toast(f"已加载知识库： {st.session_state.selected_kb}")

            with st.expander("知识库配置", True):
                kb_list = api_search.list_knowledge_bases()
                index = 0
                selected_kb = st.selectbox(
                    "请选择知识库：",
                    kb_list,
                    index=index,
                    on_change=on_kb_change,
                    key="selected_kb",
                )
                kb_top_k = st.number_input("匹配知识条数：", 1, 20, VECTOR_SEARCH_TOP_K)

                ## Bge 模型会超过1
                score_threshold = st.slider("知识匹配分数阈值：", 0.0, 2.0, float(SCORE_THRESHOLD), 0.01)

    # Display chat messages from history on app rerun
    chat_box.output_messages()

    chat_input_placeholder = "请输入对话内容，换行请使用Shift+Enter。 "

    if prompt := st.chat_input(chat_input_placeholder, key="prompt"):
        history = get_messages_history(history_len)
        chat_box.user_say(prompt)
        if dialogue_mode == "LLM 对话":
            chat_box.ai_say("正在思考...")
            ret = api.llm_chat(
                prompt,
                history=history,
                model=llm_model,
                prompt_name=prompt_template_name,
                temperature=temperature
            )
            chat_box.update_msg(ret["answer"], streaming=False)  # 更新最终的字符串，去除光标

        elif dialogue_mode == "知识库问答":
            chat_box.ai_say([
                f"正在查询知识库 `{selected_kb}` ...",
                Markdown("...", in_expander=True, title="知识库匹配结果", state="complete"),
            ])

            ret = api.knowledge_base_chat(
                prompt,
                knowledge_base_name=selected_kb,
                top_k=kb_top_k,
                score_threshold=score_threshold,
                history=history,
                model=llm_model,
                prompt_name=prompt_template_name,
                temperature=temperature
            )

            chat_box.update_msg(ret["answer"], element_index=0, streaming=False)
            chat_box.update_msg("\n\n".join(ret["docs"]), element_index=1, streaming=False)

    if st.session_state.get("need_rerun"):
        st.session_state["need_rerun"] = False
        st.rerun()

    now = datetime.now()
    with st.sidebar:

        cols = st.columns(2)
        export_btn = cols[0]
        if cols[1].button(
                "清空对话",
                use_container_width=True,
        ):
            chat_box.reset_history()
            st.rerun()

    export_btn.download_button(
        "导出记录",
        "".join(chat_box.export2md()),
        file_name=f"{now:%Y-%m-%d %H.%M}_对话记录.md",
        mime="text/markdown",
        use_container_width=True,
    )
