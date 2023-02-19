# page 2: Sumarize your arguments

from typing import List

import streamlit as st
import uuid

from essay_mentor_app.backend.aea_datamodel import (
    ArgumentativeEssayAnalysis,
    SOObjectionGist,
)

st.session_state.update(st.session_state)

st.set_page_config(page_title="Summarize Objections", page_icon="X")
aea: ArgumentativeEssayAnalysis = st.session_state.aea


## status bar 

st.sidebar.header("Objections")
progress_bar = st.sidebar.progress(0)
status_text = st.sidebar.empty()




# main page


if not aea.main_claims:
    st.write(
        "In order to summarize objections, "
        "you need to detail your primary arguments first. "
        "Please go back to the previous page and do so."
    )
    st.stop()


if aea.objections:
    st.write("#### Your objections:")
    for reason in aea.reasons:
        st.write(f"*Primary argument*: {reason.text}")
        for objection in aea.objections:
            if objection.for_ref == reason.uid:
                st.write(f"* {objection.text}")

    st.stop()


st.write("Which objections to each primary argument do you discuss?")
st.write("If none, proceed with step 'Connect Arguments to Text'")

objections_txts = []
for e, reason in enumerate(aea.reasons):
    with st.expander(f"Primary argument {e+1}: {reason.text}"):
        objections_txts.append(
            st.text_area(
                f"Summarize objections to this argument here (separated by empty lines)",
                height=120,
                key=f"objections_txt_{reason.uid}"
            )
        )



# dummy siedbar info:
i=0.2
status_text.text("%i%% Complete" % i)
progress_bar.progress(i)


if any(objections_txt for objections_txt in objections_txts):

    if st.button("Proceed with these objections"):

        for e, reason in enumerate(aea.reasons):
            if objections_txts[e]:
                for raw_obj in objections_txts[e].splitlines():
                    if raw_obj.strip():
                        aea.objections.append(
                            SOObjectionGist(
                                uid=str(uuid.uuid4()),
                                text=raw_obj,
                                for_ref=reason.uid,
                            )
                        )


st.write("-------")

with st.expander("Debugging"):
    aea: ArgumentativeEssayAnalysis = st.session_state.aea
    for objection in aea.objections:
        st.json(objection.__dict__)