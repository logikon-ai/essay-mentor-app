# passive and interactive gui components 

from typing import List, Tuple, Union, Optional, Dict

from bs4 import BeautifulSoup
import plotly.graph_objects as go
import pandas as pd
import streamlit as st
from streamlit_extras.switch_page_button import switch_page
import uuid

from essay_mentor_app.backend.aea_datamodel import (
    ArgumentativeEssayAnalysis,
    EssayContentItem,
    BaseContentItem,
    MapContentItem,
    MainClaim,
    Reason,
)

LABELS = {
    "primary argument": "PrA",
    "objection": "Obj",
    "rebuttal": "Rbt",
}

def clear_associated_keys(content_elements: List[BaseContentItem]):
    for element in content_elements:
        st.session_state.pop(f"reasons_txt_{element.uid}", None)
        if isinstance(element, Reason):
            # remove element label from all multi select widget lists
            for essay_element in st.session_state.aea.essay_content_items:
                multi_select_list = st.session_state.get(f"multiselect_assreas_{essay_element.uid}", [])
                if element.label in multi_select_list:
                    multi_select_list.remove(element.label)
        if isinstance(element, EssayContentItem):
            st.session_state.pop(f"multiselect_assreas_{element.uid}", None)



def parse_essay_content(essay_html) -> List[EssayContentItem]:
    soup = BeautifulSoup(essay_html, 'html.parser')
    content_items = []
    counter = 0
    for element in soup.find_all(['h1','h2','h3','h4','p','ul','ol']):
        html=str(element)
        level = 0
        if element.name in ['h1','h2','h3','h4']:
            level = ['h1','h2','h3','h4'].index(element.name) + 1
        else:
            counter += 1
        content_items.append(
            EssayContentItem(
                name=element.name,
                text=element.text,
                html=html,
                heading_level=level,
                label=f"{counter:03d}" if level==0 else "",
            )
        )
    return content_items


def display_essay(
    essay: Union[str, List[EssayContentItem]],
    reasons: List[Reason] = None,
    objections: List[Reason] = None,
    rebuttals: List[Reason] = None,
) -> Optional[Dict[str, List[str]]]:
    if isinstance(essay, str):
        essay_content = parse_essay_content(essay)
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
                )
                st.write("\n")

            icon = "¶" if element.name=='p' else "⋮"
            summary = f"{icon} {element.label}  {element.text[:32]}..."
            paragraph_placeholder.write(
                f"<details><summary>{summary}</summary>{element.text}</details>",
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
        disabled=not any(reasons_txt for reasons_txt in reasons_text_areas)
    )
    button_skip = st.button("Skip this input step.") if with_skip_button else False


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
        values=df.rtype, label="Type", 
        categoryorder="array",
        categoryarray=rtype_order,
    )

    # Create parcats trace
    colormap = dict([("PrimArg", 'green'), ("Object.", 'red'), ("Rebut.", "blueviolet"), ("None", "gray")])
    color = df.rtype.apply(lambda rtype: colormap.get(rtype))

    fig_data = [go.Parcats(dimensions=[paragraph_dim, reason_dim, rtype_dim],
        line={'color': color},
        hoveron='dimension', hoverinfo='count',
        arrangement='freeform'
        )
    ]

    st.plotly_chart(fig_data, use_container_width=True)

    # Debug:
    #st.experimental_show(essay_content_uids)
    #st.table(df)

