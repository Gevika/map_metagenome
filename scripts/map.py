import pandas as pd
import matplotlib.pyplot as plt
import cartopy.crs as ccrs
import cartopy.feature as cfeature
import folium
import re 

df = pd.read_csv("https://raw.githubusercontent.com/Gevika/map_metagenome/main/data/data.tsv", sep="\t", decimal=".")

# map_html
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

# map_readme
fig, ax = plt.subplots(figsize=(15, 10), subplot_kw={'projection': ccrs.PlateCarree()})
ax.set_title('World Map with Data Points', fontsize=16)

ax.add_feature(cfeature.COASTLINE)
ax.add_feature(cfeature.BORDERS, linestyle=':')
ax.add_feature(cfeature.LAND, edgecolor='black')
ax.add_feature(cfeature.LAKES, edgecolor='black')
ax.add_feature(cfeature.RIVERS)
ax.gridlines(draw_labels=True, dms=True, x_inline=False, y_inline=False)

plt.scatter(df['longitude'], df['latitude'], s=100, c='red', marker='o', label=df['geo_loc_name'])
plt.tight_layout()
plt.savefig("images/map_image.png", bbox_inches='tight')

# update README.md
with open('README.md', 'r') as file:
    content = file.read()

image_insert = "\n![My Map](./images/map_image.png)\n"

new_content = re.sub(r'<!-- START-MAP-INSERT -->.*<!-- END-MAP-INSERT -->',
                     f'<!-- START-MAP-INSERT -->{image_insert}<!-- END-MAP-INSERT -->',
                     content, flags=re.DOTALL)

with open('README.md', 'w') as file:
    file.write(new_content)
