# page 4: Summarize your rebuttals

import streamlit as st
from streamlit_extras.switch_page_button import switch_page

from backend.aea_datamodel import ArgumentativeEssayAnalysis
import backend.components as components
import backend.utils


# init

backend.utils.page_init()
aea: ArgumentativeEssayAnalysis = st.session_state.aea

# main page

components.display_submit_notice(st.session_state.has_been_submitted)

if not aea.objections:
    st.write(
        "In order to summarize rebuttals, "
        "you need to detail first the objections you discuss. "
        "Please go back to the previous page to do so."
    )
    st.stop()

if aea.rebuttals:
    st.write("#### Your rebuttals:")
    components.display_reasons(
        aea.rebuttals, aea.objections, parent_name="objection", reason_name="rebuttal"
    )

    if st.button("Revise objections", disabled=st.session_state.has_been_submitted):
        backend.utils.clear_associated_keys(aea.rebuttals)
        aea.rebuttals = []
        st.experimental_rerun()
    st.caption(
        "(Revision will delete any data that has been entered on pages hereafter.)"
    )

    if aea.rebuttals:
        st.stop()

if not st.session_state.has_been_submitted:
    st.info("Which rebuttals to each objection do you present (if any)?", icon="❔")

rebuttals, skip = components.input_reasons(
    parent_list=aea.objections,
    parent_name="objection",
    reason_name="rebuttal",
    expanded_per_default=False,
    with_skip_button=True,
    has_been_submitted=st.session_state.has_been_submitted,
)

if skip:
    switch_page("Connect Arguments To Text")

if rebuttals:
    aea.rebuttals = rebuttals
    switch_page("Connect Arguments To Text")
