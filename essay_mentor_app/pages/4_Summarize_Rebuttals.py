# page 2: Sumarize your arguments

from typing import List

import streamlit as st
import uuid

from essay_mentor_app.backend.aea_datamodel import (
    ArgumentativeEssayAnalysis,
    TORebuttalGist,
)

st.session_state.update(st.session_state)

st.set_page_config(page_title="Summarize Rebuttals", page_icon="X")
aea: ArgumentativeEssayAnalysis = st.session_state.aea


## status bar 

st.sidebar.header("Rebuttals")
progress_bar = st.sidebar.progress(0)
status_text = st.sidebar.empty()





if not aea.main_claims:
    st.write(
        "In order to summarize rebuttals, "
        "you need to detail the objections you discuss first. "
        "Please go back to the previous page to do so."
    )
    st.stop()


if aea.rebuttals:
    st.write("#### Your rebuttals:")
    for objection in aea.objections:
        st.write(f"*Objection*: {objection.text}")
        for rebuttal in aea.rebuttals:
            if rebuttal.soo_ref == objection.uid:
                st.write(f"* {rebuttal.text}")

    st.stop()


st.write("Which rebuttals to each objections do you present?")
st.write("If none, proceed with step 'Connect Arguments to Text'")

rebuttals_txts = []
for e, objection in enumerate(aea.objections):
    with st.expander(f"Objection {e+1}: {objection.text}"):
        rebuttals_txts.append(
            st.text_area(
                f"Summarize rebuttals to this objection here (separated by empty lines)",
                height=120,
                key=f"rebuttals_txts_{objection.uid}"
            )
        )



# dummy siedbar info:
i=0.2
status_text.text("%i%% Complete" % i)
progress_bar.progress(i)


if any(rebuttals_txt for rebuttals_txt in rebuttals_txts):

    if st.button("Proceed with these rebuttals"):

        for e, objection in enumerate(aea.objections):
            if rebuttals_txts[e]:
                for raw_rebuttal in rebuttals_txts[e].splitlines():
                    if raw_rebuttal.strip():
                        aea.rebuttals.append(
                            TORebuttalGist(
                                uid=str(uuid.uuid4()),
                                text=raw_rebuttal,
                                soo_ref=objection.uid,
                            )
                        )


st.write("-------")

with st.expander("Debugging"):
    aea: ArgumentativeEssayAnalysis = st.session_state.aea
    for rebuttal in aea.rebuttals:
        st.json(rebuttal.__dict__)