import ee
import os
import geopandas
import geemap.foliumap as geemap
from geemap import geojson_to_ee, ee_to_geojson
import streamlit as st
from streamlit_folium import folium_static

def authenticate():
    ee.Authenticate()
    ee.Initialize (project='ee-wildfire-celtics')

authenticate()

st.set_page_config(layout="wide")

st.header("Brazil Wildfire Analysis")


brazil_shapefile = geemap.shp_to_ee('data/Brazil.shp')

col1, col2, col3 = st.columns(3)

with col1:
    st.subheader("Burned Area")
    Map = geemap.Map()

    # Define the dataset and filter by date
    dataset = ee.ImageCollection('MODIS/061/MCD64A1').filter(ee.Filter.date('2017-01-01', '2018-05-01'))
    burnedArea = dataset.select('BurnDate')

    # A FeatureCollection defining Brazil boundary.
    fc = ee.FeatureCollection('USDOS/LSIB_SIMPLE/2017').filter(
        'country_na == "Brazil"'
    )

    # Clip the burned Area by the Brazil boundary FeatureCollection.
    # Iterate over the ImageCollection and clip each image to the FeatureCollection.
    ba_clip = burnedArea.map(lambda img: img.clipToCollection(fc))


    # Visualization parameters
    burnedAreaVis = {
        'min': 30.0,
        'max': 341.0,
        'palette': ['4e0400', '951003', 'c61503', 'ff1901']
    }

    # Create a map
    Map = geemap.Map(center=[-10, -55], zoom=4)

    # Add burned area layer to the map
    Map.addLayer(ba_clip, burnedAreaVis, 'Burned Area')
    Map.addLayer(brazil_shapefile, name='Brazil',opacity=0.5)
    Map.addLayerControl()

    Map.to_streamlit()

with col2:
    st.subheader("Land Cover")
    Map = geemap.Map()

    landcover = ee.Image('MODIS/006/MCD12Q1/2004_01_01').select('LC_Type1')

    igbpLandCoverVis = {
        'min': 1.0,
        'max': 17.0,
        'palette': [
            '05450a',
            '086a10',
            '54a708',
            '78d203',
            '009900',
            'c6b044',
            'dcd159',
            'dade48',
            'fbff13',
            'b6ff05',
            '27ff87',
            'c24f44',
            'a5a5a5',
            'ff6d4c',
            '69fff8',
            'f9ffa4',
            '1c0dff',
        ],
    }

    brazil_lc = landcover.clip(brazil_shapefile)
    Map.setCenter(-55, -10, 4)
    Map.addLayer(brazil_lc, igbpLandCoverVis, 'MODIS Land Cover')
    Map.addLayerControl()
    Map.to_streamlit()