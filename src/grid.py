"""Create a grid over a defined bbox. Created at desired granularity.

Useful for routing purposes.
"""
import shapely.geometry
import pyproj
import pandas as pd
import geopandas as gpd


def create_point_grid(bbox_list: list, stepsize: int) -> gpd.GeoDataFrame:
    """Create a metric point plane for a given bounding box.

    Return a geodataframe of evenly spaced points for a specified bounding box.
    Distance between points is controlled by stepsize in metres.  As
    an intermediate step requires transformation to epsg:27700, the calculation
    of points is suitable for GB only.

    Parameters
    ----------
    bbox_list : list
        A list in xmin, ymin, xmax, ymax order. Expected to be in epsg:4326.
        Use https://boundingbox.klokantech.com/ or similar to export a bbox.
    stepsize : int
        Spacing of grid points in metres. Must be larger than zero.

    Returns
    -------
    gpd.GeoDataFrame
        GeoDataFrame in epsg:4326 of the point locations.

    Raises
    ------
    TypeError
        bbox_list is not type list.
        Coordinates in bbox_list are not type float.
        step_size is not type int.
    ValueError
        bbox_list is not length 4.
        xmin is greater than or equal to xmax.
        ymin is greater than or equal to ymax.
        step_size is not a positive integer.

    """
    # defensive checks
    if not isinstance(bbox_list, list):
        raise TypeError(f"bbox_list expects a list. Found {type(bbox_list)}")
    if not len(bbox_list) == 4:
        raise ValueError(f"bbox_list expects 4 values. Found {len(bbox_list)}")
    for coord in bbox_list:
        if not isinstance(coord, float):
            raise TypeError(
                f"Coords must be float. Found {coord}: {type(coord)}"
            )
    # check points are ordered correctly
    xmin, ymin, xmax, ymax = bbox_list
    if xmin >= xmax:
        raise ValueError(
            "bbox_list value at pos 0 should be smaller than value at pos 2."
        )
    if ymin >= ymax:
        raise ValueError(
            "bbox_list value at pos 1 should be smaller than value at pos 3."
        )
    if not isinstance(stepsize, int):
        raise TypeError(f"stepsize expects int. Found {type(stepsize)}")
    if stepsize <= 0:
        raise ValueError("stepsize must be a positive integer.")

    # Set up crs transformers. Need a planar crs for work in metres - use BNG
    planar_transformer = pyproj.Transformer.from_crs(4326, 27700)
    geodetic_transformer = pyproj.Transformer.from_crs(27700, 4326)
    # bbox corners
    sw = shapely.geometry.Point((xmin, ymin))
    ne = shapely.geometry.Point((xmax, ymax))
    # Project corners to planar
    planar_sw = planar_transformer.transform(sw.x, sw.y)
    planar_ne = planar_transformer.transform(ne.x, ne.y)
    # Iterate over metric plane
    points = []
    x = planar_sw[0]
    while x < planar_ne[0]:
        y = planar_sw[1]
        while y < planar_ne[1]:
            p = shapely.geometry.Point(geodetic_transformer.transform(x, y))
            points.append(p)
            y += stepsize
        x += stepsize
    df = pd.DataFrame({"geometry": points, "id": range(0, len(points))})
    gdf = gpd.GeoDataFrame(df, crs=4326)
    return gdf
