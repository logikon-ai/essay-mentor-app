# page 2: Sumarize your arguments

from typing import List

import streamlit as st
from streamlit_extras.switch_page_button import switch_page
import uuid

from essay_mentor_app.backend.aea_datamodel import (
    ArgumentativeEssayAnalysis,
    Reason,
)

from essay_mentor_app.backend.components import (
    display_reasons,
    input_reasons,
    clear_associated_keys,
)

st.session_state.update(st.session_state)

st.set_page_config(page_title="Summarize Objections", page_icon="X")
aea: ArgumentativeEssayAnalysis = st.session_state.aea


## status bar 

#st.sidebar.header("Objections")
#progress_bar = st.sidebar.progress(0)
#status_text = st.sidebar.empty()




# main page


if not aea.reasons:
    st.write(
        "In order to summarize objections, "
        "you need to detail your primary arguments first. "
        "Please go back to the previous page and do so."
    )
    st.stop()


if aea.objections:
    st.write("#### Your objections:")
    display_reasons(aea.objections, aea.reasons, parent_name="primary argument", reason_name="objection")

    if st.button("Revise objections"):
        clear_associated_keys(aea.rebuttals)
        aea.rebuttals = []
        clear_associated_keys(aea.objections)
        aea.objections = []
        st.experimental_rerun()
    if aea.rebuttals:
        st.caption("(Revision will delete any data that has been entered on pages hereafter.)")

    if aea.objections:
        st.stop()

st.info(
    "Which objections to each primary argument do you discuss (if any)?",
    icon="❔"
)

objections, skip = input_reasons(
    parent_list=aea.reasons,
    parent_name="primary argument",
    reason_name="objection",
    expanded_per_default=False,
    with_skip_button=True,
)

if skip:
    switch_page("Connect Arguments To Text")


if objections:
    aea.objections = objections
    switch_page("Summarize Rebuttals")

