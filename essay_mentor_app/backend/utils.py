# utils.py

from typing import List, Tuple, Dict
import json
import requests

from bs4 import BeautifulSoup
import streamlit as st
from streamlit_extras.switch_page_button import switch_page

from essay_mentor_app.backend.aea_datamodel import (
    ArgumentativeEssayAnalysis,
    EssayContentItem,
    BaseContentItem,
    Reason,
)

_REQUEST_TIMEOUT = 480

def page_init(is_startpage=False):
    if not is_startpage:
        st.session_state.update(st.session_state)  # for multi-page state preservation
    if not st.session_state.get("logged_in") and not is_startpage:
        switch_page("Start")
    if 'sidebar_state' not in st.session_state:
        st.session_state.sidebar_state = 'collapsed'    
    page_title = "Tessy - Essay Tutor"
    if st.session_state.get("demo_mode"):
        page_title += " (🛣️)"
    st.set_page_config(
        page_title=page_title,
        page_icon="👩‍🏫",
        initial_sidebar_state=st.session_state.sidebar_state,
    )
    if not "aea" in st.session_state and not is_startpage:
        switch_page("Start")

def logged_in():
    """returns `True` if user is logged in via correct password and server is available"""

    def password_entered():
        """Checks whether a password entered by the user is correct."""
        if st.session_state["password"] == st.secrets["app_password"]:
            st.session_state["password_correct"] = True
            del st.session_state["password"]  # don't store password
        else:
            st.session_state["password_correct"] = False

    if st.session_state.get("logged_in"):
        return True

    st.text_input(
        "Please enter the password to access the app:",
        type="password",
        key="password",
        #on_change=password_entered,
    )
    st.checkbox("Demo mode 🛣️", key="demo_mode")
    st.button("Login", on_click=password_entered)

    if not "password_correct" in st.session_state:
        return False

    if not st.session_state.get("password_correct"):
        st.error("😕 Password incorrect")   
        return False
    
    try:
        page = requests.get(st.secrets["logikon_server"]["url"]+"/ui")
        status = page.status_code
    except requests.exceptions.ConnectionError:
        status = 500

    if status != 200:
        st.error("Logikon server not reachable. Please try again later or contact Logikon staff.", icon="🚨")
        return False

    st.session_state["logged_in"] = True
    st.session_state["sidebar_state"] = 'expanded'
    st.experimental_rerun()



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


def get_aea_evaluation(aea: ArgumentativeEssayAnalysis) -> Dict[str,Dict]:
    """Get evaluation of ArgumentativeEssayAnalysis from logikon server
    Args:
        aea (ArgumentativeEssayAnalysis): ArgumentativeEssayAnalysis object
    Returns:
        Tuple[Dict,Dict]: MetricsCollection for argument map, MetricsCollection for text annotation
    """

    api_token = st.secrets["logikon_server"]["token"]
    server_url = st.secrets["logikon_server"]["url"]
    headers = {
        "accept": "application/json",
        "X-Auth": api_token,
        "Content-Type": "application/json"
    }
    params = {
        "precision": "medium",
    }

    def query(payload, api_path):
        api_url = f"{server_url}/{api_path}"
        data = json.dumps(payload)
        response = requests.request(
            "POST",
            api_url,
            headers=headers,
            data=data,
            params=params,
            timeout=_REQUEST_TIMEOUT,
        )
        return json.loads(response.content.decode("utf-8"))
    

    status_report = st.empty()

    with status_report.container():
        st.info("Evaluating argument map (1/2) ...")
        argmap_metrics = query(
            aea.as_api_argmap(),
            st.secrets["logikon_server"]["path_argmap"]
        )
        st.info("Evaluating essay annotation (2/2) ...")
        annotation_metrics = query(
            {
                "argmap": aea.as_api_argmap(reason_nodes_only=True),
                "textContentItems": aea.as_api_textContentItems(),
            },
            st.secrets["logikon_server"]["path_arganno"]
        )

    status_report.empty()


    return dict(argmap_metrics=argmap_metrics, annotation_metrics=annotation_metrics)

