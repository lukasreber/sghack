import streamlit as st
from streamlit_folium import folium_static
import pandas as pd
import requests
import folium

st.title("ImmoFinder")

immo = pd.read_csv('https://raw.githubusercontent.com/cividi/st-gallen-urban-indicators/main/data/price-monitoring/price-monitoring.csv')

st.dataframe(immo)