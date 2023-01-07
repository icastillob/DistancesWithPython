# pip install geopy
# Library ---
import urllib.parse
import geopy.distance
from geopy.geocoders import Nominatim
import requests
import pandas as pd
import numpy as np
import geopandas as gpd

Filename = r'Establecimientos_Educacionales_2021.dbf'
Table = gpd.read_file(Filename)
df = pd.DataFrame(Table)
df = df[['LATITUD', 'LONGITUD', 'NOM_RBD']]

# # Get latitude and longitude ---
address = 'Palacio de la Moneda, Santiago'
url = 'https://nominatim.openstreetmap.org/search/' + urllib.parse.quote(address) +'?format=json'

response = requests.get(url).json()
print(response[0]["lat"])
print(response[0]["lon"])

# Get distance ---
coords_1 = (response[0]["lat"], response[0]["lon"])
lat = df['LATITUD'].to_list()
long = df['LONGITUD'].to_list()

geolocator = Nominatim(user_agent="red")
lista_address = []
lista_vc = []
for i in range(len(df)):
    try:
        lista_vc.append(geopy.distance.geodesic(coords_1, f'{lat[i]},{long[i]}').km)
        # location = geolocator.reverse(f'{lat[i]},{long[i]}')
        # lista_address.append(location.address)
    except:
        lista_vc.append('No tiene')

df['distance'] = lista_vc
# df['address'] = lista_address
df = df[df['distance'] != 'No tiene']
df['distance'] = df['distance'].astype('float')
df = df[df['distance'] <= 2].sort_values('distance', ascending=True)

with pd.ExcelWriter('address_distance.xlsx') as writer:
    df.to_excel(writer, sheet_name='address_distance', index=False)


# mapbox ---
import plotly.express as px

fig = px.scatter_mapbox(
    df, lat="LATITUD", lon="LONGITUD", color='distance',
    color_continuous_scale=["black", "purple", "red" ], 
    size_max=30, 
    zoom=13
    #mapbox_style="open-street-map"
    )
fig.update_layout(
        title='Distance with Mapbox',
        autosize=True,
        hovermode='closest',
        showlegend=False,
        mapbox_accesstoken=api_token, 
        mapbox_style = "mapbox://styles/strym/ckhd00st61aum19noz9h8y8kw")
fig.update_traces(marker=dict(size=6))
fig.add_scattermapbox(
    lat = [response[0]["lat"]],
    lon = [response[0]["lon"]],
    mode = 'markers+text',
    text = 'Your Center Point',
    marker_size=15,
    marker_color='rgb(235, 0, 100)'
)
fig.write_html('gps.html')

