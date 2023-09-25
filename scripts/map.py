import pandas as pd
import matplotlib.pyplot as plt
import cartopy.crs as ccrs
import cartopy.feature as cfeature
import folium
import json
import re 

# Load data
df = pd.read_csv("https://raw.githubusercontent.com/Gevika/map_metagenome/main/data/data.tsv", sep="\\t", decimal=".", engine='python')
df['depth_numeric'] = pd.to_numeric(df['depth'], errors='coerce')
min_depth = df['depth_numeric'].min()
max_depth = df['depth_numeric'].max()

def get_color(depth):
    if '.' in str(depth):
        return 'green'
    elif depth == "unknown":
        return 'gray'
    else:
        return 'red'

# Create map
m = folium.Map(location=[47, 2], zoom_start=3, tiles="Stamen Terrain")
for index, row in df.iterrows():
    value1 = row['archive_project']
    value2 = row['study_primary_focus']
    popup_content = f'Project name:<br><a href="https://www.ncbi.nlm.nih.gov/search/all/?term={value1}" target="_blank">{value1}</a><br>Study primary focus:{value2}'
    popup = folium.Popup(popup_content, max_width=300)
    color = get_color(row["depth"])
    icon = folium.Icon(color=color, icon_color='white')
    folium.Marker(
        location=(row["latitude"], row["longitude"]),
        popup=popup,
        icon=icon
    ).add_to(m)

m.save("index.html")

depth_values = [str(row["depth"]) for _, row in df.iterrows()]
depth_values_str = json.dumps(depth_values)

slider_html = f'''
<link rel="stylesheet" href="https://cdn.jsdelivr.net/npm/nouislider@14.7.0/distribute/nouislider.min.css">
<div id="depth-slider" style="margin-top: 50px; width: 80%; margin-left: 10%;"></div>
<p id="slider-values" style="text-align: center;"></p>
<script src="https://cdn.jsdelivr.net/npm/nouislider@14.7.0/distribute/nouislider.min.js"></script>
<script>
    document.addEventListener('DOMContentLoaded', function() {{
        const depths = {depth_values_str};
        const min_val = {min_depth};
        const max_val = {max_depth};
        const markers = document.querySelectorAll(".leaflet-interactive");
        markers.forEach((marker, idx) => {{
            marker.setAttribute('data-depth', depths[idx]);
        }});
        
        var slider = document.getElementById('depth-slider');
        noUiSlider.create(slider, {{
            start: [{min_depth}, {max_depth}],
            connect: true,
            range: {{
                'min': {min_depth},
                'max': {max_depth}
            }},
            tooltips: [true, true],
            format: {{
                to: function(value) {{
                    return value.toFixed(1);
                }},
                from: function(value) {{
                    return value;
                }}
            }}
        }});
        
        slider.noUiSlider.on('update', function (values, handle) {{
            const min_val = parseFloat(values[0]);
            const max_val = parseFloat(values[1]);
            markers.forEach(marker => {{
                const depth = parseFloat(marker.getAttribute('data-depth'));
                const markerTransform = marker.style.transform;
                let shadow = null;
                document.querySelectorAll('.awesome-marker-shadow').forEach(shadowCandidate => {{
                    if (shadowCandidate.style.transform === markerTransform) {{
                        shadow = shadowCandidate;
                    }}
                }});
                if (depth < min_val || depth > max_val) {{
                    marker.style.display = 'none';
                    if (shadow) {{
                        shadow.style.display = 'none';
                    }}
                }} else {{
                    marker.style.display = '';
                    if (shadow) {{
                        shadow.style.display = '';
                    }}
                }}
            }});
            document.getElementById("slider-values").innerHTML = "Depth Range: " + values.map(val => val + "m").join(" to ");
        }});
    }});
</script>
'''

# Add JS to the HTML file
with open('index.html', 'a') as file:
    file.write(slider_html)

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
