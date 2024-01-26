import datetime

import geopandas as gpd
import pandas as pd
import r5py
from pyprojroot import here
import numpy as np
import pydeck as pdk
import contextily as ctx
import matplotlib.pyplot as plt
from shapely.geometry import Point, Polygon

from src.grid import create_point_grid
from src.gpd_utils import get_median_tts_for_all_stations
from src.pydeck_utils import make_scatter_deck

station_df = pd.read_pickle(here("data/interim/station_gdf.pkl"))
station_gdf = gpd.GeoDataFrame(station_df, crs=4326)
point_plane = create_point_grid(
    [-0.5510579, 51.3332786, 0.297936, 51.725836], stepsize=1000)
# first check that the boundary of the points plane is large enough to avoid
# edge effects with the station locations
bounding_box = point_plane.total_bounds
minx, miny, maxx, maxy = bounding_box
ax = station_gdf.plot(marker="o", color="red", alpha=0.5, markersize=10)
bbox_polygon = gpd.GeoSeries(
    [Polygon([(minx, miny), (minx, maxy), (maxx, maxy), (maxx, miny)])]
    )
bbox_polygon.plot(ax=ax, alpha=0.2, edgecolor="black")
ctx.add_basemap(ax,
               crs=station_gdf.crs.to_string(),
               source=ctx.providers.CartoDB.Positron
              )
plt.savefig(here("outputs/pointinpolygon.png"), dpi=500)

# pydeck visuals - concentration of charging stations by r500m hex
layer = pdk.Layer(
    "HexagonLayer",
    station_gdf,
    pickable=True,
    extruded=True,
    get_position="listed_geom",
    auto_highlight=True,
    elevation_scale=100,
    elevation_range=[0, 100],
    coverage=1,
    radius=250, # in metres, default is 1km
    colorRange=[
        [255,255,178,130],
        [254,217,118,130],
        [254,178,76,130],
        [253,141,60,130],
        [240,59,32,130],
        [189,0,38,130],
        ],
)
view_state = pdk.ViewState(
    longitude=-0.110,
    latitude=51.518,
    zoom=11,
    min_zoom=5,
    max_zoom=15,
    pitch=40.5,
    bearing=-27.36,
)
tooltip = {"html": "<b>n Stations:</b> {elevationValue}"}
r = pdk.Deck(layers=[layer], initial_view_state=view_state, tooltip=tooltip,
map_style=pdk.map_styles.LIGHT,
)
r.to_html(here("outputs/hex_layer.html"))

# travel times from stations to points in a point plane
med_tts = pd.read_pickle(here("data/interim/median_travel_times.pkl"))
med_tts = gpd.GeoDataFrame(med_tts, crs=4326)
r = make_scatter_deck(med_tts)
r.to_html(here("outputs/point_layer.html"))

# get the n most isolated points in the cyclable zone (by 30 mins)
n_isolated = med_tts.dropna().sort_values(
    ["median_tt", "n_stations_serving"],ascending=[False, False]
    ).head(20)
r = make_scatter_deck(n_isolated, radius=50)
r.to_html(here("outputs/isolated_point_layer.html"))
# TODO: Write a shiny application that selects the most isolated points in the
# commutable zone