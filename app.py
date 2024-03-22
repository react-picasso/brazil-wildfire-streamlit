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

with st.container():
    import streamlit as st

    # List of Brazilian states
    states = ['Acre', 'Alagoas', 'Amapa', 'Amazonas', 'Bahia', 'Ceara', 'Espirito Santo', 'Goias', 'Maranhao', 
            'Mato Grosso', 'Minas Gerais', 'Para', 'Paraiba', 'Parana', 'Pernambuco', 'Piaui', 'Rio de Janeiro',
            'Rio Grande do Norte', 'Rio Grande do Sul', 'Rondonia', 'Roraima', 'Santa Catarina', 'Sao Paulo',
            'Sergipe', 'Tocantins']

    option = st.selectbox('Select a state', states)

    st.write('You selected:', option)

    # Apply custom CSS for styling
    st.markdown(
        """
        <style>
        .st-eb {
            background-color: #4CAF50;
            width: 45%;
            padding: 10px;
            margin: 10px;
            color: white;
            text-align: center;
            border-radius: 5px;
        }
        </style>
        """,
        unsafe_allow_html=True
    )

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

    with col3:
        from simpledbf import Dbf5

        dbf_file = 'data/Brazil.dbf'

        # Open the DBF file
        dbf = Dbf5(dbf_file)

        # Get the fields (columns) information
        fields = dbf.fields

        # Read the DBF file into a Pandas DataFrame
        df = dbf.to_dataframe()

        st.write(df['POP_EST'])
        st.write(df['POP_YEAR'])

with st.container():
    col3, col4 = st.columns(2)
    with col3:
        import plotly.express as px
        import pandas as pd

        df = pd.read_csv('Brazilian-fire-dataset.csv')
        selected_state = st.selectbox('Select State', df['State'].unique())
        start_date = st.date_input('Start Date')
        end_date = st.date_input('End Date')

        df['Date Reported'] = pd.to_datetime(df['Date Reported'])
        start_date = start_date.strftime('%Y-%m-%d')
        end_date = end_date.strftime('%Y-%m-%d')

        # Filter the DataFrame based on selected state and date range
        filtered_df = df[(df['State'] == selected_state) & (df['Date Reported'] >= start_date) & (df['Date Reported'] <= end_date)]

        # Create a bar graph for number of fires by month
        fig = px.bar(filtered_df, x='Month', y='Number of Fires', title=f'Number of Fires by Month in {selected_state} ({start_date} to {end_date})')


        # Display the bar graph
        st.plotly_chart(fig)
    
    with col4:
        # Filter the DataFrame based on the selected state
        filtered_df = df[df['State'] == selected_state]

        # Calculate the average number of fires by year
        avg_fires_by_year = filtered_df.groupby('Year')['Number of Fires'].mean().reset_index()

        # Create a bar graph for average number of fires by year
        fig = px.line(avg_fires_by_year, x='Year', y='Number of Fires', title=f'Average Number of Fires by Year in {selected_state}', line_shape='spline')

        # Display the bar graph
        st.plotly_chart(fig)

