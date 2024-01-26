import pandas as pd
import geopandas as gpd
from sklearn import preprocessing


def get_median_tts_for_all_stations(
    stations:gpd.GeoDataFrame, tt_matrix:pd.DataFrame, pp:gpd.GeoDataFrame
    ) -> gpd.GeoDataFrame:
    """Joins travel times & medians to point geometries.

    Station locations are presumed to be origins. Points in the point plane are
    presumed to be destinations. Station geometry is dropped.

    Parameters
    ----------
    stations : gpd.GeoDataFrame
        Locations of stations.
    tt_matrix : pd.DataFrame
        Matrix of travel times where `from_id` are stations and `to_id` are
        points in the point plane.
    pp : gpd.GeoDataFrame
        Locations in the point plane.

    Returns
    -------
    gpd.GeoDataFrame
        Point plane locations with median travel times from stations and number
        of stations serving each point. A number of features are added to
        assist in mapping.

    """
    # TODO: Defensive checks & Unit tests
    # get median travel time from all stations:
    med_tts = tt_matrix.groupby("to_id")["travel_time"].median()
    # get number of stations serving each point in the grid
    tt_dropna = tt_matrix.dropna()
    n_stations = tt_dropna.groupby("to_id")["from_id"].count()
    df = pp.join(med_tts).join(n_stations)
    df = df.rename(
        columns={"travel_time": "median_tt", "from_id": "n_stations_serving"})
    # need integer for n_stations_serving but there are NaNs
    bool_ind = df["n_stations_serving"].isna()
    df.loc[bool_ind, "n_stations_serving"] = 0.0
    df["n_stations_serving"] = df["n_stations_serving"].astype("int16")
    # feature engineering for pydeck
    x = df["n_stations_serving"].values.reshape(-1, 1)
    min_max_scaler = preprocessing.MinMaxScaler()
    x_scaled = min_max_scaler.fit_transform(x)
    df["n_stations_norm"] = pd.Series(x_scaled.flatten())
    out_gdf = gpd.GeoDataFrame(df, crs=4326)
    out_gdf["listed_geom"] = [[c.x, c.y] for c in out_gdf["geometry"]]
    out_gdf["inverted_med_tt"] = (
        max(out_gdf["median_tt"].dropna()) - out_gdf["median_tt"]
        ) * 0.1
    
    return out_gdf
