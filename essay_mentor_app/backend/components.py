# passive and interactive gui components 

from bs4 import BeautifulSoup
import markdownify
import streamlit as st

def display_essay(essay_html):
    soup = BeautifulSoup(essay_html, 'html.parser')
    for element in soup.find_all(['h1','h2','h3','h4','p','ul','ol']):
        html=str(element)
        if element.name in ['h1','h2','h3','h4']:
            level = ['h1','h2','h3','h4'].index(element.name)
            st.write(f"{'#'*(level+3)} {element.text}")
        else:
            icon = "¶" if element.name=='p' else "⋮"
            summary = f"{icon}  {element.text[:10]}..."
            md = markdownify.markdownify(html)
            st.write(
                f"<details><summary>{summary}</summary>{element.text}</details>",
                unsafe_allow_html=True
            )
            #st.code(md)
