import streamlit as st
from streamlit_folium import folium_static
import pandas as pd
import requests
from pandas import json_normalize
import json
import folium

st.title("Parking in St. Gallen")

CHOICES = {(47.42664,9.38804): "Steingrüeblistrasse 11, 9000 St. Gallen", (47.4239053,9.3656355): "Tellstrasse 20, 9000 St. Gallen", (47.4192677,9.3658008): "Unterstrasse 28, 9000 St. Gallen"}

def format_func(option):
    return CHOICES[option]

location = st.selectbox("Select a location", options=list(CHOICES.keys()), format_func=format_func)

radius = st.slider('Choose a radius in meter',200,1000)

def get_parking(lat,lon,radius=1000):
    r = requests.get(f'https://daten.stadt.sg.ch/api/records/1.0/search/?dataset=freie-parkplatze-in-der-stadt-stgallen-pls&q=&geofilter.distance={lat}%2C{lon}%2C{radius}')
    nhits = json.loads(r.content)['nhits']
    if nhits != 0:
        df = json_normalize(json.loads(r.content)['records'])
        df[['lon','lat']] = df['geometry.coordinates'].tolist()
        df = df[['fields.phname','lon','lat']]
    else:
        df = pd.DataFrame()
    return df,nhits

df,nhits = get_parking(location[0],location[1],radius)

#selection = {'fields.phname':'test','lon':location[1],'lat':location[0]}
#df = df.append(selection, ignore_index=True)

m = folium.Map(location=[location[0],location[1]], zoom_start=14)

folium.Circle(
    location=[location[0],location[1]], 
    radius=radius,
    color="#3186cc",
    fill=True,
    fill_color="#3186cc",
    popup="test"
).add_to(m)

folium.Marker([location[0],location[1]],popup='selection',icon=folium.Icon(color="red", icon="info-sign")).add_to(m)

for index, row in df.iterrows():
    folium.Marker([row.lat,row.lon],popup=row['fields.phname']).add_to(m)

folium_static(m)

st.dataframe(df)