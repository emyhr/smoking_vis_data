import altair as alt
import streamlit as st
import pandas as pd

st.title("Tobacco: a silent killer")

##########################################################
#############       smoking_deaths.py        #############
##########################################################

st.header("Smoking Deaths from 1990 to 2017")

'''
	Smoking has been seen as a critical factor leading to a death in the world. 
	These following charts give us an overview of smoking deaths in a country from 1990 to 2017. 
	First, you should select a specific country where you want to analyze. 
	The bottom-left chart not only shows the total number of deaths in all ages, but also gives us an interval selection tool to filter the data in a particular period of time.
	The top-left charts illustrates the normalized distribution of smoking deaths by ages.
	In the bar chart on the right, we can see how smoking ranks in the list of risk factors that lead to deaths in the chosen country in the chosen period of time.
'''

deaths = pd.read_csv('data/smoking-deaths-by-age.csv',
                    header=0,
                    names=[
                        'country',
                        'code',
                        'year',
                        '15 to 49',
                        '50 to 69',
                        'Above 70'])
factors = pd.read_csv('data/number-of-deaths-by-risk-factor.csv',
                    header=0,
                    index_col=False,
                    names=[
                        'country',
                        'code',
                        'year',
                        'Diet low in vegetables',
                        'Diet low in whole grains',
                        'Diet low in nuts and seeds',
                        'Diet low in calcium',
                        'Unsafe sex',
                        'No access to handwashing facility',
                        'Child wasting',
                        'Child stunting',
                        'Diet high in red meat',
                        'Diet low in fiber',
                        'Diet low in seafood omega-3 fatty acids',
                        'Diet high in sodium',
                        'Low physical activity',
                        'Non-exclusive breastfeeding',
                        'Discontinued breastfeeding',
                        'Iron deficiency',
                        'Vitamin A deficiency',
                        'Zinc deficiency',
                        'Smoking',
                        'Secondhand smoke',
                        'Alcohol use',
                        'Drug use',
                        'High fasting plasma glucose',
                        'High total cholesterol', # Many null values
                        'High systolic blood pressure',
                        'High body-mass index',
                        'Low bone mineral density',
                        'Diet low in fruits',
                        'Diet low in legumes',
                        'Low birth weight for gestation',
                        'Unsafe water source',
                        'Unsafe sanitation',
                        'Household air pollution from solid fuels',
                        'Air pollution',
                        'Outdoor air pollution'])

# Convert data from wide to long
deaths = pd.melt(deaths, id_vars=['country', 'year'], value_vars=['15 to 49', '50 to 69', 'Above 70'], var_name='Age')
factors = pd.melt(factors, id_vars=['country', 'year'], value_vars=['Diet low in vegetables',
                        'Diet low in nuts and seeds',
                        'Diet low in calcium',
                        'Unsafe sex',
                        'No access to handwashing facility',
                        'Child wasting',
                        'Child stunting',
                        'Diet high in red meat',
                        'Diet low in fiber',
                        'Diet low in seafood omega-3 fatty acids',
                        'Diet high in sodium',
                        'Low physical activity',
                        'Non-exclusive breastfeeding',
                        'Discontinued breastfeeding',
                        'Iron deficiency',
                        'Vitamin A deficiency',
                        'Zinc deficiency',
                        'Smoking',
                        'Secondhand smoke',
                        'Alcohol use',
                        'Drug use',
                        'High fasting plasma glucose',
                        'High total cholesterol', # Many null values
                        'High systolic blood pressure',
                        'High body-mass index',
                        'Low bone mineral density',
                        'Diet low in fruits',
                        'Diet low in legumes',
                        'Low birth weight for gestation',
                        'Unsafe water source',
                        'Unsafe sanitation',
                        'Household air pollution from solid fuels',
                        'Air pollution',
                        'Outdoor air pollution'], var_name='Risk Factor')

# Country Selection
countries = deaths['country'].unique() # get unique country names
countries.sort() # sort alphabetically
selectCountry = st.selectbox('Select a country: ', countries)

# selectCountry = alt.selection_single(
#     name='Select', # name the selection 'Select'
#     fields=['country'], # limit selection to the country field
#     init={'country': countries[0]}, # use first country entry as initial value
#     bind=alt.binding_select(options=countries) # bind to a menu of unique country values
# )

# Year selection
brush = alt.selection_interval(encodings=['x'])
years = alt.Chart(deaths).mark_line().add_selection(
    brush
).transform_filter(
    alt.datum.country == selectCountry
).encode(
    alt.X('year:O', title='Year'),
    alt.Y('sum(value)', title='Smoking Deaths (all ages)')
).properties(
	width=400,
    height=100
)

# Area chart - Smoking deaths by ages
base = alt.Chart(deaths).mark_area().transform_filter(
    alt.datum.country == selectCountry
).transform_filter(
    brush
).encode(
    alt.X('year:O', title='Year'),
    y=alt.Y('value:Q', title='Smoking Deaths by Ages (normalized)', stack="normalize"),
    color=alt.Color('Age:O', scale=alt.Scale(scheme='lightorange')),
    tooltip='Age:O',
    text='Age:O'
).properties(
    width=400,
    height=200
)

# Bar chart - Risk factors
bar_factors = alt.Chart(factors).mark_bar().transform_filter(
    alt.datum.country == selectCountry
).transform_filter(
    brush
).encode(
    alt.X('sum(value):Q', title='Total deaths'),
    y=alt.Y('Risk Factor:O',sort='-x'),
    tooltip='sum(value):Q',
    color=alt.condition(
      alt.datum['Risk Factor'] == 'Smoking',
      alt.value("red"),  # Smoking color
      alt.value("lightgray")  # Other than smoking
    )
).properties(
    width=200,
    height=400
)

# Visualize
st.altair_chart(alt.hconcat(alt.vconcat(base,years)
                            .properties(spacing=20), bar_factors)
                            .configure_legend(orient='top-left', strokeColor='gray',
                                            fillColor='#EEEEEE',
                                            padding=5,
                                            cornerRadius=10)
                            .properties(spacing=20, autosize="pad")
                            .configure_title(
                                            align="center",
                                            fontSize=20,
                                            font='Arial',
                                            color='black'))




#########################################################
#############       tobacco_sales.py        #############
#########################################################
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

###########################################################
#############       tobacco_control.py        #############
###########################################################


####### Datasets

control_dataset = 'https://raw.githubusercontent.com/JulioCandela1993/VisualAnalytics/master/data/control_policy.csv'
deaths_dataset = 'https://raw.githubusercontent.com/JulioCandela1993/VisualAnalytics/master/data/deaths.csv'

####### Dashboard

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

