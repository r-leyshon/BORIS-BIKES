"""Carry out routing with r5py and save outputs to data/interim.

JDK dependency to run the routing.
"""
import datetime

import geopandas as gpd
import pandas as pd
import r5py
from pyprojroot import here

from src.grid import create_point_grid
from src.gpd_utils import get_median_tts_for_all_stations


# TODO: This script relies on openJDK to do the routing with r5. It would be
# better to serve a docker container with all dependencies pre-installed.

point_plane = create_point_grid(
    [-0.5510579, 51.3332786, 0.297936, 51.725836], stepsize=1000
)
# station point data
london_bike_stations = pd.read_pickle(here("data/interim/bike_stations.pkl"))
station_gdf = gpd.GeoDataFrame(london_bike_stations, crs=4326)
station_gdf["listed_geom"] = [[c.x, c.y] for c in station_gdf["geometry"]]
del london_bike_stations


# Carry out the routing
transport_network = r5py.TransportNetwork(here("data/external/london.osm.pbf"))
travel_time_matrix = r5py.TravelTimeMatrixComputer(
    transport_network,
    origins=station_gdf,
    destinations=point_plane,
    transport_modes=[r5py.TransportMode.BICYCLE],
    departure=datetime.datetime(2023, 1, 22, 8, 0, 0),  # 9am on a Monday
    departure_time_window=datetime.timedelta(minutes=10),  # depart every...
    snap_to_network=True,
    # doesn't work for all points, TODO: snap to nearest vertex in road
    # network where auto snapping failed. TODO: Report haversine distance
    # to snapped location.
    max_time=datetime.timedelta(minutes=30),  # journeys <= 30 mins
).compute_travel_times()

med_tts = get_median_tts_for_all_stations(
    stations=station_gdf, tt_matrix=travel_time_matrix, pp=point_plane
)

station_gdf.to_pickle(here("data/interim/station_gdf.pkl"))
med_tts.to_pickle(here("data/interim/median_travel_times.pkl"))
