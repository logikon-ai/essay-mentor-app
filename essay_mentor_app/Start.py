import logging

from bs4 import BeautifulSoup
import markdown
import markdownify
import streamlit as st

from backend.aea_datamodel import ArgumentativeEssayAnalysis
from backend.components import display_essay, parse_essay_content

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

    if st.session_state.aea.essaytext_html:
        st.write("(Reload this page to start over with another text.)")
        st.write("## Your Essay:")
        st.write("------")
        display_essay(st.session_state.aea.essaytext_html)
        st.stop()

    if "essay_raw" not in st.session_state or st.session_state.essay_raw is None: 
        st.session_state["essay_raw"] = "" 


    col1, col2 = st.columns(2)
    with col1:
        # file uploader
        uploaded_file = st.file_uploader("You can upload your essay ...", type=["txt", "md", "pdf"])
    with col2:
        # select example essay
        example_essay = st.selectbox(
            "... or select an example ...",
            ["", "Example 1", "Example 2"]
        )

    essay_raw = st.text_area(
        "... or directly paste your text here:",
        height=400,
        key="essay_raw",
    )


    if essay_raw:
        essay_html = markdown.markdown(essay_raw)


        with st.expander("Preview essay structure (click to expand)"):

            display_essay(essay_html)
            st.write(" ")


        if st.button("Proceed with this text"):
            aea: ArgumentativeEssayAnalysis = st.session_state.aea
            aea.essaytext_md = essay_raw
            aea.essaytext_html = essay_html
            aea.essay_content_items = parse_essay_content(essay_html)

        st.write("------")
        st.write("Debugging:")
        st.code(st.session_state.essay_raw if "essay_raw" in st.session_state else "")

if __name__ == '__main__':
    main()
