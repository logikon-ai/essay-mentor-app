"""Start page of TESSY streamlit app"""

from io import StringIO
import markdown
import markdownify
from PyPDF2 import PdfReader
import requests

import streamlit as st
from streamlit_extras.switch_page_button import switch_page

from backend.aea_datamodel import ArgumentativeEssayAnalysis
import backend.components as components
import backend.examples
import backend.utils

DEBUG = True


# init
backend.utils.page_init(is_startpage=True)


def main():
    # setup session_state

    st.session_state.update(st.session_state)  # for multi-page state preservation
    st.session_state["DEBUG"] = DEBUG

    if not st.session_state.get("logged_in"):
        try:
            page = requests.get(st.secrets["logikon_server"]["url"]+"/ui")
            status = page.status_code
        except requests.exceptions.ConnectionError:
            status = 500
        if status == 200:
            st.session_state["logged_in"] = True
        else:
            st.error("Logikon server not reachable. Please try again later or contact Logikon staff.", icon="🚨")
            st.stop()

    if not "aea" in st.session_state:
        st.session_state["aea"] = ArgumentativeEssayAnalysis()
    aea: ArgumentativeEssayAnalysis = st.session_state.aea

    if not "has_been_submitted" in st.session_state:
        st.session_state["has_been_submitted"] = False

    if "essay_raw" not in st.session_state or st.session_state.essay_raw is None:
        st.session_state["essay_raw"] = ""

    # title

    st.title("TESSY - Essay Tutor")
    st.write(
        "**The AI Co-Tutor that supports you in writing better essays, and your teacher in grading them.**"
    )

    st.warning(
        "This is an experimental prototype 🧪 and a proof of concept 🔥 developed by [Logikon AI](http://logikon.ai).\n\n "
        "In particular, the app is powered by a medium-sized language model, "
        "which has been rudimentarily trained on a small fraction of Logikon's critical thinking dataset only. "
        "Please do not use it for grading essays -- yet 😉. ",
    )


    # if essay is already uploaded, don't show the upload form again
    if aea.essay_content_items:
        st.write("(Reload this page to start over with another text.)")
        st.write("------")
        st.write("*The essay that's currently being processed*:")
        components.display_essay(st.session_state.aea.essay_content_items)
        #if st.session_state.get("DEBUG"):
        #    st.json(st.session_state.aea.essay_content_items)
        st.stop()

    # essay upload form
    col1, col2 = st.columns(2)
    with col1:
        # file uploader
        uploaded_file = st.file_uploader(
            "You can upload your essay ...", type=["txt", "md", "pdf"]
        )
        if uploaded_file is not None:
            essay_raw: str = ""
            if uploaded_file.name.endswith(".pdf"):
                reader = PdfReader(uploaded_file)
                for page in reader.pages:
                    essay_raw += page.extract_text()
                    essay_raw += "\n\n"
            elif uploaded_file.name.endswith(".txt") or uploaded_file.name.endswith(
                ".md"
            ):
                stringio = StringIO(uploaded_file.getvalue().decode("utf-8"))
                tmp_text = stringio.read()
                # remove html tags:
                tmp_text = markdown.markdown(tmp_text)
                tmp_text = markdownify.markdownify(tmp_text)
                essay_raw = tmp_text
            st.session_state["essay_raw"] = essay_raw
            st.session_state["example_essay_id"] = ""  # reset example essay

    with col2:
        # select example essay
        def paste_example_essay():
            if st.session_state.example_essay_id == "Example 1 (Racism)":
                st.session_state["essay_raw"] = backend.examples.EX1_RACISM_PAPERSOWL
            elif st.session_state.example_essay_id == "Example 2 (Veganism)":
                st.session_state["essay_raw"] = backend.examples.EX2_VEGANISM_PAPERSOWL
            elif st.session_state.example_essay_id == "Example 3 (Critical Thinking)":
                st.session_state["essay_raw"] = backend.examples.EX3_CRITTHINK
            elif st.session_state.example_essay_id == "Example 4 (Debugging)":
                st.session_state["essay_raw"] = backend.examples.EX4_DEBUGGING
            else:
                st.session_state["essay_raw"] = st.session_state.example_essay_id

        options = [
            "",
            "Example 1 (Racism)",
            "Example 2 (Veganism)",
            "Example 3 (Critical Thinking)",
        ]
        if st.session_state.get("DEBUG"):
            options.append("Example 4 (Debugging)")
        st.selectbox(
            "... or select an example ...",
            options,
            on_change=paste_example_essay,
            key="example_essay_id",
            disabled=uploaded_file is not None,
        )

    essay_raw = st.text_area(
        "... or directly paste your text here:",
        height=280,
        key="essay_raw",
        help=(
            "Please use basic [markdown formatting](https://www.markdownguide.org/basic-syntax/), in particular:\n "
            " * '#', '##', '###' for headings\n"
            " * paragraphs are separated by an empty line\n"
        ),
    )

    if not essay_raw:
        # info with lightbulb icon
        st.info(
            "TIP: Instead of uploading a file, consider converting "
            "it with https://pandoc.org/try/ to markdown and paste "
            "the resulting text.",
            icon="💡",
        )
        placeholder = st.empty()
    else:
        # parse and preview essay
        essay_html = markdown.markdown(essay_raw)
        st.success(
            "Your essay is ready to be analysed. (Preview essay structure below.)"
        )
        placeholder = st.empty()
        st.write("------")
        with st.expander("Preview essay structure (click to expand)"):
            components.display_essay(essay_html)
            st.write(" ")

    with placeholder:
        if st.button(
            "Use this text and proceed with next step", disabled=not (essay_raw)
        ):
            aea.essaytext_md = essay_raw
            essay_html = markdown.markdown(essay_raw)
            aea.essaytext_html = essay_html
            aea.essay_content_items = backend.utils.parse_essay_content(essay_html)
            switch_page("Describe Main Question And Claims")


if __name__ == "__main__":
    main()
