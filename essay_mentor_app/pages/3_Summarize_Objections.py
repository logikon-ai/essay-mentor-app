# page 2: Sumarize your arguments

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

if not aea.reasons:
    st.write(
        "In order to summarize objections, "
        "you need to detail your primary arguments first. "
        "Please go back to the previous page and do so."
    )
    st.stop()

if aea.objections:
    st.write("#### Your objections:")
    components.display_reasons(
        aea.objections,
        aea.reasons,
        parent_name="primary argument",
        reason_name="objection",
    )

    if st.button("Revise objections", disabled=st.session_state.has_been_submitted):
        backend.utils.clear_associated_keys(aea.rebuttals)
        aea.rebuttals = []
        backend.utils.clear_associated_keys(aea.objections)
        aea.objections = []
        st.experimental_rerun()
    if aea.rebuttals:
        st.caption(
            "(Revision will delete any data that has been entered on pages hereafter.)"
        )

    if aea.objections:
        st.stop()

if not st.session_state.has_been_submitted:
    st.info(
        "Which objections to each primary argument, or claim, do you discuss (if any)?",
        icon="❔",
    )

objections, skip = components.input_reasons(
    parent_list=aea.reasons + aea.main_claims,
    parent_name="primary argument/claim",
    reason_name="objection",
    expanded_per_default=False,
    with_skip_button=True,
    has_been_submitted=st.session_state.has_been_submitted,
)

if skip:
    switch_page("Connect Arguments To Text")

if objections:
    aea.objections = objections
    switch_page("Summarize Rebuttals")
