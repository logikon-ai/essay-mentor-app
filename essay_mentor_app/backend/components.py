# passive and interactive gui components 

from typing import List, Tuple

from bs4 import BeautifulSoup
import markdownify
import streamlit as st
from streamlit_extras.switch_page_button import switch_page
import uuid

from essay_mentor_app.backend.aea_datamodel import (
    EssayContentItem,
    BaseContentItem,
    Reason,
)

def clear_associated_keys(content_elements: List[BaseContentItem]):
    for element in content_elements:
        st.session_state.pop(f"reasons_txt_{element.uid}", None)

def parse_essay_content(essay_html) -> List[EssayContentItem]:
    soup = BeautifulSoup(essay_html, 'html.parser')
    content_items = []
    for element in soup.find_all(['h1','h2','h3','h4','p','ul','ol']):
        html=str(element)
        level = 0
        if element.name in ['h1','h2','h3','h4']:
            level = ['h1','h2','h3','h4'].index(element.name) + 1
        content_items.append(
            EssayContentItem(
                name=element.name,
                text=element.text,
                html=html,
                heading_level=level,
            )
        )
    return content_items


def display_essay(essay_html):
    essay_content = parse_essay_content(essay_html)
    for element in essay_content:
        if element.name in ['h1','h2','h3','h4']:
            st.write(f"{'#'*(element.heading_level+3)} {element.text}")
        else:
            icon = "¶" if element.name=='p' else "⋮"
            summary = f"{icon}  {element.text[:10]}..."
            st.write(
                f"<details><summary>{summary}</summary>{element.text}</details>",
                unsafe_allow_html=True
            )
            # Debugging:
            #md = markdownify.markdownify(element.html)
            #st.code(md)

def display_reasons(
    reasons: List[Reason],
    parent_list: List[BaseContentItem],
    parent_name: str = "parent",
    next_page_label: str = None,
):
    for parent in parent_list:
        st.write(f"*{parent_name}*: {parent.text}")
        list_items = [
            f"* {reason.text}"
            for reason in reasons
            if reason.parent_uid == parent.uid
        ]
        st.write("\n".join(list_items))

def input_reasons(
    parent_list: List[BaseContentItem],
    parent_name: str = "parent",
    reason_name: str = "argument",
    expanded = True,
    with_skip_button = False,
) -> Tuple[List[Reason],bool]:
    
    reasons_text_areas = []
    for e, parent in enumerate(parent_list):
        #initial_text = "\n\n".join([
        #    ir.text for ir in initial_reasons
        #    if ir.parent_uid==parent.uid
        #])
        with st.expander(f"{parent_name} {e+1}: {parent.text}", expanded=expanded):
            reasons_text_areas.append(
                st.text_area(
                    f"Summarize {reason_name}s for this {parent_name} (separated by empty lines)",
                    #value=initial_text,
                    height=120,
                    key=f"reasons_txt_{parent.uid}",
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

    if with_skip_button:
        placeholder = st.empty()
        button_skip = st.button("Skip this input step.")
    else:
        placeholder = st.empty()
        button_skip = False

    with placeholder:
        button_proceed = st.button(
            str(f"Proceed with these {reason_name}s"),
            disabled=not any(reasons_txt for reasons_txt in reasons_text_areas)
        )

    if button_proceed:

        for e, parent in enumerate(parent_list):
            if reasons_text_areas[e]:
                for raw_reason in reasons_text_areas[e].splitlines():
                    if raw_reason.strip():
                        reasons.append(
                            Reason(
                                text=raw_reason,
                                parent_uid=parent.uid,
                            )
                        )

    return reasons, button_skip
