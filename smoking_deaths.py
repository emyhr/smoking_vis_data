import altair as alt
import streamlit as st
import pandas as pd


st.header("Smoking Deaths from 1990 to 2017")

'''
The following analysis is based on the evaluation made by World Health Organization (WHO) 
to country policies against Tobacco. A score from 1 to 5 is assigned depending on the intensity 
of a country to deal with Tobacco issues being 1 the worst and 5 the best
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
selectCountry = alt.selection_single(
    name='Select', # name the selection 'Select'
    fields=['country'], # limit selection to the country field
    init={'country': countries[0]}, # use first country entry as initial value
    bind=alt.binding_select(options=countries) # bind to a menu of unique country values
)

# Year selection
brush = alt.selection_interval(encodings=['x'])
years = alt.Chart(deaths).mark_line().add_selection(
    brush
).transform_filter(
    selectCountry
).encode(
    alt.X('year:O', title='Year'),
    alt.Y('sum(value)', title='Smoking Deaths (all ages)')
).properties(
    height=100
)

# Area chart - Smoking deaths by ages
base = alt.Chart(deaths).mark_area().add_selection(
    selectCountry
).transform_filter(
    selectCountry
).transform_filter(
    brush
).encode(
    alt.X('year:O', title='Year'),
    y=alt.Y('value:Q', title='Smoking Deaths by Ages (normalized)', stack="normalize"),
    color=alt.Color('Age:O', scale=alt.Scale(scheme='lightorange')),
    tooltip='Age:O',
    text='Age:O'
).properties(
    width=550,
    height=250
)

# Bar chart - Risk factors
bar_factors = alt.Chart(factors).mark_bar().add_selection(
    selectCountry
).transform_filter(
    selectCountry
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
    width=150,
    height=450
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