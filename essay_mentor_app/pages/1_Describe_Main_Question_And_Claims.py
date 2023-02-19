# page 1: Describe Main Question and Claims

from typing import List

import streamlit as st
import uuid

from essay_mentor_app.backend.aea_datamodel import (
    ArgumentativeEssayAnalysis,
    MainClaim,
    MainQuestion,
)

st.session_state.update(st.session_state)

st.set_page_config(page_title="Main Question And Claims", page_icon="?!")
aea: ArgumentativeEssayAnalysis = st.session_state.aea


## status bar 

st.sidebar.header("Main Question and Claims")
progress_bar = st.sidebar.progress(0)
status_text = st.sidebar.empty()




# main page


if not aea.essaytext_html:
    st.write(
        "You need to upload an essay first. "
        "Please go back to the previous page and do so."
    )
    st.stop()


if aea.main_questions or aea.main_claims:
    st.write("#### Your main question:")
    st.write(aea.main_questions[0].text)
    st.write("#### Your central claims:")
    for claim in aea.main_claims:
        st.write(f"* {claim.text}")

    st.stop()


st.write(
    "What is your essay all about? — Enter the main question you address below. "
    "Also, summarize the answers you discuss in the form of central claims. "
    "List only independent claims, i.e., answers you argue for without resort "
    "to each other."
)

main_question_txt = st.text_area(
    "Enter your main question here",
    height=30,
    key="main_question"
)

main_claims_txt = st.text_area(
    "Enter your central claim(s) here (separataed by empty lines)",
    height=200,
    key="central_claims"
)


# dummy siedbar info:
i=0.2
status_text.text("%i%% Complete" % i)
progress_bar.progress(i)


if main_question_txt and main_claims_txt:

    if st.button("Proceed with this question and claims"):

        main_question = MainQuestion(
            uid=str(uuid.uuid4()),
            text=main_question_txt,
        )

        main_claims: List[MainClaim] = []
        for claim in main_claims_txt.splitlines():
            if claim.strip():
                main_claims.append(
                    MainClaim(
                        uid=str(uuid.uuid4()),
                        text=claim,
                        question_refs=[main_question.uid],
                    )
                )
                main_question.claim_refs.append(main_claims[-1].uid)

        aea.main_questions = [main_question]
        aea.main_claims = main_claims



st.write("-------")

with st.expander("Debugging"):
    aea: ArgumentativeEssayAnalysis = st.session_state.aea
    if aea.main_questions:
        st.json(aea.main_questions[0].__dict__)
    for claim in aea.main_claims:
        st.json(claim.__dict__)