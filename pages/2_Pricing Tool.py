import streamlit as st


st.set_page_config(page_title="Pricing Tool")


st.title("Pricing Analytics Tool")





with st.sidebar:
    st.title("Inputs")
    add_radio = st.radio(
        "Select A Model  ",
        ("Standard (5-15 days)", "Express (2-5 days)")
    )


add_selectbox = st.sidebar.selectbox(
    "How would you like to be contacted?",
    ("Email", "Home phone", "Mobile phone")
)
