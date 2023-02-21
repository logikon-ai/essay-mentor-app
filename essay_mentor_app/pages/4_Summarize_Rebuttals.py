# page 2: Sumarize your arguments

from typing import List

import streamlit as st
from streamlit_extras.switch_page_button import switch_page

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

st.set_page_config(page_title="Summarize Rebuttals", page_icon="X")
aea: ArgumentativeEssayAnalysis = st.session_state.aea


## status bar 

#st.sidebar.header("Rebuttals")
#progress_bar = st.sidebar.progress(0)
#status_text = st.sidebar.empty()





if not aea.objections:
    st.write(
        "In order to summarize rebuttals, "
        "you need to detail first the objections you discuss. "
        "Please go back to the previous page to do so."
    )
    st.stop()


if aea.rebuttals:
    st.write("#### Your rebuttals:")
    display_reasons(aea.rebuttals, aea.objections, parent_name="objection", reason_name="rebuttal")

    if st.button("Revise objections"):
        clear_associated_keys(aea.rebuttals)
        aea.rebuttals = []
        st.experimental_rerun()
    st.caption("(Revision will delete any data that has been entered on pages hereafter.)")

    if aea.rebuttals:
        st.stop()

st.info(
    "Which rebuttals to each objection do you present (if any)?",
    icon="❔"
)

rebuttals, skip = input_reasons(
    parent_list=aea.objections,
    parent_name="objection",
    reason_name="rebuttal",
    expanded_per_default=False,
    with_skip_button=True,
)

if skip:
    switch_page("Connect Arguments To Text")


if rebuttals:
    aea.rebuttals = rebuttals
    switch_page("Connect Arguments To Text")




