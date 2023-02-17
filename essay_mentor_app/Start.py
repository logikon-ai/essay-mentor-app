import logging

from bs4 import BeautifulSoup
import markdown
import markdownify
import streamlit as st
from streamlit_ace import st_ace

from backend.aea_datamodel import ArgumentativeEssayAnalysis
from backend.components import display_essay

st.set_page_config(
    page_title="Welcome",
    page_icon="👩‍🏫",
)

def main():

    st.session_state.update(st.session_state)

    st.title('Essay Mentor')
    st.write('This AI Co-Tutor supports you in writing better essays, and your teacher in grading them.')

    if not "aea" in st.session_state:
        st.session_state["aea"] = ArgumentativeEssayAnalysis()

    if st.session_state.aea.essaytext_html:
        st.write("(Reload this page to start over with another text.)")
        st.write("## Your Essay:")
        st.write("------")
        display_essay(st.session_state.aea.essaytext_html)
        st.stop()

    initial_text = ""
    if "essay_raw" in st.session_state and st.session_state.essay_raw is not None: 
        initial_text = st.session_state.essay_raw 
    essay_raw = st_ace(
        placeholder='Paste your essay here...',
        value=initial_text,
        language='markdown',
        theme='chrome',
        height=400,
        font_size=14,
        tab_size=4,
        wrap=True,
        show_gutter=True,
        show_print_margin=False, 
        auto_update=True,
        key="essay_raw",
    )

    if essay_raw:
        essay_html = markdown.markdown(essay_raw)

        st.write("------")

        display_essay(essay_html)

        st.write("------")

        if st.button("Proceed with this text"):
            st.session_state.aea.essaytext_md = essay_raw
            st.session_state.aea.essaytext_html = essay_html

        st.write("------")
        st.write("Debugging:")
        st.code(st.session_state.essay_raw if "essay_raw" in st.session_state else "")

if __name__ == '__main__':
    main()
