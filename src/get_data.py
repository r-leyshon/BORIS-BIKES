"""Ingest osm & station location data."""
import subprocess

from pyprojroot import here
import requests
import pandas as pd
import geopandas as gpd

def get_input_data():
    """Ingest all required inputs.

    Downloads London osm cut and bike station locations and writes to data
    folder.

    Raises
    ------
    requests.exceptions.HTTPError
        HTTP error encountered when querying TfL RESTapi.

    Returns
    -------
    None
        Run module from command line, used for side effects.
    """

    # get the London cut of the osm for building trans net
    subprocess.run(
        [
            "curl",
            "https://download.bbbike.org/osm/bbbike/London/London.osm.pbf",
            "-o",
            here("data/external/london.osm.pbf")
            ])
    # get the bike station locs, TODO - modularise this & run as an integration
    # test with a pytest.mark. Can build that into an end to end test later.
    ENDPOINT = "https://api.tfl.gov.uk/BikePoint/"
    # todo using http adapter, add retry strategy & user agent for more robust
    # request. Add in parameters requesting json format & pagination if needed.
    resp = requests.get(ENDPOINT)
    if resp.ok:
        content = resp.json()
    else:
        raise requests.exceptions.HTTPError(
            f"{resp.status_code}: {resp.reason}")

    needed_keys = ["id", "commonName", "lat", "lon"]
    all_stations = list()
    for i in content:
        node_dict = dict()
        for k,v in i.items():
            if k in needed_keys:
                node_dict[k] = v
        all_stations.append(node_dict)

    stations = pd.DataFrame(all_stations)
    stations_gdf = gpd.GeoDataFrame(
        stations, geometry=gpd.points_from_xy(stations["lon"], stations["lat"]),
        crs=4326)
    stations_gdf.to_pickle(here("data/interim/bike_stations.pkl"))

if __name__ == "__main__":
    get_input_data()
