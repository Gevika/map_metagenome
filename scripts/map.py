import pandas as pd
import matplotlib.pyplot as plt
import cartopy.crs as ccrs
import cartopy.feature as cfeature
import folium
import json
import re 

# Load data
df = pd.read_csv("https://raw.githubusercontent.com/Gevika/map_metagenome/main/data/data.tsv", sep="\\t", decimal=".")
df['depth_numeric'] = pd.to_numeric(df['depth'], errors='coerce')
min_depth = df['depth_numeric'].min()
max_depth = df['depth_numeric'].max()

# Create map
m = folium.Map(location=[47, 2], zoom_start=3, tiles="Stamen Terrain")
for index, row in df.iterrows():
    popup_content = f'Project name:<br><a href="https://www.ncbi.nlm.nih.gov/search/all/?term={{row["archive_project"]}}" target="_blank">{{row["archive_project"]}}</a><br>Study primary focus: {{row["study_primary_focus"]}}'
    popup = folium.Popup(popup_content, max_width=300)
    folium.CircleMarker(
        location=(row["latitude"], row["longitude"]),
        radius=6,
        popup=popup,
        fill_color='red',
        color='grey',
        fill_opacity=0.7
    ).add_to(m)

m.save("index.html")

depth_values = [str(row["depth"]) for _, row in df.iterrows()]
depth_values_str = json.dumps(depth_values)

# JavaScript код для установки атрибутов data-depth для каждого маркера после их создания
js_code = f'''
<script>
    document.addEventListener('DOMContentLoaded', function() {{
        const depths = {depth_values_str};
        const markers = document.querySelectorAll(".leaflet-interactive");
        markers.forEach((marker, idx) => {{
            marker.setAttribute('data-depth', depths[idx]);
        }});
    }});
</script>
'''

# Add JS to the HTML file
with open('index.html', 'a') as file:
    file.write(js_code)

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

with open('README.md', 'r') as file:
    content = file.read()
image_insert = "\n![My Map](./images/map_image.png)\n"
new_content = re.sub(r'<!-- START-MAP-INSERT -->.*<!-- END-MAP-INSERT -->',
                     f'<!-- START-MAP-INSERT -->{image_insert}<!-- END-MAP-INSERT -->',
                     content, flags=re.DOTALL)
with open('README.md', 'w') as file:
    file.write(new_content)
