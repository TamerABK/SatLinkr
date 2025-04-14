import math
import folium
from folium.plugins import HeatMap
from datetime import datetime
import sys
import os
sys.path.append(os.path.join(os.getcwd(),"static","bin","filter"))
from static.bin.filter.filterSWPR import *
import numpy as np


def generate_map(lat,long,radius,gas_data):
    m = folium.Map(
        location=[lat, long],
        zoom_start=12,
        tiles="CartoDB dark_matter",  
        control_scale=True,      
    )

    if gas_data!=[]:    
        # Convert numpy.float32 values to standard Python float
        gas_data = [[float(x[0]), float(x[1]), float(x[2])] for x in gas_data]
        
        # Get the maximum ppm value for normalization
        max_ppm = math.ceil(max([x[2] for x in gas_data ]))
        min_ppm=math.floor(min([x[2] for x in gas_data ] ))

        # Define the extended gradient for the ppm levels
        gradient = {
            "0.0": "#0000FF",    # Blue (350 ppm)
            "0.2": "#00FF00",    # Green (380 ppm)
            "0.3": "#FFFF00",    # Yellow (400 ppm)
            "0.5": "#FFA500",    # Orange (450 ppm)
            "0.7": "#FF0000",    # Red (500 ppm)
            "0.99": "#8B0000",    # Dark Red (550 ppm)
            "1.0": "#800080"     # Purple (600 ppm)
        }

        # Normalize the ppm values and map them to the gradient
        # Normalize gas data ppm values to be between 0 and 1 based on the max_ppm
        normalized_gas_data = [
            [x[0], x[1], (x[2]-min_ppm) / (max_ppm-min_ppm)  ] for x in gas_data if x[2] != -999.0 
        ]

        # Add Heatmap layer to the map with customized extended gradient
        HeatMap(normalized_gas_data, 
                radius=5, 
                blur=0.1, 
                min_opacity=0.5,
                max_zoom=100,
                gradient=gradient
        ).add_to(m)

        folium.Circle(
            location=[lat, long],  # Center of the circle
            radius=1000*radius,  # Radius in meters
            color='black',  # Circle color
        ).add_to(m)
        
        step = (max_ppm - min_ppm) / 7
        sc=min_ppm
        scale=""
    
        while(sc<max_ppm):
            if step < 1 and sc <100:
                tp=round(sc,1)
            else:
                tp=round(sc)

            scale+=f"<span>{tp}</span>"
            sc+=step
        print(gas_data)
        # Adding a legend for the map
        legend_html = f"""
        <div style="
            position: absolute;
            top: 10px;
            right: 10px;
            width: 220px;
            height: 100px;
            background-color: white;
            border: 2px solid grey;
            z-index:9999;
            font-size:14px;
            padding: 10px;
            text-align: center;
            box-shadow: 2px 2px 5px rgba(0,0,0,0.3);
        ">
            <b>Gas Concentration Levels (ppm)</b><br>
            <div style="
                width: 100%;
                height: 20px;
                background: linear-gradient(to right, #0000FF, #00FF00, #FFFF00, #FFA500, #FF0000, #8B0000);
                margin-top: 5px;
            "></div>
            <div style="display: flex; justify-content: space-between; font-size: 12px; margin-top: 2px;">
                {scale}
            </div>
        </div>
        """

        # Add the legend to the map using Element
        m.get_root().html.add_child(folium.Element(legend_html))

    folium.TileLayer('Esri.WorldImagery').add_to(m) 
    return m._repr_html_()  # Return HTML representation of the map
