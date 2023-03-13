# passive and interactive gui components 

from typing import List, Tuple, Union, Optional, Dict

from bs4 import BeautifulSoup
import plotly.graph_objects as go
import numpy as np
import pandas as pd
import random
import streamlit as st
from streamlit_extras.switch_page_button import switch_page
import uuid

from essay_mentor_app.backend.aea_datamodel import (
    EssayContentItem,
    BaseContentItem,
    MapContentItem,
    MainClaim,
    Reason,
)
import backend.utils

LABELS = {
    "primary argument": "PrA",
    "objection": "Obj",
    "rebuttal": "Rbt",
}

def display_submit_notice(has_been_submitted: bool = False):
    if has_been_submitted:
        st.info(
            "Your essay has been submitted and evaluated. Results are shown on "
            "page 'Evaluate'. To start over, reload this page.",
            icon="💡"
        )

def display_essay(
    essay: Union[str, List[EssayContentItem]],
    reasons: List[Reason] = None,
    objections: List[Reason] = None,
    rebuttals: List[Reason] = None,
    has_been_submitted: bool = False,
) -> Optional[Dict[str, List[str]]]:
    if isinstance(essay, str):
        essay_content = backend.utils.parse_essay_content(essay)
    else:
        essay_content = essay

    reason_labels = {}
    if any([reasons, objections, rebuttals]):
        for rlist in [reasons, objections, rebuttals]:
            if rlist is not None:
                reason_labels.update({
                    r.label: r.uid for r in rlist
                })

    label_assignments = {}
    for element in essay_content:
        if element.name in ['h1','h2','h3','h4']:
            st.write(f"{'#'*(element.heading_level+3)} {element.text}")
        else:
            paragraph_placeholder = st.empty()
            if reason_labels:                
                label_assignments[element.uid] = st.multiselect(
                    "Reasons discussed in paragraph quoted above (if any):",
                    options=list(reason_labels.keys()),
                    key=f"multiselect_assreas_{element.uid}",
                    disabled=has_been_submitted,
                )
                st.write("\n")

            icon = "¶" if element.name=='p' else "⋮"
            summary = f"{icon} {element.label}  {element.text[:32]}..."
            paragraph_placeholder.write(
                f"<p><details><summary>{summary}</summary>{element.text}</details></p>",
                unsafe_allow_html=True
            )

    # use uids in label assignments
    for k, v in label_assignments.items():
        label_assignments[k] = [reason_labels[label] for label in v]

    return label_assignments if reason_labels else None



def display_reasons(
    reasons: List[Reason],
    parent_list: List[BaseContentItem],
    reason_name: str = "argument",
    parent_name: str = "parent",
):
    reason_name = reason_name[:1].upper()+reason_name[1:]
    for parent in parent_list:
        list_items = [
            f"* **\[{reason.label}\]**: {reason.text}"
            for reason in reasons
            if reason.parent_uid == parent.uid
        ]
        if list_items:
            st.write(f"{reason_name}s that address {parent_name} \[{parent.label}\] ({parent.text}):")
            st.write("\n".join(list_items))


def display_reasons_hierarchy(
    claims: List[MainClaim],
    reasons: List[Reason],
    objections: List[Reason],
    rebuttals: List[Reason],
):
    markdown_lines = [] 
    for claim in claims:
        markdown_lines.append(f"* **\[{claim.label}\]**: {claim.text}")
        for reason in reasons:
            if reason.parent_uid == claim.uid:
                markdown_lines.append(f"  * **\[{reason.label}\]**: {reason.text}")
                for objection in objections:
                    if objection.parent_uid == reason.uid:
                        markdown_lines.append(f"    * **\[{objection.label}\]**: {objection.text}")
                        for rebuttal in rebuttals:
                            if rebuttal.parent_uid == objection.uid:
                                markdown_lines.append(f"      * **\[{rebuttal.label}\]**: {rebuttal.text}")
    st.markdown("\n".join(markdown_lines))


def input_reasons(
    parent_list: List[MapContentItem],
    parent_name: str = "parent",
    reason_name: str = "argument",
    expanded_per_default = True,
    with_skip_button = False,
    has_been_submitted = False,
) -> Tuple[List[Reason],bool]:
    
    reasons_text_areas = []
    for e, parent in enumerate(parent_list):
        #initial_text = "\n\n".join([
        #    ir.text for ir in initial_reasons
        #    if ir.parent_uid==parent.uid
        #])
        key=f"reasons_txt_{parent.uid}"
        expanded = expanded_per_default or bool(st.session_state.get(key, None))
        with st.expander(f"\[{parent.label}\]: {parent.text}", expanded=expanded):
            reasons_text_areas.append(
                st.text_area(
                    f"Summarize {reason_name}s for this {parent_name} (separated by empty lines)",
                    #value=initial_text,
                    height=120,
                    key=key,
                    disabled=has_been_submitted,
                )
            )

    n_reasons = 0
    for reasons_txt in reasons_text_areas:
        if reasons_txt:
            n_reasons += len([
                r for r in reasons_txt.splitlines()
                if r.strip()
            ])

    if n_reasons==0:
        st.warning(str(f"No {reason_name}s provided."))
    else:
        st.success(str(f"{n_reasons} {reason_name}s provided."))

    reasons: List[Reason] = []

    button_proceed = st.button(
        str(f"Proceed with these {reason_name}s"),
        disabled=not any(reasons_txt for reasons_txt in reasons_text_areas) or has_been_submitted
    )
    button_skip = st.button("Skip this input step.", disabled=has_been_submitted) if with_skip_button else False


    if button_proceed:

        count = 0
        for e, parent in enumerate(parent_list):
            if reasons_text_areas[e]:
                for raw_reason in reasons_text_areas[e].splitlines():
                    if raw_reason.strip():
                        count += 1
                        reasons.append(
                            Reason(
                                text=raw_reason,
                                parent_uid=parent.uid,
                                label=f"{LABELS.get(reason_name,'ARG')}{count}",
                            )
                        )

    return reasons, button_skip


def display_essay_annotation_metrics(
    essay: List[EssayContentItem],
    reasons: List[Reason] = None,
    objections: List[Reason] = None,
    rebuttals: List[Reason] = None,
):
    # list of all arguments
    arguments: List[Reason] = reasons or []
    if objections:
        arguments += objections
    if rebuttals:
        arguments += rebuttals

    # list of all paragraph uids
    essay_content_items = [
        element for element in essay
        if element.name not in ['h1','h2','h3','h4']
    ]
    essay_content_uids = [element.uid for element in essay_content_items]

    # metrics
    essay_content_covered = [
        uid for uid in essay_content_uids
        if any([arg for arg in arguments if uid in arg.essay_text_refs])
    ]
    essay_content_covered_ratio = len(essay_content_covered)/len(essay_content_uids)

    arguments_assigned = [
        arg for arg in arguments
        if arg.essay_text_refs
    ]
    arguments_assigned_ratio = len(arguments_assigned)/len(arguments)

    average_paragraphs_per_argument = np.mean([
        len(arg.essay_text_refs) for arg in arguments_assigned
    ])

    col1, col2, col3 = st.columns(3)
    col1.metric("Essay content covered", f"{essay_content_covered_ratio*100:.0f} %")
    col2.metric("Arguments assigned", f"{arguments_assigned_ratio*100:.0f} %")
    col3.metric("Paragraphs per ass. argument", f"{average_paragraphs_per_argument:.2f}")


def display_essay_annotation_figure(
    essay: List[EssayContentItem],
    reasons: List[Reason] = None,
    objections: List[Reason] = None,
    rebuttals: List[Reason] = None,
):
    essay_content_items = [
        element for element in essay
        if element.name not in ['h1','h2','h3','h4']
    ]
    essay_content_uids = [element.uid for element in essay_content_items]

    data = []
    for reason in reasons:
        if reason.essay_text_refs:
            for ref in reason.essay_text_refs:
                if ref in essay_content_uids:
                    essay_item = next(x for x in essay_content_items if x.uid==ref)
                    data.append({
                        "reason": "[%s]" % reason.label,
                        "paragraph": essay_item.label,
                        "rtype": "PrimArg",
                    })
        else:
            data.append({
                "reason": "[%s]" % reason.label,
                "paragraph": "None",
                "rtype": "PrimArg",
            })
    for objection in objections:
        if objection.essay_text_refs:
            for ref in objection.essay_text_refs:
                if ref in essay_content_uids:
                    essay_item = next(x for x in essay_content_items if x.uid==ref)
                    data.append({
                        "reason": "[%s]" % objection.label,
                        "paragraph": essay_item.label,
                        "rtype": "Object.",
                    })
        else:
            data.append({
                "reason": "[%s]" % objection.label,
                "paragraph": "None",
                "rtype": "Object.",
            })
    for rebuttal in rebuttals:
        if rebuttal.essay_text_refs:
            for ref in rebuttal.essay_text_refs:
                if ref in essay_content_uids:
                    essay_item = next(x for x in essay_content_items if x.uid==ref)
                    data.append({
                        "reason": "[%s]" % rebuttal.label,
                        "paragraph": essay_item.label,
                        "rtype": "Rebut.",
                    })
        else:
            data.append({
                "reason": "[%s]" % rebuttal.label,
                "paragraph": "None",
                "rtype": "Rebut.",
            })
    for essay_item in essay_content_items:
        if not any(
            essay_item.uid in r.essay_text_refs 
            for r in reasons+objections+rebuttals
        ):
            data.append({
                "reason": "None",
                "paragraph": essay_item.label,
                "rtype": "None",
            })
                
    df = pd.DataFrame(data)
    

    # Create dimensions
    paragraph_dim = go.parcats.Dimension(
        values=df.paragraph,
        categoryorder='category ascending', label="Paragraph"
    )

    reason_dim = go.parcats.Dimension(
        values=df.reason, label="Reason",
    )

    rtype_order = ["PrimArg","Object.","Rebut.","None"]
    rtype_order = [t for t in rtype_order if t in df.rtype]
    rtype_dim = go.parcats.Dimension(
        values=df.rtype, label="Argument Type", 
        categoryorder="array",
        categoryarray=rtype_order,
    )

    # Create parcats trace
    colormap = dict([("PrimArg", 'green'), ("Object.", 'red'), ("Rebut.", "blueviolet"), ("None", "gray")])
    color = df.rtype.apply(lambda rtype: colormap.get(rtype))

    fig_data = [go.Parcats(dimensions=[paragraph_dim, reason_dim, rtype_dim],
        line={'color': color},
        hoveron='dimension', hoverinfo='count'#,
        #labelfont={'size': 12, 'family': 'Sans-Serif'},
        #tickfont={'size': 12, 'family': 'Sans-Serif'}#,
        #arrangement='freeform'
        )
    ]

    st.plotly_chart(
        fig_data,
        use_container_width=False
    )

    # Debug:
    #st.experimental_show(essay_content_uids)
    #st.table(df)


def eval_scores_table(data: Dict[str,int]) -> str:
    """Return a html table with the evaluation scores."""

    def emoji(score: int) -> str:
        if score == 0:
            return "😩"
        elif score == 1:
            return "😟"
        elif score == 2:
            return "😐"
        elif score == 3:
            return "😊"
        elif score == 4:
            return "😄"

    data_rows = ""
    for key, value in data.items():
        row = f"<tr><td>{key}:</td>"
        for i in range(5):
            if i == value:
                row += f"<td align=center><h4>{emoji(i)}</h4></td>"
            else:
                row += "<td></td>"
        row += "</tr>"
        data_rows += row

    table_header = (
        "<table>"
        "<tr>"
        "<td width=30%></td>"
        "<td align=center width=14%><i>erroneous</i></td>"
        "<td align=center width=14%><i>implausible</i></td>"
        "<td align=center width=14%><i>arbitrary</i></td>"
        "<td align=center width=14%><i>plausible</i></td>"
        "<td align=center width=14%><i>compelling</i></td>"
        "</tr>"
    )
    table_footer = "</table><br/>"
    
    return table_header + data_rows + table_footer


def dummy_show_detailed_scores(aea):
    # list of all arguments
    arguments: List[Reason] = aea.reasons or []
    if aea.objections:
        arguments += aea.objections
    if aea.rebuttals:
        arguments += aea.rebuttals

    for argument in arguments:
        st.write(f"##### [{argument.label}]: {argument.text}")
        st.write(f"Linked to paragraphs: ¶003, ¶005")
        dummy_scores = {
            f"Argumentative relation of [{argument.label}] to other arguments":random.randint(0,4),
            f"Link of [{argument.label}] to paragraphs in the essay":random.randint(0,4),
        }
        st.markdown(
            eval_scores_table(dummy_scores),
            unsafe_allow_html=True
        )
        explanation = st.expander("More details and explanation...", expanded=False)
        with explanation:
            summary = f"It is <b>very likely</b> that {argument.label} is related to further arguments differently than specified by the author (i.e., not as pro reason for [xxx]). Most plausible alternatives:"
            details = f"<ul><li>Pro reason for [Obj2] (23%)</li><li>Con reason against [Claim1] (12%)</li><li>Pro reason for [Rbt3] (11%)</li></ul>"
            st.markdown(
                f"<p>{summary}</p><p>{details}</p>",
                unsafe_allow_html=True
            )
            summary = f"It is <b>unlikely</b> that {argument.label} appears in the essay at different places than specified by the author. Most plausible alternatives:"
            details = f"<ul><li>Discussed in ¶002 (15%)</li><li>Not discussed in ¶003 (12%)</li><li>Discussed in ¶001 (4%)</li></ul>"
            st.markdown(
                f"<p>{summary}</p><p>{details}</p>",
                unsafe_allow_html=True
            )
