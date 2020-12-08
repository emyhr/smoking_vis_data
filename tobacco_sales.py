import altair as alt
import streamlit as st
import pandas as pd
import numpy as np

sales_data = pd.read_csv('data/sales-of-cigarettes-per-adult-per-day.csv',
                    header=0,
                    names=[
                        'Country',
                        'Code',
                        'Year',
                        'NumCig'
                    ],
                    dtype={'Country': str,
                            'Code': str,
                            'Year': 'Int64',
                            'NumCig': 'float64'})

sales_minyear = sales_data.loc[:, 'Year'].min()
sales_maxyear = sales_data.loc[:, 'Year'].max()

container = st.beta_container()
with container:
    st.header('Tobacco sales trend in different countries')
    '''
    This chart below shows average number of cigarettes sold per day in a particular country.
    For example, in 1980 in France, people used to buy on average 6 cigarettes per day.
    '''
    sales_bycountry = st.multiselect('Select countries to plot',
                           sales_data.groupby('Country').count().reset_index()['Country'].tolist(),
                           default=['France', 'Germany', 'Spain'])


slider = st.slider('Select a period to plot', int(str(sales_minyear)), int(str(sales_maxyear)), (1980, 2000))
sales_chart = alt.Chart(sales_data, height=500, width=700,
title='Average number of cigarettes sold daily during chosen period of time').mark_line().encode(
alt.X('Year', axis=alt.Axis(title='Years', tickCount=5)),
alt.Y('NumCig', axis=alt.Axis(title='Avg daily sales of cigarretes')),
alt.Color('Country')
).transform_filter(
    {'and': [{'field': 'Country', 'oneOf': sales_bycountry},
            {'field': 'Year', 'range': slider}]}
    )
with container:

    st.altair_chart(sales_chart)
