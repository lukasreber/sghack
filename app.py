import streamlit as st
from streamlit_folium import folium_static
import pandas as pd
import requests
import json
import folium
from pandas import json_normalize
from shapely.geometry import Polygon
import geopandas as gpd

st.set_page_config(page_title='Find Your Flat',initial_sidebar_state='collapsed',menu_items={'Get Help': None, 'Report a bug': None, 'About': None})

st.image('./data/images/logo.jpeg')

# Import all necessary dat
immo = pd.read_csv('./data/immo_uni.csv')
supermarkets = pd.read_csv('./data/supermarkets.csv')
trains = pd.read_csv('./data/train.csv')
schools = pd.read_csv('./data/schools.csv')
immo_uni = pd.read_csv('./data/immo_uni.csv')
immo_supermarket = pd.read_csv('./data/immo_supermarkets.csv')
immo_train = pd.read_csv('./data/immo_train.csv')
immo_school = pd.read_csv('./data/immo_school.csv')


st.sidebar.title("Find Your Flat")
st.sidebar.subheader('Ein Projekt von Niels Ham und Lukas Reber')
st.sidebar.text('Unterstützt durch')
st.sidebar.image('./data/images/sg.png')
st.sidebar.image('./data/images/opendata_sg.png')
st.sidebar.image('./data/images/upinfo.png')

# Filter for Distance to Universities
dist_uni = st.slider('Wähle die maximale Laufdistanz in Meter zur Uni',0,6000,1000,50)
immo_uni = immo_uni[immo_uni.distance_meters <= dist_uni].id.tolist()

# Filter for Distance to Supermarkets
dist_supermarket = st.slider('Wähle die maximale Laufdistanz in Meter zum nächsten Supermarkt',0,6000,500,50)
immo_supermarket = immo_supermarket[immo_supermarket.distance_meters <= dist_supermarket].id.tolist()

# Filter for Distance to Train
dist_trains = st.slider('Wähle die maximale Laufdistanz in Meter zum nächsten Bahnhof',0,6000,1000,50)
immo_train = immo_train[immo_train.distance_meters <= dist_trains].id.tolist()

# Filter for Distance to Schools
dist_schools = st.slider('Wähle die maximale Laufdistanz in Meter zur nächsten Schule',0,6000,500,50)
immo_school = immo_school[immo_school.distance_meters <= dist_schools].id.tolist()

# toggle data on map
show_supermarkets = st.checkbox('Alle Supermärkte auf der Karte anzeigen')
show_trains = st.checkbox('Alle Bahnhöfe auf der Karte anzeigen')
show_schools = st.checkbox('Alle Schulen auf der Karte anzeigen')

# compare all lists
res_id = set(immo_uni) & set(immo_supermarket) & set(immo_train) & set(immo_school)

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

if (show_schools):
    for index, row in schools.iterrows():
        folium.Marker([row.lat,row.lon],popup=row['Bezeichnung'],icon=folium.Icon(color="blue", icon="info-sign")).add_to(m)


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

    parking,parking_nhits = get_parking(location[0],location[1],radius)

    # Request Freiraeume
    def get_freiraeume(lat,lon,radius=1000):
        r = requests.get(f'https://daten.stadt.sg.ch/api/records/1.0/search/?dataset=freiraume-stadt-stgallen&q=&facet=art&facet=bedeutung&facet=typ&geofilter.distance={lat}%2C{lon}%2C{radius}')
        nhits = json.loads(r.content)['nhits']
        if nhits != 0:
            df = json_normalize(json.loads(r.content)['records'])
            df[['lon','lat']] = df['geometry.coordinates'].tolist()
            df = df[['fields.art','lon','lat','fields.typ','fields.geo_shape.coordinates']]
        else:
            df = pd.DataFrame()
        return df,nhits

    freiraeume,freiraeume_nhits = get_freiraeume(location[0],location[1],radius)

    # Request Recycling
    def get_recycling(lat,lon,radius=1000):
        r = requests.get(f'https://daten.stadt.sg.ch/api/records/1.0/search/?dataset=sammelstellen&q=&facet=abfallarten&geofilter.distance={lat}%2C{lon}%2C{radius}')
        nhits = json.loads(r.content)['nhits']
        if nhits != 0:
            df = json_normalize(json.loads(r.content)['records'])
            df[['lon','lat']] = df['geometry.coordinates'].tolist()
            df = df[['fields.standort','lon','lat','fields.abfallarten']]
        else:
            df = pd.DataFrame()
        return df,nhits

    recycling,recycling_nhits = get_recycling(location[0],location[1],radius)

    # Request Mobility
    def get_mobility(lat,lon,radius=1000):
        r = requests.get(f'https://daten.stadt.sg.ch/api/records/1.0/search/?dataset=mobility-stationen-und-fahrzeuge-schweiz&geofilter.distance={lat}%2C{lon}%2C{radius}')
        nhits = json.loads(r.content)['nhits']
        if nhits != 0:
            df = json_normalize(json.loads(r.content)['records'])
            df[['lon','lat']] = df['geometry.coordinates'].tolist()
            df = df[['fields.name','lon','lat']]
        else:
            df = pd.DataFrame()
        return df,nhits

    mobility,mobility_nhits = get_mobility(location[0],location[1],radius)

    # Request Velo
    def get_velo(lat,lon,radius=1000):
        r = requests.get(f'https://daten.stadt.sg.ch/api/records/1.0/search/?dataset=veloabstellplatze&q=signal%3A%22P+nur+Velo%22&geofilter.distance={lat}%2C{lon}%2C{radius}')
        nhits = json.loads(r.content)['nhits']
        if nhits != 0:
            df = json_normalize(json.loads(r.content)['records'])
            df[['lon','lat']] = df['geometry.coordinates'].tolist()
            df = df[['fields.adresse','lon','lat']]
        else:
            df = pd.DataFrame()
        return df,nhits

    velo,velo_nhits = get_velo(location[0],location[1],radius)

    # Is Appartment inside a 30-Tempo Zone
    def get_zone(lat,lon):
        r = requests.get(f'https://daten.stadt.sg.ch/api/records/1.0/search/?dataset=tempo-30-zonen&q=&facet=realisiert&geofilter.distance={lat}%2C{lon}')
        nhits = json.loads(r.content)['nhits']
        return int(nhits)

    zone_nhits = get_zone(location[0],location[1])
    
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
        folium.Marker([row.lat,row.lon],popup=popup,icon=folium.Icon(color="black", icon="car", prefix="fa")).add_to(m)

    for index, row in recycling.iterrows():
        popup = folium.Popup('{0}, Abfallarten: {1}'.format(row['fields.standort'],row['fields.abfallarten']),max_width=300)
        folium.Marker([row.lat,row.lon],popup=popup,icon=folium.Icon(color="green", icon="glyphicon-trash")).add_to(m)

    for index, row in mobility.iterrows():
        popup = folium.Popup('Mobility Station: {0}'.format(row['fields.name']),max_width=300)
        folium.Marker([row.lat,row.lon],popup=popup,icon=folium.Icon(color="green")).add_to(m)

    for index, row in velo.iterrows():
        popup = folium.Popup('Veloparkplatz: {0}'.format(row['fields.adresse']),max_width=300)
        folium.Marker([row.lat,row.lon],popup=popup,icon=folium.Icon(color="green",icon="bicycle",prefix="fa")).add_to(m)

    for index, row in freiraeume.iterrows():
        popup = folium.Popup('{0}, Typ: {1}'.format(row['fields.art'],row['fields.typ']),max_width=300)
        folium.Marker([row.lat,row.lon],popup=popup,icon=folium.Icon(color="blue")).add_to(m)
        polygon_geom = Polygon(row['fields.geo_shape.coordinates'][0])
        polygon = gpd.GeoDataFrame(index=[0], crs='EPSG:4326', geometry=[polygon_geom])
        folium.GeoJson(polygon).add_to(m)
    
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
    col3.metric('Freiräume',len(freiraeume.index))
    col1.metric('Sammelstellen',len(recycling.index))
    col2.metric('Mobility Stationen',len(mobility.index))
    col3.metric('Veloparkplätze',len(velo.index))

    if (zone_nhits > 0):
        st.markdown('<div style="background-color: #e1f5fe">Hey hier noch ein Hinweis: Deine Wohnung liegt in einer 30er Zone. Wir gehen daher davon aus, dass sich dein neues Zuhause in einer ruhigen Gegend befindet 👌</div>', unsafe_allow_html=True)
