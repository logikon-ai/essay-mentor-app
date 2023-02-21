import logging

import plotly.graph_objects as go
import pandas as pd


import markdown
import streamlit as st
from streamlit_extras.switch_page_button import switch_page

from backend.aea_datamodel import ArgumentativeEssayAnalysis
from backend.components import display_essay, parse_essay_content
import backend.examples

st.set_page_config(
    page_title="Welcome",
    page_icon="👩‍🏫",
)

def main():

    st.session_state.update(st.session_state)

    st.title('TESSY – Essay Tutor')
    st.write('**The AI Co-Tutor that supports you in writing better essays, and your teacher in grading them.**')







    if not "aea" in st.session_state:
        st.session_state["aea"] = ArgumentativeEssayAnalysis()

    if st.session_state.aea.essay_content_items:
        st.write("(Reload this page to start over with another text.)")
        st.write("------")
        st.write("*The essay that's currently being processed*:")
        display_essay(
            st.session_state.aea.essay_content_items,
            # reasons=[
            #     Reason("text","lab1","parentuid"),
            #     Reason("text","lab2","parentuid"),
            #     Reason("text","lab3","parentuid"),
            #     Reason("text","lab4","parentuid"),
            # ]
        )
        st.stop()

    if "essay_raw" not in st.session_state or st.session_state.essay_raw is None: 
        st.session_state["essay_raw"] = "" 


    col1, col2 = st.columns(2)
    with col1:
        # file uploader
        uploaded_file = st.file_uploader("You can upload your essay ...", type=["txt", "md", "pdf"])
    with col2:
        # select example essay
        def paste_example_essay():
            if st.session_state.example_essay_id == "Example 1":
                st.session_state["essay_raw"] = backend.examples.GUARDIAN1
            else:
                st.session_state["essay_raw"] = st.session_state.example_essay_id
        st.selectbox(
            "... or select an example ...",
            ["", "Example 1", "Example 2"],
            on_change=paste_example_essay,
            key="example_essay_id",
        )
        

    essay_raw = st.text_area(
        "... or directly paste your text here:",
        height=320,
        key="essay_raw",
    )

    if not essay_raw:
        st.warning("No essay text provided yet.")
        placeholder = st.empty()
    else:
        essay_html = markdown.markdown(essay_raw)
        st.success(
            "Your essay is ready to be analysed."
        )
        placeholder = st.empty()
        st.write("------")
        with st.expander("Preview essay structure (click to expand)"):
            display_essay(essay_html)
            st.write(" ")

    with placeholder:
        if st.button("Use this text and proceed with next step", disabled=not(essay_raw)):
            aea: ArgumentativeEssayAnalysis = st.session_state.aea
            aea.essaytext_md = essay_raw
            essay_html = markdown.markdown(essay_raw)
            aea.essaytext_html = essay_html
            aea.essay_content_items = parse_essay_content(essay_html)
            switch_page("Describe Main Question And Claims")



        #st.write("------")
        #st.write("Debugging:")
        #st.code(st.session_state.essay_raw if "essay_raw" in st.session_state else "")

if __name__ == '__main__':
    main()
