# utils.py

from typing import List

from bs4 import BeautifulSoup
import streamlit as st
from streamlit_extras.switch_page_button import switch_page

from essay_mentor_app.backend.aea_datamodel import (
    EssayContentItem,
    BaseContentItem,
    Reason,
)


def page_init(is_startpage=False):
    if not is_startpage:
        st.session_state.update(st.session_state)
    st.set_page_config(
        page_title="Tessy - Essay Tutor",
        page_icon="👩‍🏫",
    )
    if not "aea" in st.session_state and not is_startpage:
        switch_page("Start")


def clear_associated_keys(content_elements: List[BaseContentItem]):
    for element in content_elements:
        st.session_state.pop(f"reasons_txt_{element.uid}", None)
        if isinstance(element, Reason):
            # remove element label from all multi select widget lists
            for essay_element in st.session_state.aea.essay_content_items:
                multi_select_list = st.session_state.get(f"multiselect_assreas_{essay_element.uid}", [])
                if element.label in multi_select_list:
                    multi_select_list.remove(element.label)
        if isinstance(element, EssayContentItem):
            st.session_state.pop(f"multiselect_assreas_{element.uid}", None)



def parse_essay_content(essay_html) -> List[EssayContentItem]:
    soup = BeautifulSoup(essay_html, 'html.parser')
    content_items = []
    counter = 0
    for element in soup.find_all(['h1','h2','h3','h4','p','ul','ol']):
        html=str(element)
        level = 0
        if element.name in ['h1','h2','h3','h4']:
            level = ['h1','h2','h3','h4'].index(element.name) + 1
        else:
            counter += 1
        content_items.append(
            EssayContentItem(
                name=element.name,
                text=element.text,
                html=html,
                heading_level=level,
                label=f"{counter:03d}" if level==0 else "",
            )
        )
    return content_items
