import streamlit as st
import pandas as pd
import io
from google.cloud import bigquery

st.set_page_config(page_title="Exploratory Data Analysis")


st.title("Exploratory Data Analysis")


tab1, tab2, tab3, tab4 = st.tabs(["Data Preview", "Data Information", "Column and Row Count", "Descriptive Analysis"])

with tab1:
    st.markdown('<p class="sub-header">Data Preview</p>', unsafe_allow_html=True)
    st.write(df.head())

with tab2:
    st.markdown('<p class="sub-header">Data Information</p>', unsafe_allow_html=True)
    buffer = io.StringIO()
    df.info(buf=buffer)
    s = buffer.getvalue()
    st.markdown(f"```{s}```")

with tab3:
    st.markdown('<p class="sub-header">Column and Row Count</p>', unsafe_allow_html=True)
    st.write(f"Rows: {df.shape[0]}")
    st.write(f"Columns: {df.shape[1]}")

with tab4:
    st.markdown('<p class="sub-header">Descriptive Analysis</p>', unsafe_allow_html=True)
    st.markdown('<div class="info-message">This gives the statistical value of the numerical columns in the dataframe, please note that other columns are omitted.</div>', unsafe_allow_html=True)
    st.write(df.describe())

