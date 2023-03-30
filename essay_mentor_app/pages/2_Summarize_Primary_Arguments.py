# page 2: Sumarize your arguments

from typing import List

import streamlit as st
from streamlit_extras.switch_page_button import switch_page

from essay_mentor_app.backend.aea_datamodel import ArgumentativeEssayAnalysis
import essay_mentor_app.backend.components as components
import backend.utils


# init

backend.utils.page_init()
aea: ArgumentativeEssayAnalysis = st.session_state.aea


# main page

components.display_submit_notice(st.session_state.has_been_submitted)

if not aea.main_claims:
    st.write(
        "You need to detail your central claims first. "
        "Please go back to the previous page and do so."
    )
    st.stop()

if aea.reasons:
    st.write("#### Your primary arguments:")
    components.display_reasons(aea.reasons, aea.main_claims, parent_name="claim", reason_name="primary argument")

    if st.button("Revise primary arguments", disabled=st.session_state.has_been_submitted):
        backend.utils.clear_associated_keys(aea.objections)
        aea.objections = []
        backend.utils.clear_associated_keys(aea.rebuttals)
        aea.rebuttals = []
        backend.utils.clear_associated_keys(aea.reasons)
        aea.reasons = []
        st.experimental_rerun()
    if aea.objections:
        st.caption("(Revision will delete any data that has been entered on pages hereafter.)")

    if aea.reasons:
        st.stop()

st.info(
    "What are your arguments for each central claim?",
    icon="❔"
)

reasons, _ = components.input_reasons(
    parent_list=aea.main_claims,
    parent_name="claim",
    reason_name="primary argument",
    expanded_per_default=True,
    has_been_submitted=st.session_state.has_been_submitted,
    default_value="Animal farming contributes to climate heating.\n\n"
    "Animals have feelings and can suffer, especially when they are "
    "farmed and slaughtered.\n\n"
    "Animal farming creates a lot of joy and happiness: For farmers, "
    "children, and least but not least for the happy animals "
    "themselves." if st.session_state.DEBUG else ""
)

if reasons:
    aea.reasons = reasons
    switch_page("Summarize Objections")


