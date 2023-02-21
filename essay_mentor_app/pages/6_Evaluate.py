# page 6

import streamlit as st
st.session_state.update(st.session_state)

from essay_mentor_app.backend.aea_datamodel import (
    ArgumentativeEssayAnalysis,
)
from essay_mentor_app.backend.components import (
    display_reasons_hierarchy,
    display_essay_annotation_figure,
)

aea:ArgumentativeEssayAnalysis = st.session_state.aea



if not aea.reasons or not any(r.essay_text_refs for r in aea.reasons+aea.objections+aea.rebuttals):
    st.write(
        "In order to annotate the essay, "
        "you need to detail your primary arguments "
        "(and possibly further objections and rebuttals) "
        "and connect them to your essay text first. "
        "Please go back to the previous pages and do so."
    )
    st.stop()


# info with lightbulb icon
st.info(
    "Review the summary of your analysis and annotation before submitting it.",
    icon="💡"
)

st.markdown("### Reason hierarchy")
st.caption("Arguments, objections, rebuttals as summarized before.")
display_reasons_hierarchy(
    claims=aea.main_claims,
    reasons=aea.reasons,
    objections=aea.objections,
    rebuttals=aea.rebuttals,
)

st.markdown("### Annotation visualization")
st.caption("Mapping of paragraphs in the essay (left column) to reasons (middle and right column).")
display_essay_annotation_figure(
    aea.essay_content_items,
    reasons=aea.reasons,
    objections=aea.objections,
    rebuttals=aea.rebuttals,
)

