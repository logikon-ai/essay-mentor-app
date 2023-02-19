# page 2: Sumarize your arguments

from typing import List

import streamlit as st
import uuid

from essay_mentor_app.backend.aea_datamodel import (
    ArgumentativeEssayAnalysis,
    FOReasonGist,
)

st.session_state.update(st.session_state)

st.set_page_config(page_title="Summarize Primary Arguments", page_icon="X")
aea: ArgumentativeEssayAnalysis = st.session_state.aea


## status bar 

st.sidebar.header("Primary Arguments")
progress_bar = st.sidebar.progress(0)
status_text = st.sidebar.empty()




# main page


if not aea.main_claims:
    st.write(
        "You need to detail your central claims first. "
        "Please go back to the previous page and do so."
    )
    st.stop()


if aea.reasons:
    st.write("#### Your primary arguments:")
    for claim in aea.main_claims:
        st.write(f"*claim*: {claim.text}")
        for reason in aea.reasons:
            if reason.claim_ref == claim.uid:
                st.write(f"* {reason.text}")

    st.stop()


st.write(
    "What are your arguments for each central claim?"
)

reasons_txts = []
for e, claim in enumerate(aea.main_claims):
    with st.expander(f"Claim {e+1}: {claim.text}", expanded=True):
        reasons_txts.append(
            st.text_area(
                f"Summarize arguments for this claim here (separated by empty lines)",
                height=120,
                key=f"reasons_txt_{claim.uid}"
            )
        )



# dummy siedbar info:
i=0.2
status_text.text("%i%% Complete" % i)
progress_bar.progress(i)


if any(reasons_txt for reasons_txt in reasons_txts):

    if st.button("Proceed with these primary arguments"):

        for e, claim in enumerate(aea.main_claims):
            if reasons_txts[e]:
                for raw_reason in reasons_txts[e].splitlines():
                    if raw_reason.strip():
                        aea.reasons.append(
                            FOReasonGist(
                                uid=str(uuid.uuid4()),
                                text=raw_reason,
                                claim_ref=claim.uid,
                            )
                        )


st.write("-------")

with st.expander("Debugging"):
    aea: ArgumentativeEssayAnalysis = st.session_state.aea
    for reason in aea.reasons:
        st.json(reason.__dict__)