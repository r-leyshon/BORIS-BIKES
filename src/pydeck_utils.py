"""Visualisation with pydeck."""
import pydeck as pdk
import geopandas as gpd


def make_scatter_deck(
    gdf: gpd.GeoDataFrame, radius="(n_stations_norm * 25) + 20"
) -> pdk.Deck:
    """Render a scatterPlotLayer of travel time & number of stations serving.

    Intended for use with output of ./src/tt-london-bikes.py ->
    ./data/interim/median_travel_times.pkl.

    Parameters
    ----------
    gdf : gpd.GeoDataFrame
        Table of grid locations and travel time from station locations.
    radius : str, optional
        A valid pydeck get_radius expression, by default
        "(n_stations_norm * 25) + 20"

    Returns
    -------
    pdk.Deck
        A rendered interactive map.

    """
    if not isinstance(gdf, gpd.GeoDataFrame):
        raise TypeError(f"gdf expected gpd.GeoDataFrame, found {type(gdf)}")
    expected_cols = [
        "n_stations_serving",
        "listed_geom",
        "inverted_med_tt",
        "median_tt",
    ]
    coldiff = set(gdf.columns).diff(expected_cols)
    if coldiff:
        raise AttributeError(f"Required column names are absent: {coldiff}")
    # TODO: Expose more params in func signature
    gdf = gdf.rename(columns={"n_stations_serving": "n_stats"})
    layer = pdk.Layer(
        "ScatterplotLayer",
        gdf,
        pickable=True,
        opacity=0.2,
        stroked=True,
        filled=True,
        radius_scale=6,
        radius_min_pixels=1,
        radius_max_pixels=100,
        line_width_min_pixels=1,
        get_position="listed_geom",
        get_radius=radius,
        get_fill_color="[255,(inverted_med_tt * 255), (median_tt * 255)]",
        get_line_color="[0,0,0,0]",
    )
    # Set the viewport location
    view_state = pdk.ViewState(
        longitude=-0.110,
        latitude=51.518,
        zoom=10,
        min_zoom=5,
        max_zoom=15,
        pitch=40.5,
        bearing=-27.36,
    )

    tooltip = {
        "text": "Stations serving: {n_stats}\nMdn travel time: {median_tt}"
    }
    # Render
    r = pdk.Deck(
        layers=[layer], initial_view_state=view_state, tooltip=tooltip
    )
    return r
