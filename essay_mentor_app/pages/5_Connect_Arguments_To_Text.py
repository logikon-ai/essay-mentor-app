# page 3

import streamlit as st
from streamlit_extras.switch_page_button import switch_page
st.session_state.update(st.session_state)

from essay_mentor_app.backend.aea_datamodel import (
    ArgumentativeEssayAnalysis,
)
from essay_mentor_app.backend.components import (
    display_essay,
    display_reasons_hierarchy,
)

st.session_state.update(st.session_state)

st.set_page_config(
    page_title="Tessy - Essay Tutor",
    page_icon="👩‍🏫",
)
if not "aea" in st.session_state:
    switch_page("Start")
aea:ArgumentativeEssayAnalysis = st.session_state.aea



if not aea.reasons:
    st.write(
        "In order to annotate the essay, "
        "you need to detail your primary arguments "
        "(and possibly further objections and rebuttals) first. "
        "Please go back to the previous pages and do so."
    )
    st.stop()

st.info(
    "Where, in your essay, do you present the arguments summarized so far?",
    icon="❔"
)

with st.expander(
    "Reason hierarchy (arguments, objections, rebuttals) as summarized before",
    expanded=True,
):
    display_reasons_hierarchy(
        claims=aea.main_claims,
        reasons=aea.reasons,
        objections=aea.objections,
        rebuttals=aea.rebuttals,
    )

st.write("------")
st.write("Select reasons that are discussed in each corresponding paragraph:")

reason_assignments = display_essay(
    aea.essay_content_items,
    reasons=aea.reasons,
    objections=aea.objections,
    rebuttals=aea.rebuttals,
)

if reason_assignments:
    if st.button("Use these annotations and proceed with preview", disabled=not(any(reason_assignments.values()))):
        # clear all previous assigments
        for reason in aea.reasons+aea.objections+aea.rebuttals:
            reason.essay_text_refs = []
        # assign new labels
        for essay_text_uid, uids in reason_assignments.items():
            for reason_uid in uids:
                reason = aea.get_reason_by_uid(reason_uid)
                reason.essay_text_refs.append(essay_text_uid)
        switch_page("Evaluate")

# Debugging:
#st.json(reason_assignments)



