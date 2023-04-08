from io import StringIO
import logging
import subprocess
import sys
import time

import graphviz
import markdown
import markdownify
import plotly.graph_objects as go
import pandas as pd
from PyPDF2 import PdfReader
import streamlit as st
from streamlit_extras.switch_page_button import switch_page

from backend.aea_datamodel import ArgumentativeEssayAnalysis
import backend.components as components
import backend.examples
import backend.utils

DEBUG = True



# init
backend.utils.page_init(is_startpage=True)


def main():

    st.session_state.update(st.session_state)
    st.session_state["DEBUG"] = DEBUG

    st.title('TESSY - Essay Tutor')
    st.write('**The AI Co-Tutor that supports you in writing better essays, and your teacher in grading them.**')

    if not "aea" in st.session_state:
        st.session_state["aea"] = ArgumentativeEssayAnalysis()
    aea:ArgumentativeEssayAnalysis = st.session_state.aea


    #########
    # test section #

    import plotly.graph_objects as go
    import matplotlib

    cmap = matplotlib.cm.get_cmap('RdYlGn')

    test_num = st.slider('test', min_value=0, max_value=100, value=50, step=1)

    cmap = matplotlib.cm.get_cmap('RdYlGn')
    rgba = cmap(test_num/100.0)
    

    fig = go.Figure(go.Indicator(
        mode = "gauge+number",
        value = test_num,
        domain = {'x': [0, 1], 'y': [0, 1]},
        #title = {'text': "plausible", 'font': {'size': 18}},
        #delta = {"prefix": "plausible", "reference": 50, "relative": True, "valueformat":"0d"},
        number = {
            'font': {'size': 24},
            'prefix': 'plausible (',
            'suffix': ')',
        },
        gauge = {
            'axis': {
                'range': [None, 100.],
                'tick0': 100/7,
                'dtick': 100/7,
                'showticklabels': False,
                'tickwidth': 1,
                'tickcolor': "darkblue",
            },
            'bar': {'color': f'rgba{rgba}'},
            'bgcolor': "white",
            'borderwidth': 2,
            'bordercolor': "gray",
            #'steps': [
            #    {'range': [0, 50], 'color': 'cyan'},
            #    {'range': [5, 70], 'color': 'royalblue'}],
            'threshold': {
                'line': {'color': "black", 'width': 4},
                'thickness': 0.75,
                'value': test_num}
            }
        ))
    fig.update_layout(
        width=300,
        height=150,
        margin=dict(l=20, r=20, t=1, b=1),
    )
    fig3 = go.Figure(go.Indicator(
        mode = "gauge+number",
        value = 0,
        domain = {'x': [0, 1], 'y': [0, 1]},
        #title = {'text': "plausible", 'font': {'size': 18}},
        #delta = {"prefix": "plausible", "reference": 50, "relative": True, "valueformat":"0d"},
        number = {
            'font': {'size': 24},
            'prefix': 'arbitrary (',
            'suffix': ')',
        },
        gauge = {
            'axis': {
                'range': [None, 100.],
                'tick0': 100/7,
                'dtick': 100/7,
                'showticklabels': False,
                'tickwidth': 1,
                'tickcolor': "darkblue",
            },
            'bar': {'color': 'white'},
            'bgcolor': "lightgray",
            'borderwidth': 2,
            'bordercolor': "gray",
            #'steps': [
            #    {'range': [0, 50], 'color': 'cyan'},
            #    {'range': [5, 70], 'color': 'royalblue'}],
            #'threshold': {
            #    'line': {'color': "black", 'width': 4},
            #    'thickness': 0.75,
            #    'value': test_num}
            }
        ))
    fig3.update_layout(
        width=300,
        height=150,
        margin=dict(l=20, r=20, t=1, b=1),
    )    
    col1, col2 = st.columns(2)
    with col1:
        st.markdown("Overall quality of the **argumentative analysis**:")
        st.plotly_chart(fig, use_container_width=True)
    with col2:
        st.markdown("Overall quality of the **essay annotation**:")
        st.plotly_chart(fig3, use_container_width=True)


    with st.expander("Detailed score [PrArg2]"):
        col1, col2 = st.columns([2,1])
        with col1:
            st.markdown("Argumentative relation of [PrArg2] to further arguments:")
        with col2:
            fig2 = go.Figure(
                go.Indicator(
                    mode = "number+gauge",
                    value = None, #test_num,
                    gauge = {
                        'bgcolor': 'lightgray',
                        'bar': {'color': f'rgba{rgba}','thickness': 0.6},
                        'shape': "bullet",
                        'axis' : {'range': [None, 100.],'visible': False}
                    },
                    domain = {'x': [0, 1], 'y': [0, 1]}
                )
            )
            fig2.update_layout(
                width=300,
                height=25,
                margin=dict(l=10, r=10, t=1, b=1),
            )
            st.plotly_chart(fig2, use_container_width=True)

        summary = f"It is <b>very likely</b> that [PrArg1] is related to further arguments in another way than specified by the author (i.e., not as pro reason for [xxx]). Most plausible alternatives:"
        details = f"<ol><li>Pro reason for [Obj2] (23%)</li><li>Con reason against [Claim1] (12%)</li><li>Pro reason for [Rbt3] (11%)</li></ol>"
        st.markdown(
            f"<p><details><summary>{summary}</summary><p>{details}</details></p>",
            unsafe_allow_html=True
        )

        col1, col2 = st.columns([2,1])
        with col1:
            st.markdown("Linkage of [PrArg2] to paragraphs in the text (annotation):")
        with col2:
            fig2 = go.Figure(
                go.Indicator(
                    mode = "number+gauge",
                    value = test_num,
                    gauge = {
                        'bar': {'color': f'rgba{rgba}','thickness': 0.6},
                        'shape': "bullet",
                        'axis' : {'range': [None, 100.],'visible': False}
                    },
                    domain = {'x': [0, 1], 'y': [0, 1]}
                )
            )
            fig2.update_layout(
                width=300,
                height=25,
                margin=dict(l=10, r=10, t=1, b=1),
            )
            st.plotly_chart(fig2, use_container_width=True)
        summary = f"It is <b>unlikely</b> that [PrArg1] appears in the essay at different places than specified by the author (i.e., ¶XXX). Most plausible alternatives:"
        details = f"<ol><li>Discussed in ¶002 (15%)</li><li>Not discussed in ¶003 (12%)</li><li>Discussed in ¶001 (4%)</li></ol>"
        st.markdown(
            f"<p>{summary}</p><p>{details}</p>",
            unsafe_allow_html=True
        )

    #########



    if not "has_been_submitted" in st.session_state:
        st.session_state["has_been_submitted"] = False        

    if aea.essay_content_items:
        st.write("(Reload this page to start over with another text.)")
        st.write("------")
        st.write("*The essay that's currently being processed*:")
        components.display_essay(st.session_state.aea.essay_content_items)
        st.stop()

    if "essay_raw" not in st.session_state or st.session_state.essay_raw is None: 
        st.session_state["essay_raw"] = "" 


    col1, col2 = st.columns(2)
    with col1:
        # file uploader
        uploaded_file = st.file_uploader("You can upload your essay ...", type=["txt", "md", "pdf"])
        if uploaded_file is not None:
            essay_raw:str = ""
            if uploaded_file.name.endswith(".pdf"):
                reader = PdfReader(uploaded_file)
                for page in reader.pages:
                    essay_raw += (page.extract_text())
                    essay_raw += "\n\n"
            elif uploaded_file.name.endswith(".txt") or uploaded_file.name.endswith(".md"):
                stringio = StringIO(uploaded_file.getvalue().decode("utf-8"))
                tmp_text = stringio.read()
                # remove html tags:
                tmp_text = markdown.markdown(tmp_text)
                tmp_text = markdownify.markdownify(tmp_text)
                essay_raw = tmp_text
            st.session_state["essay_raw"] = essay_raw

    with col2:
        # select example essay
        def paste_example_essay():
            if st.session_state.example_essay_id == "Example 1 (Racism)":
                st.session_state["essay_raw"] = backend.examples.EX1_RACISM_PAPERSOWL
            elif st.session_state.example_essay_id == "Example 2 (Veganism)":
                st.session_state["essay_raw"] = backend.examples.EX2_VEGANISM_PAPERSOWL
            elif st.session_state.example_essay_id == "Example 3 (Critical Thinking)":
                st.session_state["essay_raw"] = backend.examples.EX3_CRITTHINK
            else:
                st.session_state["essay_raw"] = st.session_state.example_essay_id
        st.selectbox(
            "... or select an example ...",
            ["", "Example 1 (Racism)", "Example 2 (Veganism)", "Example 3 (Critical Thinking)"],
            on_change=paste_example_essay,
            key="example_essay_id",
        )
        

    essay_raw = st.text_area(
        "... or directly paste your text here:",
        height=280,
        key="essay_raw",
        help=(
            "Please use basic [markdown formatting](https://www.markdownguide.org/basic-syntax/), in particular:\n "
            " * '#', '##', '###' for headings\n"
            " * paragraphs are separated by an empty line\n"
        )
    )

    if not essay_raw:
        # info with lightbulb icon
        st.info(
            "TIP: Instead of uploading a file, consider converting "
            "it with https://pandoc.org/try/ to markdown and paste "
            "the resulting text.",
            icon="💡"
        )
        placeholder = st.empty()
    else:
        essay_html = markdown.markdown(essay_raw)
        st.success(
            "Your essay is ready to be analysed. (Preview essay structure below.)"
        )
        placeholder = st.empty()
        st.write("------")
        with st.expander("Preview essay structure (click to expand)"):
            components.display_essay(essay_html)
            st.write(" ")

    with placeholder:
        if st.button("Use this text and proceed with next step", disabled=not(essay_raw)):
            aea.essaytext_md = essay_raw
            essay_html = markdown.markdown(essay_raw)
            aea.essaytext_html = essay_html
            aea.essay_content_items = backend.utils.parse_essay_content(essay_html)
            switch_page("Describe Main Question And Claims")



        #st.write("------")
        #st.write("Debugging:")
        #st.code(st.session_state.essay_raw if "essay_raw" in st.session_state else "")

if __name__ == '__main__':
    main()
