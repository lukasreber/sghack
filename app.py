import streamlit as st
from streamlit_folium import folium_static
import pandas as pd
import folium

st.image('logo.jpeg')

# Import all necessary dat
immo = pd.read_csv('immo_uni.csv')
immo_uni = pd.read_csv('immo_uni.csv')
immo_supermarket = pd.read_csv('supermarkets.csv')


st.sidebar.title("Find Your Flat")
st.sidebar.subheader('Ein Projekt von Niels Ham und Lukas Reber')
st.sidebar.image('opendata_sg.png')

# Filter for Distance to Universities
dist_uni = st.slider('Wähle die maximale Laufdistanz in Meter zur Uni',0,6000)
immo_uni = immo_uni[immo_uni.distance_meters <= dist_uni].id.tolist()

# Filter for Distance to Supermarkets
dist_supermarket = st.slider('Wähle die maximale Laufdistanz in Meter zum nächsten Supermarkt',0,6000)
immo_supermarket = immo_supermarket[immo_supermarket.distance_meters <= dist_supermarket].id.tolist()

# compare all lists
res_id = set(immo_uni) & set(immo_supermarket)

res = immo[immo.id.isin(res_id)]

# Return count of search results
st.text(f'Deine Suche ergibt {len(res.index)} Treffer')

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

for index, row in res.iterrows():
    popup = folium.Popup('Adresse: {0}<br>Preis: {1}'.format(row['street_number'],row.rent),max_width=300)
    folium.Marker([row.lat,row.lng],popup=popup).add_to(m)

folium_static(m)

st.dataframe(res)