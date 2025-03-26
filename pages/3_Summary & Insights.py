import streamlit as st

st.set_page_config(page_title="Summary & Insights")


st.subheader("Insights:")

insights = ['Streamlit - for the web application', 
       'Google Cloud Platform (BigQuery) - for the data warehouse',
       'DBT - for data transformation',
       'Python (various packages) - for data manipulation, analysis, visualization, and modeling']

s = ''

for i in insights:
    s += "- " + i + "\n"

st.markdown(i)