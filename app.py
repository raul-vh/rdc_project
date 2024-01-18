import os
from dotenv import load_dotenv
import streamlit as st
import pandas as pd
import duckdb
import plotly.express as px

load_dotenv()
url = os.getenv('GOOGLESHEETS_URL')

try:
    df = duckdb.sql(
        f"SELECT * FROM read_csv_auto('{url}')").df()
except Exception as exeption:
    print(str(exeption))

st.set_page_config(page_title="Onderzoek wachtwoordgebruik en digitale veiligheid", page_icon=":bar_chart:", layout="wide")

st.write(df)