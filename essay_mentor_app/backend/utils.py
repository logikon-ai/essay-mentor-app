# utils.py

from typing import List

from bs4 import BeautifulSoup
import streamlit as st
from streamlit_extras.switch_page_button import switch_page

from essay_mentor_app.backend.aea_datamodel import (
    ArgumentativeEssayAnalysis,
    EssayContentItem,
    BaseContentItem,
    Reason,
)

import logikon_client
from logikon_client.rest import ApiException


def page_init(is_startpage=False):
    if not is_startpage:
        st.session_state.update(st.session_state)
    st.set_page_config(
        page_title="Tessy - Essay Tutor",
        page_icon="👩‍🏫",
    )
    if not "aea" in st.session_state and not is_startpage:
        switch_page("Start")


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


def get_aea_evaluation(aea: ArgumentativeEssayAnalysis) -> str:

    #cast aea as an ArgAnnotation
    nodelist = []
    edgelist = []
    for claim in aea.main_claims:
        nodelist.append(
            logikon_client.ArgMapNode(
                id=claim.uid,
                text=claim.text,
                label=claim.label,
            )
        )
    arguments = aea.reasons if aea.reasons else []
    if aea.objections:
        arguments += aea.objections
    if aea.rebuttals:
        arguments += aea.rebuttals
    for argument in arguments:
        nodelist.append(
            logikon_client.ArgMapNode(
                id=argument.uid,
                text=argument.text,
                label=argument.label,
                annotation_references=argument.essay_text_refs
            )
        )
        edgelist.append(
            logikon_client.ArgMapEdgelist(
                source=argument.uid,
                target=argument.parent_uid,
                valence="pro" if argument in aea.reasons else "con",
            )
        )

    argmap = logikon_client.ArgMap(
        nodelist = nodelist,
        edgelist = edgelist,
    )

    text_content_items = []
    for essay_element in aea.essay_content_items:
        text_content_items.append(
            logikon_client.TextContentItem(
                id = essay_element.uid,
                text = essay_element.text,
                name = essay_element.label,
            )
        )
    body = logikon_client.ArgAnnotation(
        argmap = argmap,
        text_content_items = text_content_items,
    )
    precision = 'medium' 

    # Configure API key authorization: api_key
    configuration = logikon_client.Configuration()
    configuration.host = st.secrets["logikon_server"]["url"]
    configuration.api_key['X-Auth'] = st.secrets["logikon_server"]["token"]

    # ApiInstance
    api_instance = logikon_client.MetricsApi(logikon_client.ApiClient(configuration))

    try:
        # Assesses the plausibility of an argumentative text annotation applying diverse metrics
        api_response = api_instance.evaluate_arg_annotation(body=body, precision=precision)
    except ApiException as e:
        st.error("Exception when calling MetricsApi->evaluate_arg_annotation: %s\n" % e)

    return api_response