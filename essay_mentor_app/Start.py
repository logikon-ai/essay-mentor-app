from io import StringIO
import logging

import markdown
import markdownify
import plotly.graph_objects as go
import pandas as pd
from PyPDF2 import PdfReader
import streamlit as st
from streamlit_extras.switch_page_button import switch_page

from backend.aea_datamodel import ArgumentativeEssayAnalysis
from backend.components import display_essay, parse_essay_content
import backend.examples

st.set_page_config(
    page_title="Tessy - Essay Tutor",
    page_icon="👩‍🏫",
)

def main():

    st.session_state.update(st.session_state)

    st.title('TESSY – Essay Tutor')
    st.write('**The AI Co-Tutor that supports you in writing better essays, and your teacher in grading them.**')



    if not "aea" in st.session_state:
        st.session_state["aea"] = ArgumentativeEssayAnalysis()
    aea:ArgumentativeEssayAnalysis = st.session_state.aea

    if aea.essay_content_items:
        st.write("(Reload this page to start over with another text.)")
        st.write("------")
        st.write("*The essay that's currently being processed*:")
        display_essay(st.session_state.aea.essay_content_items)
        st.stop()

    if "essay_raw" not in st.session_state or st.session_state.essay_raw is None: 
        st.session_state["essay_raw"] = "" 


    col1, col2 = st.columns(2)
    with col1:
        # file uploader
        uploaded_file = st.file_uploader("You can upload your essay ...", type=["txt", "md", "pdf"])
        if uploaded_file is not None:
            essay_raw:str = ""
            if uploaded_file.name.endswith(".pdf"):
                reader = PdfReader(uploaded_file)
                for page in reader.pages:
                    essay_raw += (page.extract_text())
                    essay_raw += "\n\n"
            elif uploaded_file.name.endswith(".txt") or uploaded_file.name.endswith(".md"):
                stringio = StringIO(uploaded_file.getvalue().decode("utf-8"))
                tmp_text = stringio.read()
                # remove html tags:
                tmp_text = markdown.markdown(tmp_text)
                tmp_text = markdownify.markdownify(tmp_text)
                essay_raw = tmp_text
            st.session_state["essay_raw"] = essay_raw

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
        height=280,
        key="essay_raw",
        help=(
            "Please use basic [markdown formatting](https://www.markdownguide.org/basic-syntax/), in particular:\n "
            " * '#', '##', '###' for headings\n"
            " * paragraphs are separated by an empty line\n"
        )
    )

    if not essay_raw:
        # info with lightbulb icon
        st.info(
            "TIP: Instead of uploading a file, consider converting "
            "it with https://pandoc.org/try/ to markdown and paste "
            "the resulting text.",
            icon="💡"
        )
        placeholder = st.empty()
    else:
        essay_html = markdown.markdown(essay_raw)
        st.success(
            "Your essay is ready to be analysed. (Preview essay structure below.)"
        )
        placeholder = st.empty()
        st.write("------")
        with st.expander("Preview essay structure (click to expand)"):
            display_essay(essay_html)
            st.write(" ")

    with placeholder:
        if st.button("Use this text and proceed with next step", disabled=not(essay_raw)):
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
