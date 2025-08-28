import math
import folium
from folium.plugins import HeatMap
from datetime import datetime
import sys
import os
sys.path.append(os.path.join(os.getcwd(),"static","bin","filter"))
from static.bin.filter.filterSWPR import *
import numpy as np
import matplotlib.colors as mcolors






def get_color(value, gradient):
    stops = sorted((float(k), v) for k, v in gradient.items())
    for i, (stop, color) in enumerate(stops):
        if value <= stop:
            if i == 0:
                return color
            prev_stop, prev_color = stops[i-1]
            ratio = (value - prev_stop) / (stop - prev_stop)
            prev_rgb = np.array(mcolors.to_rgb(prev_color))
            curr_rgb = np.array(mcolors.to_rgb(color))
            interp_rgb = prev_rgb * (1 - ratio) + curr_rgb * ratio
            return mcolors.to_hex(interp_rgb)
    return stops[-1][1]

def generate_map(lat, long, radius, gas_data, scale_title, mode='heatmap'):
    heat_gradient = {
        "0.0": "#0000FF",
        "0.2": "#00FF00",
        "0.3": "#FFFF00",
        "0.5": "#FFA500",
        "0.7": "#FF0000",
        "0.99": "#8B0000",
        "1.0": "#800080"
    }

    square_gradient = {
        0.0: "#0000FF",
        0.2: "#00FF00",
        0.3: "#FFFF00",
        0.5: "#FFA500",
        0.7: "#FF0000",
        0.99: "#8B0000",
        1.0: "#8B0000"
    }

    m = folium.Map(
        location=[lat, long],
        zoom_start=12,
        min_zoom=4,
        max_zoom=18,
        tiles="CartoDB dark_matter",
        control_scale=True,
    )

    if gas_data != []:
        gas_data = [[float(x[0]), float(x[1]), float(x[2])] for x in gas_data]
        max_ppm = math.ceil(max([x[2] for x in gas_data]))
        min_ppm = math.floor(min([x[2] for x in gas_data]))



        if mode == 'heatmap':
            normalized_gas_data = [
                [x[0], x[1], (x[2]-min_ppm) / (max_ppm-min_ppm)] for x in gas_data if x[2] != -999.0
            ]
            HeatMap(normalized_gas_data,
                    radius=5,
                    blur=0.1,
                    min_opacity=0.5,
                    max_zoom=100,
                    gradient=heat_gradient
            ).add_to(m)

            folium.Circle(
                location=[lat, long],
                radius=1000 * radius,
                color='black',
            ).add_to(m)

        elif mode == 'squares':
            for x in gas_data:
                lat_c, lon_c, ppm = x
                if ppm == -999.0:
                    continue

                try:
                    norm = (ppm - min_ppm) / (max_ppm - min_ppm)
                    norm = max(0.0, min(1.0, norm))
                except ZeroDivisionError:
                    norm = ppm


                color = get_color(norm, square_gradient)
                bounds = [
                    [lat_c - 0.5, lon_c - 0.5],
                    [lat_c + 0.5, lon_c + 0.5]
                ]
                folium.Rectangle(
                    bounds=bounds,
                    color=color,
                    fill=True,
                    weight=2,
                    fill_color=color,
                    fill_opacity=0.5,
                    popup=f"{ppm}"
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
        # Adding a legend for the map
        legend_html = f"""
        <div style="
            position: absolute;
            top: 10px;
            right: 10px;
            width: 240px;
            height: fit-content;
            background-color: white;
            border: 2px solid grey;
            z-index:9999;
            font-size:14px;
            padding: 10px;
            text-align: center;
            box-shadow: 2px 2px 5px rgba(0,0,0,0.3);
        ">
            <b>{scale_title}</b><br>
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
