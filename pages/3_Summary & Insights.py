import streamlit as st

st.set_page_config(page_title="Summary & Insights")


st.subheader("Insights:")

lst = ['Streamlit - for the web application', 
       'Google Cloud Platform (BigQuery) - for the data warehouse',
       'DBT - for data transformation',
       'Python (various packages) - for data manipulation, analysis, visualization, and modeling',
       'GitHub - for version control']
s = ''

for i in lst:
    s += "- " + i + "\n"

st.markdown(s)