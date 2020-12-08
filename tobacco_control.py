import streamlit as st
import pandas as pd
import altair as alt
import json
import requests
import numpy as np
from IPython.display import display, HTML
from altair import datum



####### Datasets

control_dataset = 'https://raw.githubusercontent.com/JulioCandela1993/VisualAnalytics/master/data/control_policy.csv'
deaths_dataset = 'https://raw.githubusercontent.com/JulioCandela1993/VisualAnalytics/master/data/deaths.csv'

####### Dashboard

st.title("Tobacco: a silent killer")


st.header("How are countries controlling Tobacco consumption?")

'''
The following analysis is based on the evaluation made by World Health Organization (WHO) 
to country policies against Tobacco. A score from 1 to 5 is assigned depending on the intensity 
of a country to deal with Tobacco issues being 1 the worst and 5 the best
'''

####### Control Measures given by WHO

control_metrics = ["Monitor",	
           "Protect from tobacco smoke",	
           "Offer help to quit tobacco use", 
           "Warn about the dangers of tobacco",
           "Enforce bans on tobacco advertising",
           "Raise taxes on tobacco",
           "Anti-tobacco mass media campaigns"
]

container_map = st.beta_container()
with container_map:

    cols = st.selectbox('Select control measure: ', control_metrics)
    
    if cols in control_metrics:   
        metric_to_show_in_covid_Layer = cols +":Q"
        metric_name = cols
       
    years = ['2008', '2010', '2012', '2014', '2016', '2018']
    columns_year = [metric_name+" "+str(year) for year in years]
    columns = ["d" +str(year) for year in years]
    
    st.header("A global view of the implementation of control policies around the world")

    '''
    In the folling map, we can identify the intensity of a specific control policy for each country. 
    We can also see the evolution of these policies from 2008 to 2018
    '''




####### Map Visualization


url_topojson = 'https://raw.githubusercontent.com/JulioCandela1993/VisualAnalytics/master/world-countries.json'
data_topojson_remote = alt.topo_feature(url=url_topojson, feature='countries1')

select_year = st.slider('Select period: ', 2008, 2018, 2008, step = 2)

map_geojson = alt.Chart(data_topojson_remote).mark_geoshape(
    stroke="black",
    strokeWidth=1,
    fill='lightgray'
).encode(
    color=metric_to_show_in_covid_Layer,
).transform_lookup(
        lookup="properties.name",
        from_=alt.LookupData(control_dataset, "Country", [metric_name,"Year"])
).properties(
    width=800,
    height=400
)
      
choro = alt.Chart(data_topojson_remote).mark_geoshape(
    stroke='black'
).encode(
    color=metric_to_show_in_covid_Layer,
            tooltip=[
                alt.Tooltip("properties.name:O", title="Country name"),
                alt.Tooltip(metric_to_show_in_covid_Layer, title=metric_name),
                alt.Tooltip("year:Q", title="Year"),
            ],
).transform_calculate(
    d2008 = "1",
    d2010 = "1",
    d2012 = "1",
    d2014 = "1",
    d2016 = "1",
    d2018 = "1"
).transform_fold(
    columns, as_=['year', 'metric']
).transform_calculate(
    yearQ = 'replace(datum.year,"d","")'
).transform_calculate(
    key_val = 'datum.properties.name + datum.yearQ'
).transform_lookup(
        lookup="key_val",
        from_=alt.LookupData(control_dataset, "ID", [metric_name,"Year"])
).transform_calculate(
    year='parseInt(datum.Year)',
).transform_filter(
    alt.FieldEqualPredicate(field='year', equal=select_year)
)

with container_map:
    st.altair_chart(map_geojson + choro)



####### Scatterplot control policy vs deaths

st.header("Are control policies effective?")

'''
Countries have implemented different control policies against Tobacco which have been measured by WHO from 2008 until 2018. 
During this period, some countries have strengthen their policies; however, we don't know the real impact of them in the quality 
of citizen's life.

As a consequence, we have developed the next visualization to measure the efficiency of each change in control policies with 
respect to the change in deaths because of Smoking. We consider "change" as the percentage of variation
between 2008 and 2016. The user can also select brush the histograms in order to filter the points and 
evaluate the slope of the regression in more detail (with groups that increased more or less the efforts in control policies, for example)

An increase in the efforts of a control policy should be reflected in a decrease in the number of deaths as part of 
the efficiency of the control measure

'''

brush = alt.selection_interval()

base_scatter = alt.Chart(control_dataset).transform_lookup(
        lookup="ID",
        from_=alt.LookupData(deaths_dataset, "ID", ["deaths","Year"])
).transform_calculate(
    deaths='parseFloat(datum.deaths)',
    year='parseInt(datum.Year)',
    metric = alt.datum[metric_name]
).transform_calculate(
    deaths_2016='datum.year==2016?datum.deaths:0',
    deaths_2008='datum.year==2008?datum.deaths:0',
    metric_2016='datum.year==2016?datum.metric:0',
    metric_2008='datum.year==2008?datum.metric:0',
    year='parseInt(datum.Year)',
).transform_aggregate(
    deaths_2016='sum(deaths_2016)',
    metric_2016='sum(metric_2016)',
    deaths_2008='sum(deaths_2008)',
    metric_2008='sum(metric_2008)',
    groupby=["Country"]
).transform_calculate(
    incr_ratio_deaths='((datum.deaths_2016/datum.deaths_2008)-1)*100',
    incr_ratio_metric='((datum.metric_2016/datum.metric_2008)-1)*100',
)

xscale = alt.Scale(domain=(-100, 400))
yscale = alt.Scale(domain=(-100, 200))

# area_args = {'opacity': .3, 'interpolate': 'step'}

points_scatter = base_scatter.mark_circle().encode(
    alt.X('incr_ratio_metric:Q', scale = xscale, title = '% change of efforts in ' + metric_name + ' from 2008 to 2016'),
    alt.Y('incr_ratio_deaths:Q', scale=yscale, title = '% change in deaths from 2008 to 2016'),
    #color=alt.condition(brush, alt.value('blue'), alt.value('lightgray')),  
    
    #opacity=alt.condition(brush, alt.value(0.75), alt.value(0.05)),
    tooltip=[
                alt.Tooltip("Country:N", title="Country"),
            ],
).properties(
    width=600,
    height=400
).transform_filter(brush)   
    
regression_scatter = points_scatter.transform_regression(
        on='incr_ratio_metric', regression='incr_ratio_deaths'#, method = 'log'
).mark_line(color='orange')

scatter_final = (points_scatter + regression_scatter)
    
top_hist = base_scatter.mark_area().encode(
    alt.X("incr_ratio_metric:Q",
          bin=alt.Bin(maxbins=10, extent=xscale.domain),
          title=''
          ),
    alt.Y('count()', title='N° Countries'),
    #alt.Color('Country:N'),
).add_selection(
    brush
).properties(width=600 , height=80)

right_hist = base_scatter.mark_area().encode(
    alt.Y('incr_ratio_deaths:Q',
          bin=alt.Bin(maxbins=20, extent=yscale.domain),
          title='',
          ),
    alt.X('count()', title='N° Countries'),
    #alt.Color('species:N'),
).add_selection(
    brush
).properties(width=100, height=400)


st.altair_chart(top_hist & (scatter_final |right_hist ))


# st.altair_chart(right_hist)
# st.altair_chart(points)
#st.altair_chart(top_hist & (points | right_hist))























#st.header("Evolution of awareness in countries with highest deaths because of Smoking")

# circle_countries = alt.Chart(control_dataset).mark_circle(
#     opacity=0.8,
#     stroke='black',
#     strokeWidth=1
# ).encode(
#     alt.X('Year:O', axis=alt.Axis(labelAngle=0)),
#     alt.Y('Country:N', sort=alt.Sort(field="rank", order="descending")),
#     alt.Size(metric_to_show_in_covid_Layer,
#         scale=alt.Scale(range=[1, 1000]),
#         legend=alt.Legend(title=metric_name)
#     ),
#     alt.Color('Country:N', legend=None)
# ).properties(
#     width=800,
#     height=600
# ).transform_lookup(
#         lookup="Country",
#         from_=alt.LookupData(deaths_dataset, "Country", ["deaths"])
# ).transform_calculate(
#     deaths='parseFloat(datum.deaths)',
# ).transform_window(
#     rank='rank(deaths)',
#     sort=[alt.SortField('deaths', order='descending')]
# ).transform_filter(
#     (alt.datum.rank < 60)
# )

#st.altair_chart(circle_countries)

####### HeatMap Visualization: Measure by Deaths num


# rect_countries = alt.Chart(control_dataset).mark_rect(
# ).encode(
#     alt.X('Year:O'),
#     alt.Row('Country:N'),
#     alt.Color(metric_to_show_in_covid_Layer, scale=alt.Scale(scheme='greenblue'), legend=alt.Legend(orient='bottom'))
# ).properties(
#     width=400,
#     height=500
# ).transform_lookup(
#         lookup="ID",
#         from_=alt.LookupData(deaths_dataset, "ID", ["deaths"])
# ).transform_calculate(
#     deaths='parseFloat(datum.deaths)',
# ).transform_window(
#     rank='rank(deaths)',
#     sort=[alt.SortField('deaths', order='descending')]
# ).transform_filter(
#     (alt.datum.rank < 60)
# )
    
    
# circ_countries = rect_countries.mark_point().encode(
#     alt.ColorValue('grey'),
#     alt.Size('deaths:Q',
#         legend=alt.Legend(title='Number of Deaths because of Smoking', orient='bottom')
#     )
# )

# area_countries = rect_countries.mark_area().encode(
#     alt.Y('deaths:Q'),
#     alt.Row('Country:N')
# )

# st.altair_chart(rect_countries + area_countries)
