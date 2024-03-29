# page 6: Essay evaluation

import jinja2
import pdfkit
import streamlit as st

from backend.aea_datamodel import ArgumentativeEssayAnalysis
import backend.components as components
import backend.utils
import backend.templates

ANNOTATION_FIGURE_PATH = "essay_annotation_figure.svg"


# init

backend.utils.page_init()
aea: ArgumentativeEssayAnalysis = st.session_state.aea

# main

if not aea.reasons or not any(
    r.essay_text_refs for r in aea.reasons + aea.objections + aea.rebuttals
):
    st.write(
        "In order to evaluate the essay, "
        "you need to detail your primary arguments "
        "(and possibly further objections and rebuttals) "
        "and connect them to your essay text first. "
        "Please go back to the previous pages and do so."
    )
    st.stop()

# status info upfront
if not st.session_state.has_been_submitted:
    st.info(
        "Review the summary of your analysis and annotation before submitting it.",
        icon="💡",
    )

if st.session_state.has_been_submitted and not "evaluation_result" in st.session_state:
    # st.json(
    #     {
    #         "submitted argmap": aea.as_api_argmap(),
    #         "submitted text items": aea.as_api_textContentItems(),
    #     }
    # )
    with st.spinner("Evaluating your essay ..."):
        try:
            evaluation_result = backend.utils.get_aea_evaluation(aea)
        except Exception as e:
            st.error(
                "Error while evaluating your essay. Please try again later. (%s)"
                % e
            )
            st.stop()
        if (
            not evaluation_result.get("argmap_metrics")
            or not evaluation_result.get("annotation_metrics")
            or "error" in evaluation_result.get("argmap_metrics")
            or "error" in evaluation_result.get("annotation_metrics")
            or evaluation_result.get("argmap_metrics",{}).get("status", 200) != 200
            or evaluation_result.get("annotation_metrics",{}).get("status", 200) != 200
        ):
            st.error(
                "Error while evaluating your essay. Please try again later. (%s)"
                % evaluation_result
            )
            st.stop()
        st.session_state["evaluation_result"] = evaluation_result

if st.session_state.get("evaluation_result"):
    st.success(
        "Evaluation completed. Find the results below.",
        icon="✅",
    )


st.markdown("### Reason hierarchy")
st.caption("Arguments, objections, rebuttals as summarized before:")
argmap_svg = components.display_argument_map(
    claims=aea.main_claims,
    reasons=aea.reasons,
    objections=aea.objections,
    rebuttals=aea.rebuttals,
)
# st.write(argmap_svg) # debugging
with st.expander("Reason hierarchy as nested list"):
    components.display_reasons_hierarchy(
        claims=aea.main_claims,
        reasons=aea.reasons,
        objections=aea.objections,
        rebuttals=aea.rebuttals,
    )
    st.write("")

st.markdown("### Essay Annotation")

components.display_essay_annotation_metrics(
    aea.essay_content_items,
    reasons=aea.reasons,
    objections=aea.objections,
    rebuttals=aea.rebuttals,
)

st.caption(
    "Mapping of paragraphs in the essay (left column) to reasons (middle and right column):"
)
fig = components.display_essay_annotation_figure(
    aea.essay_content_items,
    reasons=aea.reasons,
    objections=aea.objections,
    rebuttals=aea.rebuttals,
)

if False:
    fig.write_image(ANNOTATION_FIGURE_PATH)  # save figure for report, uses kaleido
# st.image(ANNOTATION_FIGURE_PATH)  # debugging


def on_submit():
    st.session_state["has_been_submitted"] = True


submit = st.button(
    "Submit for evaluation",
    disabled=st.session_state.has_been_submitted,
    on_click=on_submit,
)

if st.session_state.get("evaluation_result"):

    st.markdown("## Evaluation")

    # st.json(st.session_state.evaluation_result)

    components.display_evaluation_results(st.session_state.evaluation_result, aea)

    if False:
        st.markdown("------")

        # read svg file
        with open(ANNOTATION_FIGURE_PATH, "r") as f:
            annotation_svg = f.read()
        report_data = {
            "argmap_svg": argmap_svg,
            "annotation_svg": annotation_svg,
            "reason_hierarchy": "JUST A TEST MAP",
        }
        # load jinja template from backend.templates.REPORT_TEMPLATE
        template = jinja2.Template(backend.templates.REPORT_TEMPLATE)
        report_html = template.render(**report_data)
        # st.markdown(report_html, unsafe_allow_html=True) # debugging

        report_pdf = pdfkit.from_string(report_html, False)
        st.download_button(
            "⬇️ Download Report (PDF)",
            data=report_pdf,
            file_name="report.pdf",
            mime="application/octet-stream",
        )
