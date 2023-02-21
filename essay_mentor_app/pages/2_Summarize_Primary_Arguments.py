# page 2: Sumarize your arguments

from typing import List

import copy
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

st.set_page_config(page_title="Summarize Primary Arguments", page_icon="X")
aea: ArgumentativeEssayAnalysis = st.session_state.aea


## status bar 

st.sidebar.header("Primary Arguments")
progress_bar = st.sidebar.progress(0)
status_text = st.sidebar.empty()




# main page

# dummy update sidebar info:
i=0.2
status_text.text("%i%% Complete" % i)
progress_bar.progress(i)

if not aea.main_claims:
    st.write(
        "You need to detail your central claims first. "
        "Please go back to the previous page and do so."
    )
    st.stop()

if aea.reasons:
    st.write("#### Your primary arguments:")
    display_reasons(aea.reasons, aea.main_claims, parent_name="claim")

    if st.button("Revise primary arguments"):
        clear_associated_keys(aea.objections)
        aea.objections = []
        clear_associated_keys(aea.rebuttals)
        aea.rebuttals = []
        clear_associated_keys(aea.reasons)
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

reasons, _ = input_reasons(
    parent_list=aea.main_claims,
    parent_name="claim",
    reason_name="primary argument",
    expanded_per_default=True,
)

if reasons:
    aea.reasons = reasons
    switch_page("Summarize Objections")


