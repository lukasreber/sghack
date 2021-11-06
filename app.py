import streamlit as st
from streamlit_folium import folium_static
import pandas as pd
import folium

# Import all necessary dat
immo_uni = pd.read_csv('immo_uni.csv')


st.title("Find Your Flat")

# Filter for Distance to Universities
dist_uni = st.slider('Wähle die maximale Laufdistanz in Meter zur Uni',0,6000)
immo_uni = immo_uni[immo_uni.distance_meters <= dist_uni]

# Display Results on Map
startloc = ['47.422124', '9.368013']
m = folium.Map(location=[startloc[0],startloc[1]], zoom_start=13)

# folium.Circle(
#     location=[location[0],location[1]], 
#     radius=radius,
#     color="#3186cc",
#     fill=True,
#     fill_color="#3186cc",
#     popup="test"
# ).add_to(m)

#folium.Marker([location[0],location[1]],popup='selection',icon=folium.Icon(color="red", icon="info-sign")).add_to(m)

for index, row in immo_uni.iterrows():
    folium.Marker([row.lat,row.lng],popup=row['street_number']).add_to(m)

folium_static(m)

st.dataframe(immo_uni)