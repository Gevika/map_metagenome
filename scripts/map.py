import pandas as pd
import matplotlib.pyplot as plt
import cartopy.crs as ccrs
import cartopy.feature as cfeature
import folium
import json
import re 
import io
from PIL import Image

# Read data from the URL into a DataFrame and correct the 'depth' column to numeric values
df = pd.read_csv("https://raw.githubusercontent.com/Gevika/map_metagenome/main/data/data.tsv", sep="\\t", decimal=".", engine='python')
df['depth_numeric'] = pd.to_numeric(df['depth'], errors='coerce')
min_depth = df['depth_numeric'].min()
max_depth = df['depth_numeric'].max()

# Function to determine color based on the depth value
def get_color(depth):
    if '.' in str(depth):
        return 'green'
    elif depth == "unknown":
        return 'gray'
    else:
        return 'red'

# Create a Folium map object and iterate through DataFrame rows to add markers
m = folium.Map(location=[47, 2], zoom_start=2.8, tiles="http://services.arcgisonline.com/arcgis/rest/services/NatGeo_World_Map/MapServer/tile/{z}/{y}/{x}", attr="© OpenStreetMap contributors")
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

# Save the map as an HTML file
m.save("index.html")

# Process depth values and prepare slider HTML element with embedded JS for interactivity
depth_values = [str(row["depth"]) for _, row in df.iterrows()]
depth_values_str = json.dumps(depth_values)

slider_html = f'''
<link rel="stylesheet" href="https://cdn.jsdelivr.net/npm/nouislider@14.7.0/distribute/nouislider.min.css">
<style>
    .awesome-marker-shadow {{
        display: none !important;
    }}
</style>
<div id="depth-slider" style="margin-top: 50px; width: 80%; margin-left: 10%;"></div>
<p id="slider-values" style="text-align: center;"></p>
<div id="button-container" style="text-align: center; margin-top: 20px;">
    <button id="red-button" style="background-color: red; color: white;">Toggle Red Markers</button>
    <button id="gray-button" style="background-color: gray; color: white;">Toggle Gray Markers</button>
    <button id="green-button" style="background-color: green; color: white;">Toggle Green Markers</button>
</div>
<script src="https://cdn.jsdelivr.net/npm/nouislider@14.7.0/distribute/nouislider.min.js"></script>
<script>
    document.addEventListener('DOMContentLoaded', function() {{
        const depths = {depth_values_str};
        const min_val = {min_depth};
        const max_val = {max_depth};
        const markers = document.querySelectorAll(".leaflet-interactive");
        markers.forEach((marker, idx) => {{
            const depth = depths[idx];
            let valueType;
            if (depth === "unknown") {{
                valueType = 'unknown';
            }} else if (depth === "nan") {{
                valueType = 'none';
            }} else {{
                valueType = 'float';
            }}
            marker.setAttribute('data-depth', depth);
            marker.setAttribute('data-value-type', valueType);
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
                if (depth < min_val || depth > max_val) {{
                    marker.style.display = 'none';
                }} else {{
                    marker.style.display = '';
                }}
            }});
            document.getElementById("slider-values").innerHTML = "Depth Range: " + values.map(val => val + "m").join(" to ");
        }});
        
        const redButton = document.getElementById('red-button');
        const grayButton = document.getElementById('gray-button');
        const greenButton = document.getElementById('green-button');
        
        let noneVisible = true;
        let unknownVisible = true;
        let floatVisible = true;
        
        function toggleMarkers(valueType, isVisible) {{
            markers.forEach(marker => {{
                const value = marker.getAttribute('data-value-type');
                if (value === valueType) {{
                    marker.style.display = isVisible ? '' : 'none';
                }}
            }});
        }}
        
        redButton.addEventListener('click', function() {{
            noneVisible = !noneVisible;
            toggleMarkers('none', noneVisible);
        }});
        
        grayButton.addEventListener('click', function() {{
            unknownVisible = !unknownVisible;
            toggleMarkers('unknown', unknownVisible);
        }});
        
        greenButton.addEventListener('click', function() {{
            floatVisible = !floatVisible;
            toggleMarkers('float', floatVisible);
        }});
    }});
</script>
'''

# Append the slider code to the previously saved map HTML file
with open('index.html', 'a') as file:
    file.write(slider_html)

# Define the favicon link and insert it into the <head> section of the map HTML file
favicon_link = '<link rel="icon" href="images/git_img_link_map.png" type="image/x-icon" />'
with open('index.html', 'r') as file:
    content = file.read()
head_end_index = content.find('</head>')
new_content = content[:head_end_index] + favicon_link + content[head_end_index:]
with open('index.html', 'w') as file:
    file.write(new_content)

# Create and save a Matplotlib plot showing the geographical distribution of the data points
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
plt.savefig("images/git_img_map.png", bbox_inches='tight')

# Read the README, insert the created image, and write the updated content back to the README
with open('README.md', 'r') as file:
    content = file.read()
image_insert = "\n![My Map](./images/git_img_map.png)\n"
new_content = re.sub(r'<!-- START-MAP-INSERT -->.*<!-- END-MAP-INSERT -->',
                     f'<!-- START-MAP-INSERT -->{image_insert}<!-- END-MAP-INSERT -->',
                     content, flags=re.DOTALL)
with open('README.md', 'w') as file:
    file.write(new_content)

img_data = m._to_png(5)
img = Image.open(io.BytesIO(img_data))
img.save('images/git_img_map_folium.png')
