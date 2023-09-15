import folium
import pandas

df = pandas.read_csv("data.tsv")
lat = list(df["latitude"])
lon = list(df["longitude"])
name_list = list(df["study_primary_focus"])
archive = list(df["archive_project"])

html = """
Project name:<br>
<a href="https://www.ncbi.nlm.nih.gov/search/all/?term=%%22%s%%22" target="_blank">%s</a><br>
Study primary focus: %s
"""


map = folium.Map(location=[47, 2], zoom_start=3, tiles="Stamen Terrain")
fgv = folium.FeatureGroup(name="Metagenomic samples")

for lt, ln, name, archive_name in zip(lat, lon, name_list, archive):
    iframe = folium.IFrame(html=html % (archive_name, archive_name, name), width=200, height=100)
    fgv.add_child(folium.CircleMarker(location=[lt, ln], radius=6, popup=folium.Popup(iframe), fill_color='red', color='grey', fill_opacity=0.7))


map.add_child(fgv)
map.add_child(folium.LayerControl())

map.save("index.html")
