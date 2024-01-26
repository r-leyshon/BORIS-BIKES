import pydeck as pdk
import pandas as pd


def make_scatter_deck(
    df:pd.DataFrame, radius="(n_stations_norm * 25) + 20") -> pdk.Deck:
    # TODO: Defensive checks
    # TODO: Expose params in func signature
    df = df.rename(columns={"n_stations_serving": "n_stats"})
    layer = pdk.Layer(
        "ScatterplotLayer",
        df,
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
        "text": "Stations serving: {n_stats}\nMdn travel time: {median_tt}"}
    # Render
    r = pdk.Deck(
        layers=[layer], initial_view_state=view_state, tooltip=tooltip)
    return r