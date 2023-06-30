import pandas as pd
import geopandas as gpd
import folium
import branca
import json

# Load the GeoJSON data
gdf = gpd.read_file('/Users/adpena/PycharmProjects/RespectCampaignMap/Current_Districts_2023.geojson')

# Load the teacher experience data
df = pd.read_csv('DSTAF.csv')

gdf["DISTRICT_C"] = gdf["DISTRICT_C"].apply(lambda x: "'" + ("0" * (6 - len(str(x)))) + str(x))
gdf = gdf.rename(columns={"DISTRICT_C": "District Number"})
df = df.rename(columns={"DISTRICT": "District Number"})

# Merge the GeoDataFrame with the DataFrame
merged = pd.merge(gdf, df, on='District Number', how='left')

enrollment = pd.read_excel("Directory.xlsx")

merged = pd.merge(merged, enrollment[["District Number", "District Enrollment as of Oct 2022"]], on="District Number", how="left")

merged = merged.rename(columns={"District Enrollment as of Oct 2022": "enrollment"})

# Load the Excel file
df_local = pd.read_excel('2021-2022 TAPR DStaff Legend.xlsx')

# Create a dictionary from the 'NAME' and 'LABEL' columns
name_label_dict = pd.Series(df_local.LABEL.values,index=df_local.NAME.values).to_dict()
name_label_dict_processed = {}

for k, v in name_label_dict.items():
    if "District Number" not in v:
        name_label_dict_processed[k.replace("\xa0", "")] = v.replace("\xa0", "")

merged = merged.rename(columns=name_label_dict_processed)

def calc_experience_percentage(row):
    total = float(row["District 2022 Staff: Teacher Total Full Time Equiv Count"])
    beginning = float(row["District 2022 Staff: Teacher Beginning Full Time Equiv Count"])
    onetofive = float(row["District 2022 Staff: Teacher 1-5 Years Full Time Equiv Count"])
    return round(((total -  beginning - onetofive)/total) * 100, 2)

merged["experience_percentage"] = merged.apply(calc_experience_percentage, axis=1)

merged.to_file("merged.geojson", driver='GeoJSON')

# Convert the GeoDataFrame to GeoJSON
geojson_data = json.loads(merged.to_json())

s = "{s}"
x = "{x}"
y = "{y}"
z = "{z}"

position = "{position: 'bottomright'}"

# Generate the HTML file
with open('map.html', 'w') as f:
    f.write(f"""
<!DOCTYPE html>
<html>
<head>
    <!-- Load Leaflet from CDN-->
    <link rel="stylesheet" href="https://unpkg.com/leaflet/dist/leaflet.css" />
    <script src="https://unpkg.com/leaflet/dist/leaflet.js"></script>

    <!-- Load Chroma.js (for colors) from CDN -->
    <script src="https://cdnjs.cloudflare.com/ajax/libs/chroma-js/2.1.0/chroma.min.js"></script>

    <!-- CSS Styling -->
    <style>
        #map {{
            height: 600px;
        }}
        .info {{
            background-color: white;
            padding: 10px;
            border-radius: 4px;
            opacity: 0.8;
        }}
        .legend {{
            line-height: 18px;
            color: #555;
        }}
        .legend i {{
            width: 18px;
            height: 18px;
            float: left;
            margin-right: 8px;
            opacity: 0.7;
        }}
    </style>
</head>
<body style='font-family: Verdana'>
    <div style='text-align: center;'>
        <h1>Supplemental Payment Proposals Analysis</h1>
        <p style='font-size: 14px; font-style: italic;'>A. Pena  |  Texas AFT  |  June 29, 2023</p>
    </div>
    <div id="map"></div>

    <script>
        // Initialize the map
        var map = L.map('map').setView([31.9686, -99.9018], 6);

        // Add a base map layer
        L.tileLayer('https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png', {{
            attribution: '&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a> contributors'
        }}).addTo(map);

        // Define the color scale
        var colorScaleExperience = chroma.scale('YlOrRd').mode('lch').domain([0, 100], 'quantiles');
        var colorScaleEnrollment = chroma.scale(['red', 'blue']).domain([0, 20000], 'quantiles');

        // Load the GeoJSON data
        var data = {json.dumps(geojson_data)};

        // Function to handle mouseover event
        function highlightFeature(e) {{
            var layer = e.target;

            layer.setStyle({{
                weight: 2,
                color: '#666',
                dashArray: '',
                fillOpacity: 0.9,
                smoothFactor: 0,
            }});

            if (!L.Browser.ie && !L.Browser.opera && !L.Browser.edge) {{
                layer.bringToFront();
            }}

            info.update(layer.feature.properties);
        }}

        // Function to handle mouseout event
        function resetHighlight(e) {{
            var layer = e.target;
            if (map.hasLayer(geojsonEnrollment)) {{
                layer.setStyle(styleEnrollment(layer.feature));
            }} else {{
                layer.setStyle(styleExperience(layer.feature));
            }}
            info.update();
        }}

        // Function to zoom to district on click
        function zoomToFeature(e) {{
            map.fitBounds(e.target.getBounds());
        }}

        // Function to assign event handlers to features
        function onEachFeature(feature, layer) {{
            layer.on({{
                mouseover: highlightFeature,
                mouseout: resetHighlight,
                click: zoomToFeature
            }});
        }}

        // Control that shows district info on hover
        var info = L.control({{position: 'topright'}});

        info.onAdd = function (map) {{
            this._div = L.DomUtil.create('div', 'info'); // create a div with a class "info"
            this.update();
            return this._div;
        }};

        // Method that we will use to update the control based on feature properties passed
        info.update = function (props) {{
            var layerContent = '';
            if (props) {{
                layerContent += '<span><b>' + props.NAME + '</b></span><br />';
                if (map.hasLayer(geojsonEnrollment)) {{
                    layerContent += props.enrollment ? 'Total Enrollment as of 10/2022: <br /><span>' + props.enrollment + '</span><br />' : '';
                }} else {{
                    layerContent += props.experience_percentage ? '% of Teachers With 6+ Years of Experience: <br /><span>' + props.experience_percentage + ' %</span><br />' : '';
                }}
            }}
            layerContent = layerContent || 'Hover over a district';
            this._div.innerHTML = '<h4>TX School District:</h4>' + layerContent;
        }};

        info.addTo(map);

        // Define function for enrollment-based color scale
        function getColorEnrollment(d) {{
            return d > 20000 ? 'blue' : 'red';
        }}

        // Define function for enrollment-based style
        function styleEnrollment(feature) {{
            return {{
                fillColor: getColorEnrollment(feature.properties.enrollment),
                weight: 0.5,
                opacity: 1,
                color: 'white',
                dashArray: '',
                fillOpacity: 0.7,
                smoothFactor: 0,
            }};
        }}

        // Define function for experience-based style
        function styleExperience(feature) {{
            return {{
                fillColor: colorScaleExperience(feature.properties.experience_percentage).hex(),
                weight: 0.5,
                color: 'black',
                fillOpacity: 0.7,
                smoothFactor: 0
            }};
        }}

        // Add the GeoJSON layer
        var geojson = L.geoJson(data, {{
            style: styleExperience,
            onEachFeature: onEachFeature
        }});

        // Add the enrollment-based GeoJSON layer
        var geojsonEnrollment = L.geoJson(data, {{
            style: styleEnrollment,
            onEachFeature: onEachFeature
        }});

        // Create layer control
        var baseLayers = {{
            "Teacher Experience": geojson,
            "Student Enrollment": geojsonEnrollment
        }};

        var overlayLayers = {{
            "Districts": geojson
        }};

        var layerControl = L.control.layers(baseLayers, overlayLayers, {{collapsed: false}});
        layerControl.addTo(map);

        // Activate the experience-based layer by default
        geojson.addTo(map);

    </script>
</body>
</html>

""")
