"""Tests for pydeck_utils."""
import re

from shapely import Point
import geopandas as gpd
import pandas as pd
import pytest

from src.pydeck_utils import make_scatter_deck


class TestMakeScatterDeck(object):
    """Test make_scatter_deck."""

    def test_defensive_type_checks(self):
        """Check raises on TypeError."""
        with pytest.raises(
            TypeError,
            match="gdf expected gpd.GeoDataFrame, found <class 'int'>",
        ):
            make_scatter_deck(gdf=1)

    def test_defensive_column_checks(self):
        """Check raises if required cols are missing."""
        foo = pd.DataFrame({"geometry": [Point(0.1, 0.1)]})
        foo = gpd.GeoDataFrame(foo, crs=4326)
        with pytest.raises(
            AttributeError,
            match=re.escape(
                "Required column names are absent: ['inverted_med_tt',"
                " 'listed_geom', 'median_tt', 'n_stations_serving']"
            ),
        ):
            make_scatter_deck(foo)
