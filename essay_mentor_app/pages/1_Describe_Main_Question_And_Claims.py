import streamlit as st

st.session_state.update(st.session_state)

st.set_page_config(page_title="Main Question And Claims", page_icon="?!")

st.markdown("# Main Question and Claims")
st.sidebar.header("Main Question and Claims")
st.write(
    """Enter your main question and claims below."""
)

#st.write("Back to [start](../)")

progress_bar = st.sidebar.progress(0)
status_text = st.sidebar.empty()

i=0.2
status_text.text("%i%% Complete" % i)
progress_bar.progress(i)

st.write("#### Debugging")
st.code(st.session_state.essay_raw if "essay_raw" in st.session_state else "`essay_raw` no in session_state")