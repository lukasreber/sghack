import streamlit as st
from streamlit_folium import folium_static
import pandas as pd
import requests
import json
import folium
from pandas import json_normalize

st.image('logo.jpeg')

# Import all necessary dat
immo = pd.read_csv('./data/immo_uni.csv')
supermarkets = pd.read_csv('./data/supermarkets.csv')
trains = pd.read_csv('./data/train.csv')
immo_uni = pd.read_csv('./data/immo_uni.csv')
immo_supermarket = pd.read_csv('./data/immo_supermarkets.csv')
immo_train = pd.read_csv('./data/immo_train.csv')


st.sidebar.title("Find Your Flat")
st.sidebar.subheader('Ein Projekt von Niels Ham und Lukas Reber')
st.sidebar.text('Unterstützt durch')
st.sidebar.image('sg.png')
st.sidebar.image('opendata_sg.png')
st.sidebar.image('upinfo.png')

# Filter for Distance to Universities
dist_uni = st.slider('Wähle die maximale Laufdistanz in Meter zur Uni',0,6000,1000,50)
immo_uni = immo_uni[immo_uni.distance_meters <= dist_uni].id.tolist()

# Filter for Distance to Supermarkets
dist_supermarket = st.slider('Wähle die maximale Laufdistanz in Meter zum nächsten Supermarkt',0,6000,500,50)
immo_supermarket = immo_supermarket[immo_supermarket.distance_meters <= dist_supermarket].id.tolist()

# Filter for Distance to Supermarkets
dist_trains = st.slider('Wähle die maximale Laufdistanz in Meter zum nächsten Bahnhof',0,6000,500,50)
immo_train = immo_train[immo_train.distance_meters <= dist_trains].id.tolist()

# toggle data on map
show_supermarkets = st.checkbox('Alle Supermärkte auf Karte anzeigen')
show_trains = st.checkbox('Alle Bahnhöfe auf Karte anzeigen')

# compare all lists
res_id = set(immo_uni) & set(immo_supermarket) & set(immo_train)

res = immo[immo.id.isin(res_id)]

# Return count of search results
st.subheader(f'Deine Suche ergibt {len(res.index)} Treffer')

# Display Results on Map
startloc = ['47.422124', '9.368013']
m = folium.Map(location=[startloc[0],startloc[1]], zoom_start=13)

for index, row in res.iterrows():
    popup = folium.Popup('Adresse: {0}<br>Preis: {1}'.format(row['street_number'],row.rent),max_width=300)
    folium.Marker([row.lat,row.lng],popup=popup).add_to(m)

if (show_supermarkets):
    for index, row in supermarkets.iterrows():
        folium.Marker([row.lon,row.lat],popup=row['properties.name'],icon=folium.Icon(color="green", icon="info-sign")).add_to(m)

if (show_trains):
    for index, row in trains.iterrows():
        folium.Marker([row.lat,row.lon],popup=row['Bezeichnung'],icon=folium.Icon(color="red", icon="info-sign")).add_to(m)


folium_static(m)

if (res.empty == False):
    # create dictionary for selection
    select = dict()
    for index, row in res.iterrows():
        select[(row.lat,row.lng,row.id)] = f'{row.street_number} - Preis: {row.rent}'

    def format_func(option):
        return select[option]

    # dropdown for selection of location
    location = st.selectbox("Wähle eine Wohnung aus den Suchresultaten aus", options=list(select.keys()), format_func=format_func)
    radius = st.slider('Wähle den Radius in Meter',200,1000,200,50)

    # Request Parkings
    def get_parking(lat,lon,radius=1000):
        r = requests.get(f'https://daten.stadt.sg.ch/api/records/1.0/search/?dataset=freie-parkplatze-in-der-stadt-stgallen-pls&q=&geofilter.distance={lat}%2C{lon}%2C{radius}')
        nhits = json.loads(r.content)['nhits']
        if nhits != 0:
            df = json_normalize(json.loads(r.content)['records'])
            df[['lon','lat']] = df['geometry.coordinates'].tolist()
            df = df[['fields.phname','lon','lat','fields.shortfree']]
        else:
            df = pd.DataFrame()
        return df,nhits

    parking,nhits = get_parking(location[0],location[1],radius)

    # Display Flat selection map
    m = folium.Map(location=[location[0],location[1]], zoom_start=16)

    folium.Circle(
        location=[location[0],location[1]], 
        radius=radius,
        color="#3186cc",
        fill=True,
        fill_color="#3186cc",
    ).add_to(m)

    folium.Marker([location[0],location[1]],popup='Ausgewählte Wohnung',icon=folium.Icon(color="red", icon="info-sign")).add_to(m)

    for index, row in parking.iterrows():
        popup = folium.Popup('{0}, freie Parkplätze: {1}'.format(row['fields.phname'],row['fields.shortfree']),max_width=300)
        folium.Marker([row.lat,row.lon],popup=popup).add_to(m)

    folium_static(m)

# Statistics
st.markdown(f'**Die ausgewählte Wohnung hat im Umkreis von {radius} Meter folgendes zu bieten:**')

# check if dataframe is not empty
if (parking.empty):
    parking_count = 0
else:
    parking_count = int(parking['fields.shortfree'].sum())


col1, col2, col3 = st.columns(3)
col1.metric('Parkhäuser',len(parking.index))
col2.metric('Freie Parkplätze',parking_count)
col3.metric('Parkhäuser',len(parking.index))