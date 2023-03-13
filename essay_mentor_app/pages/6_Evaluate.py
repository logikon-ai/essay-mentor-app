# page 6

import streamlit as st
from streamlit_extras.switch_page_button import switch_page

from essay_mentor_app.backend.aea_datamodel import ArgumentativeEssayAnalysis
import essay_mentor_app.backend.components as components
import backend.utils


# init

backend.utils.page_init()
aea:ArgumentativeEssayAnalysis = st.session_state.aea


# main

if not aea.reasons or not any(r.essay_text_refs for r in aea.reasons+aea.objections+aea.rebuttals):
    st.write(
        "In order to evaluate the essay, "
        "you need to detail your primary arguments "
        "(and possibly further objections and rebuttals) "
        "and connect them to your essay text first. "
        "Please go back to the previous pages and do so."
    )
    st.stop()


# info with lightbulb icon
if not st.session_state.has_been_submitted:
    st.info(
        "Review the summary of your analysis and annotation before submitting it.",
        icon="💡"
    )

st.markdown("### Reason hierarchy")
st.caption("Arguments, objections, rebuttals as summarized before:")
components.display_reasons_hierarchy(
    claims=aea.main_claims,
    reasons=aea.reasons,
    objections=aea.objections,
    rebuttals=aea.rebuttals,
)

st.markdown("### Essay Annotation")


components.display_essay_annotation_metrics(
    aea.essay_content_items,
    reasons=aea.reasons,
    objections=aea.objections,
    rebuttals=aea.rebuttals,
)
st.caption("Mapping of paragraphs in the essay (left column) to reasons (middle and right column):")
components.display_essay_annotation_figure(
    aea.essay_content_items,
    reasons=aea.reasons,
    objections=aea.objections,
    rebuttals=aea.rebuttals,
)


def on_submit():
    st.session_state["has_been_submitted"] = True
submit = st.button(
    "Submit for evaluation",
    disabled=st.session_state.has_been_submitted,
    on_click=on_submit,
)

if st.session_state.has_been_submitted:

    if not "evaluation_result" in st.session_state:
        with st.spinner("Evaluating your essay ..."):
            import time
            time.sleep(2)
            st.session_state["evaluation_result"] = {"some": "result"}

    st.markdown("## Evaluation")
    st.caption("😩 erroneous, 😟 implausible, 😐 arbitrary, 😊 plausible, 😄 compelling")
    st.markdown("### Overall score")
    st.markdown(
        components.eval_scores_table({
            "Argumentative analysis (reason hierarchy)": 2,
            "Linkage of arguments to text (essay annotation)": 3,
        }),
        unsafe_allow_html=True
    )
    st.markdown("### Individual scores per argument")
    components.dummy_show_detailed_scores(aea)
