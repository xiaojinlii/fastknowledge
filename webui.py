import streamlit as st
from streamlit_option_menu import option_menu

from webui_pages.api_request import ApiRequest
from webui_pages.dialogue.dialogue import dialogue_page
import os
from application.settings import VERSION, SEARCH_SERVER_URL, TITLE

api = ApiRequest()
api_search = ApiRequest(SEARCH_SERVER_URL)

if __name__ == "__main__":
    st.set_page_config(
        f"{TITLE} WebUI",
        os.path.join("static/system", "favicon.png"),
        initial_sidebar_state="expanded",
        menu_items={
            'Get Help': 'https://github.com/xiaojinlii/fastknowledge',
            'Report a bug': "https://gitee.com/xiaojinli/fast-knowledge/issues",
            'About': f"""欢迎使用 {TITLE} WebUI {VERSION}！"""
        }
    )

    # pages = {
    #     "对话": {
    #         "icon": "chat",
    #         "func": dialogue_page,
    #     },
    # }

    with st.sidebar:

        st.image(
            os.path.join(
                "static/system",
                "facebook_cover_photo_1.png"
            ),
            use_column_width=True
        )
        st.caption(
            f"""<p align="right">当前版本：{VERSION}</p>""",
            unsafe_allow_html=True,
        )

    #     options = list(pages)
    #     icons = [x["icon"] for x in pages.values()]
    #
    #     default_index = 0
    #     selected_page = option_menu(
    #         "",
    #         options=options,
    #         icons=icons,
    #         # menu_icon="chat-quote",
    #         default_index=default_index,
    #     )
    #
    # if selected_page in pages:
    #     pages[selected_page]["func"](api=api, api_search=api_search)
    dialogue_page(api=api, api_search=api_search)
