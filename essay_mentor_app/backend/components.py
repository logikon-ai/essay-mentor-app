# passive and interactive gui components 

from typing import List

from bs4 import BeautifulSoup
import markdownify
import streamlit as st
import uuid

from essay_mentor_app.backend.aea_datamodel import EssayContentItem

def parse_essay_content(essay_html) -> List[EssayContentItem]:
    soup = BeautifulSoup(essay_html, 'html.parser')
    content_items = []
    for element in soup.find_all(['h1','h2','h3','h4','p','ul','ol']):
        html=str(element)
        level = 0
        if element.name in ['h1','h2','h3','h4']:
            level = ['h1','h2','h3','h4'].index(element.name) + 1
        content_items.append(
            EssayContentItem(
                uid=str(uuid.uuid4()),
                name=element.name,
                text=element.text,
                html=html,
                heading_level=level,
            )
        )
    return content_items


def display_essay(essay_html):
    essay_content = parse_essay_content(essay_html)
    for element in essay_content:
        if element.name in ['h1','h2','h3','h4']:
            st.write(f"{'#'*(element.heading_level+3)} {element.text}")
        else:
            icon = "¶" if element.name=='p' else "⋮"
            summary = f"{icon}  {element.text[:10]}..."
            st.write(
                f"<details><summary>{summary}</summary>{element.text}</details>",
                unsafe_allow_html=True
            )
            # Debugging:
            #md = markdownify.markdownify(element.html)
            #st.code(md)
