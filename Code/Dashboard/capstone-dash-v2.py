# Run this app with `python app.py` and
# visit http://127.0.0.1:8050/ in your web browser.


import dash
from dash import dcc
from dash import html
from dash import Input, Output, State 
import dash_bootstrap_components as dbc
import plotly.express as px
import pandas as pd
from dash.dependencies import Input, Output
import pymssql
from urllib.request import urlopen
import json
import numpy as np
#import matplotlib.pyplot as plt
#import seaborn as sns
import plotly.graph_objects as go
import pickle
from sklearn.model_selection import train_test_split
from sklearn.ensemble import RandomForestRegressor

from config import database
from config import user
from config import password
from config import server

cnxn = pymssql.connect(server, user, password, database)
cursor = cnxn.cursor()



conn = pymssql.connect(server,user, password,database)
cursor = cnxn.cursor()
query_own = f'SELECT * FROM OwnPrice'
dfo = pd.read_sql(query_own, cnxn)

###Historical events 
query_own = f'SELECT * FROM OwnPrice'
dfo = pd.read_sql(query_own, cnxn)

dfo['Date'] = pd.to_datetime(dfo[['year','month']].assign(DAY=1))
monthly_df = dfo[['Date','sfrMedianPrice','condoMedianPrice','coopMedianPrice']]
line_df = monthly_df.groupby('Date').agg('mean').rename(columns = {'sfrMedianPrice' : 'Single Family Residence', 
                                                                    'condoMedianPrice' : 'Condos',
                                                                    'coopMedianPrice' : 'Coops'})

fig_events = px.line(line_df,
       x = line_df.index,
       y = line_df.columns)

fig_events.update_layout(
        title = 'NYC Residential Property Average Median Prices 2010-2022',
        xaxis_title = 'Date',
        yaxis_title = 'Average Median Price',
        legend_title = 'Legend')

fig_events.add_vrect(x0="2020-03-22", x1="2020-03-28", 
              annotation_text="NYC Pause Program begins", annotation_position="top left",
              fillcolor="black", opacity=0.9, line_width=5)

fig_events.add_vrect(x0="2010-07-21",x1="2010-07-21", annotation_text="Dodd-Frank Act Passes", annotation_position="top left",
              fillcolor="black", opacity=0.9, line_width=5)

fig_events.add_vrect(x0="2019-06-14",x1="2019-06-14", annotation_text=f"Housing Stability &<br> Tenant Protection Act", annotation_position="top right",
              fillcolor="black", opacity=0.9, line_width=5)

fig_events.add_vrect(x0="2016-03-22",x1="2016-03-22", annotation_text=f"Zoning for Quality &<br> and Affordability Initiative", annotation_position="top right",
              fillcolor="black", opacity=0.9, line_width=5)

###

query_roll = "SELECT * FROM RollingSales"
query_nbd = "SELECT * FROM Neighborhood"
query_bor = "SELECT * FROM Borough"

df_roll = pd.read_sql(query_roll, cnxn)
df_nbd = pd.read_sql(query_nbd, cnxn)
df_bor = pd.read_sql(query_bor, cnxn)

RS_N_df = pd.merge(df_roll, df_nbd, how='inner', on='neighborhoodID')
full_df = pd.merge(RS_N_df, df_bor, how='inner', on='boroughID')
full_df.drop(columns='neighborhoodID', axis=1, inplace=True)

zipcodes = full_df[full_df['zipcode'] > 0]
zipcodes[['zipcode','del']] = full_df['zipcode'].astype(str).str.split('.',expand=True)
zipcodes.drop('del',axis=1, inplace=True)

zipcodes['Date'] = pd.to_datetime(zipcodes['saleDate'], format="%Y/%m/%d")
zipcodes.drop('saleDate',axis=1, inplace=True)
zipcodes.rename(columns = {'salePrice' : 'Sale Price'}, inplace=True)

# separate out by borough because Manhattan is skewing map coloring
mndf = zipcodes[(zipcodes.boroughID == 1)]
bxdf = zipcodes[(zipcodes.boroughID == 2)]
bkdf = zipcodes[(zipcodes.boroughID == 3)]
qndf = zipcodes[(zipcodes.boroughID == 4)]
sidf = zipcodes[(zipcodes.boroughID == 5)]


mndf = mndf[['zipcode','Sale Price']].groupby('zipcode').agg('median').reset_index()
bxdf = bxdf[['zipcode','Sale Price']].groupby('zipcode').agg('median').reset_index()
bkdf = bkdf[['zipcode','Sale Price']].groupby('zipcode').agg('median').reset_index()
qndf = qndf[['zipcode','Sale Price']].groupby('zipcode').agg('median').reset_index()
sidf = sidf[['zipcode','Sale Price']].groupby('zipcode').agg('median').reset_index()

with urlopen('https://data.cityofnewyork.us/resource/pri4-ifjk.geojson') as response:
    zip_codes = json.load(response)
    
mn_fig = px.choropleth_mapbox(mndf, geojson=zip_codes, locations='zipcode', color='Sale Price',
                           featureidkey='properties.modzcta',
                           color_continuous_scale="Viridis",
                           range_color=(0, 15000000),
                           mapbox_style="carto-positron",
                           zoom=10.25, center = {"lat": 40.796, "lon": -73.982},
                           opacity=0.5,
                           labels={},
                           title="Manhattan Property Sales Price by Zip Code"
                          ).update(layout=dict(title=dict(x=0.5)))
mn_fig.update_layout(margin={"r":0,"t":30,"l":0,"b":0})

bx_fig = px.choropleth_mapbox(bxdf, geojson=zip_codes, locations='zipcode', color='Sale Price',
                           featureidkey='properties.modzcta',
                           color_continuous_scale="Viridis",
                           range_color=(0, np.max(bxdf['Sale Price'])),
                           mapbox_style="carto-positron",
                           zoom=10.75, center = {"lat": 40.850, "lon": -73.89},
                           opacity=0.5,
                           labels={},
                           title="Bronx Property Sales Price by Zip Code"
                          ).update(layout=dict(title=dict(x=0.5)))
bx_fig.update_layout(margin={"r":0,"t":30,"l":0,"b":0})

bk_fig = px.choropleth_mapbox(bkdf, geojson=zip_codes, locations='zipcode', color='Sale Price',
                           featureidkey='properties.modzcta',
                           color_continuous_scale="Viridis",
                           range_color=(0, np.max(bkdf['Sale Price'])),
                           mapbox_style="carto-positron",
                           zoom=10.3, center = {"lat": 40.65, "lon": -73.95},
                           opacity=0.5,
                           labels={},
                           title="Brooklyn Property Sales Price by Zip Code"
                          ).update(layout=dict(title=dict(x=0.5)))
bk_fig.update_layout(margin={"r":0,"t":30,"l":0,"b":0})

qn_fig = px.choropleth_mapbox(qndf, geojson=zip_codes, locations='zipcode', color='Sale Price',
                           featureidkey='properties.modzcta',
                           color_continuous_scale="Viridis",
                           range_color=(0, np.max(qndf['Sale Price'])),
                           mapbox_style="carto-positron",
                           zoom=9.75, center = {"lat": 40.7, "lon": -73.769417},
                           opacity=0.5,
                           labels={},
                           title="Queens Property Sales Price by Zip Code"
                          ).update(layout=dict(title=dict(x=0.5)))
qn_fig.update_layout(margin={"r":0,"t":30,"l":0,"b":0})

si_fig = px.choropleth_mapbox(sidf, geojson=zip_codes, locations='zipcode', color='Sale Price',
                           featureidkey='properties.modzcta',
                           color_continuous_scale="Viridis",
                           range_color=(0, np.max(sidf['Sale Price'])),
                           mapbox_style="carto-positron",
                           zoom=10.5, center = {"lat": 40.580753, "lon": -74.152794},
                           opacity=0.5,
                           labels={},
                           title="Staten Island Property Sales Price by Zip Code"
                          ).update(layout=dict(title=dict(x=0.5)))
si_fig.update_layout(margin={"r":0,"t":30,"l":0,"b":0})

### Employee Pay maps
query_census = "SELECT * FROM BusinessPatterns"
df_census = pd.read_sql(query_census, cnxn)

df_census["Average Payroll"] = (df_census["annPayroll"]/df_census["numEmployees"]).apply(lambda x: x * 1000).astype(int)

with urlopen('https://data.beta.nyc/dataset/3bf5fb73-edb5-4b05-bb29-7c95f4a727fc/resource/894e9162-871c-4552-a09c-c6915d8783fb/download/zip_code_040114.geojson') as response:
    zip_codes_2 = json.load(response)

keys = zip_codes_2.keys()
keys

census_fig = px.choropleth_mapbox(df_census, geojson=zip_codes, locations='zipcode', color='Average Payroll',
                           featureidkey='properties.modzcta',
                           color_continuous_scale="Viridis",
                           range_color=(0, 200000),
                           mapbox_style="carto-positron",
                           zoom=9.25, center = {"lat": 40.743, "lon": -73.988},
                           opacity=0.5,
                           labels={},
                           title="Average Employee Pay in NYC by Zip Code"
                          ).update(layout=dict(title=dict(x=0.5)))
census_fig.update_layout(margin={"r":0,"t":30,"l":0,"b":0})


### Top 3 Neighborhoods with Greatest Increase in Median Rent

query = f'SELECT * FROM RentPrice'
dfr = pd.read_sql(query, cnxn)
dfr['Date'] = pd.to_datetime(dfr[['year', 'month']].assign(DAY=1))
dfr['Month/Year'] = pd.to_datetime(dfr[['year', 'month']].assign(DAY=1))

mny = dfr[dfr['boroughID']==1].copy()
bx = dfr[dfr['boroughID']==2].copy()
bkl = dfr[dfr['boroughID']==3].copy()
qn = dfr[dfr['boroughID']==4].copy()

# mean of studios and one bedroom for Manhattan, Bronx, Brooklyn, Queens
mny['Studio/One-Bed Median Rent'] = mny.iloc[:,4:6].mean(axis=1)
bx['Studio/One-Bed Median Rent'] = bx.iloc[:,4:6].mean(axis=1)
bkl['Studio/One-Bed Median Rent'] = bkl.iloc[:,4:6].mean(axis=1)
qn['Studio/One-Bed Median Rent'] = qn.iloc[:,4:6].mean(axis=1)

mny_top = mny.copy()
bx_top = bx.copy()
bkl_top = bkl.copy()
qn_top = qn.copy()
mny_top = mny.loc[(mny['neighborhood']=='Central Park South') | (mny['neighborhood']=='Midtown South') | (mny['neighborhood']=='Flatiron') |
    (mny['neighborhood']=='Little Italy') | (mny['neighborhood']=='Soho') | (mny['neighborhood']=='Washington Heights')]
bx_top = bx.loc[(bx['neighborhood']=='Mott Haven') | (bx['neighborhood']=='Riverdale') |
    (bx['neighborhood']=='University Heights') | (bx['neighborhood']=='Kingsbridge')]
bkl_top = bkl.loc[(bkl['neighborhood']=='Greenpoint') | (bkl['neighborhood']=='Prospect Heights') | (bkl['neighborhood']=='Downtown Brooklyn') |
    (bkl['neighborhood']=='Bay Ridge') | (bkl['neighborhood']=='Sheepshead Bay') | (bkl['neighborhood']=='Midwood')]
qn_top = qn.loc[(qn['neighborhood']=='Long Island City') | (qn['neighborhood']=='Corona') | ( qn['neighborhood']=='Astoria') |
    (qn['neighborhood']=='Elmhurst') | (qn['neighborhood']=='Rego Park') | (qn['neighborhood']=='Forest Hills')]

mny_top.rename(columns={"neighborhood": "Neighborhood"}, inplace=True)
bx_top.rename(columns={"neighborhood": "Neighborhood"}, inplace=True)
bkl_top.rename(columns={"neighborhood": "Neighborhood"}, inplace=True)
qn_top.rename(columns={"neighborhood": "Neighborhood"}, inplace=True)

# manhattan top 3 and bottom 3 neighborhoods
fig_top_mny_rent = px.line(mny_top, x="Month/Year", y="Studio/One-Bed Median Rent", color="Neighborhood",
    title="Top 3 and Bottom 3 Manhattan Neighborhoods for Rate of Rent Increase 2010-2022",
    markers=True)
fig_top_mny_rent.update_traces(opacity=0.4)
fig_top_mny_rent.update_layout(yaxis_title='Studio/One-Bed Median Rent ($USD)')
fig_top_mny_rent.update_traces(textposition="bottom right")
fig_top_mny_rent.add_trace(go.Scatter(x=['2010-01-01','2022-08-01'],
    y=[mny_top[(mny_top['Neighborhood']=='Central Park South') & (mny_top['Month/Year']=='2010-01-01')]['Studio/One-Bed Median Rent'].values[0],
        mny_top[(mny_top['Neighborhood']=='Central Park South') & (mny_top['Month/Year']=='2022-08-01')]['Studio/One-Bed Median Rent'].values[0]],
    mode='lines', name='CPS Net Δ', line=dict(color='#9467bd')))
fig_top_mny_rent.add_trace(go.Scatter(x=['2010-01-01','2022-08-01'],
    y=[mny_top[(mny_top['Neighborhood']=='Flatiron') & (mny_top['Month/Year']=='2010-01-01')]['Studio/One-Bed Median Rent'].values[0],
        mny_top[(mny_top['Neighborhood']=='Flatiron') & (mny_top['Month/Year']=='2022-08-01')]['Studio/One-Bed Median Rent'].values[0]],
    mode='lines', name='FI Net Δ', line=dict(color='#d62728')))
fig_top_mny_rent.add_trace(go.Scatter(x=['2010-01-01','2022-08-01'],
    y=[mny_top[(mny_top['Neighborhood']=='Little Italy') & (mny_top['Month/Year']=='2010-01-01')]['Studio/One-Bed Median Rent'].values[0],
        mny_top[(mny_top['Neighborhood']=='Little Italy') & (mny_top['Month/Year']=='2022-08-01')]['Studio/One-Bed Median Rent'].values[0]],
    mode='lines', name='LI Net Δ', line=dict(color='#2ca02c')))
fig_top_mny_rent.add_trace(go.Scatter(x=['2010-01-01','2022-08-01'],
    y=[mny_top[(mny_top['Neighborhood']=='Midtown South') & (mny_top['Month/Year']=='2010-01-01')]['Studio/One-Bed Median Rent'].values[0],
        mny_top[(mny_top['Neighborhood']=='Midtown South') & (mny_top['Month/Year']=='2022-08-01')]['Studio/One-Bed Median Rent'].values[0]],
    mode='lines', name='MtS Net Δ', line=dict(color='#e377c2')))
fig_top_mny_rent.add_trace(go.Scatter(x=['2010-01-01','2022-08-01'],
    y=[mny_top[(mny_top['Neighborhood']=='Soho') & (mny_top['Month/Year']=='2010-01-01')]['Studio/One-Bed Median Rent'].values[0],
        mny_top[(mny_top['Neighborhood']=='Soho') & (mny_top['Month/Year']=='2022-08-01')]['Studio/One-Bed Median Rent'].values[0]],
    mode='lines', name='Soho Net Δ', line=dict(color='#ff7f0e')))
fig_top_mny_rent.add_trace(go.Scatter(x=['2010-01-01','2022-08-01'],
    y=[mny_top[(mny_top['Neighborhood']=='Washington Heights') & (mny_top['Month/Year']=='2010-01-01')]['Studio/One-Bed Median Rent'].values[0],
        mny_top[(mny_top['Neighborhood']=='Washington Heights') & (mny_top['Month/Year']=='2022-08-01')]['Studio/One-Bed Median Rent'].values[0]],
    mode='lines', name='WH Net Δ', line=dict(color='#17becf')))

# bronx
fig_top_bx_rent = px.line(bx_top, x="Month/Year", y="Studio/One-Bed Median Rent", color="Neighborhood",
    title="Top 2 and Bottom 2 Bronx Neighborhoods for Rate of Rent Increase 2010(12)(13)(14)-2022",
    markers=True)
fig_top_bx_rent.update_traces(opacity=0.4)
fig_top_bx_rent.update_layout(yaxis_title='Studio/One-Bed Median Rent ($USD)')
fig_top_bx_rent.update_traces(textposition="bottom right")
fig_top_bx_rent.add_trace(go.Scatter(x=['2012-02-01','2022-08-01'],
    y=[bx_top[(bx_top['Neighborhood']=='Kingsbridge') & (bx_top['Month/Year']=='2012-02-01')]['Studio/One-Bed Median Rent'].values[0],
        bx_top[(bx_top['Neighborhood']=='Kingsbridge') & (bx_top['Month/Year']=='2022-08-01')]['Studio/One-Bed Median Rent'].values[0]],
    mode='lines', name='KB Net Δ', line=dict(color='#9467bd')))
fig_top_bx_rent.add_trace(go.Scatter(x=['2014-06-01','2022-08-01'],
    y=[bx_top[(bx_top['Neighborhood']=='Mott Haven') & (bx_top['Month/Year']=='2014-06-01')]['Studio/One-Bed Median Rent'].values[0],
        bx_top[(bx_top['Neighborhood']=='Mott Haven') & (bx_top['Month/Year']=='2022-08-01')]['Studio/One-Bed Median Rent'].values[0]],
    mode='lines', name='MH Net Δ', line=dict(color='#d62728')))
fig_top_bx_rent.add_trace(go.Scatter(x=['2010-01-01','2022-08-01'],
    y=[bx_top[(bx_top['Neighborhood']=='Riverdale') & (bx_top['Month/Year']=='2010-01-01')]['Studio/One-Bed Median Rent'].values[0],
        bx_top[(bx_top['Neighborhood']=='Riverdale') & (bx_top['Month/Year']=='2022-08-01')]['Studio/One-Bed Median Rent'].values[0]],
    mode='lines', name='Rd Net Δ', line=dict(color='#2ca02c')))
fig_top_bx_rent.add_trace(go.Scatter(x=['2013-03-01','2022-08-01'],
    y=[bx_top[(bx_top['Neighborhood']=='University Heights') & (bx_top['Month/Year']=='2013-03-01')]['Studio/One-Bed Median Rent'].values[0],
        bx_top[(bx_top['Neighborhood']=='University Heights') & (bx_top['Month/Year']=='2022-08-01')]['Studio/One-Bed Median Rent'].values[0]],
    mode='lines', name='UH Net Δ', line=dict(color='#e377c2')))

# brooklyn
fig_top_bkl_rent = px.line(bkl_top, x="Month/Year", y="Studio/One-Bed Median Rent", color="Neighborhood",
    title="Top 3 and Bottom 3 Brooklyn Neighborhoods for Rate of Rent Increase 2010(11)-2022",
    markers=True)
fig_top_bkl_rent.update_traces(opacity=0.4)
fig_top_bkl_rent.update_traces(textposition="bottom right")
fig_top_bkl_rent.update_layout(yaxis_title='Studio/One-Bed Median Rent ($USD)')
fig_top_bkl_rent.add_trace(go.Scatter(x=['2010-01-01','2022-08-01'],
    y=[bkl_top[(bkl_top['Neighborhood']=='Bay Ridge') & (bkl_top['Month/Year']=='2010-01-01')]['Studio/One-Bed Median Rent'].values[0],
        bkl_top[(bkl_top['Neighborhood']=='Bay Ridge') & (bkl_top['Month/Year']=='2022-08-01')]['Studio/One-Bed Median Rent'].values[0]],
    mode='lines', name='BR Net Δ', line=dict(color='#9467bd')))
fig_top_bkl_rent.add_trace(go.Scatter(x=['2010-01-01','2022-08-01'],
    y=[bkl_top[(bkl_top['Neighborhood']=='Downtown Brooklyn') & (bkl_top['Month/Year']=='2010-01-01')]['Studio/One-Bed Median Rent'].values[0],
        bkl_top[(bkl_top['Neighborhood']=='Downtown Brooklyn') & (bkl_top['Month/Year']=='2022-08-01')]['Studio/One-Bed Median Rent'].values[0]],
    mode='lines', name='Dt Bkl Net Δ', line=dict(color='#d62728')))
fig_top_bkl_rent.add_trace(go.Scatter(x=['2010-01-01','2022-08-01'],
    y=[bkl_top[(bkl_top['Neighborhood']=='Greenpoint') & (bkl_top['Month/Year']=='2010-01-01')]['Studio/One-Bed Median Rent'].values[0],
        bkl_top[(bkl_top['Neighborhood']=='Greenpoint') & (bkl_top['Month/Year']=='2022-08-01')]['Studio/One-Bed Median Rent'].values[0]],
    mode='lines', name='GP Net Δ', line=dict(color='#2ca02c')))
fig_top_bkl_rent.add_trace(go.Scatter(x=['2011-02-01','2022-08-01'],
    y=[bkl_top[(bkl_top['Neighborhood']=='Midwood') & (bkl_top['Month/Year']=='2011-02-01')]['Studio/One-Bed Median Rent'].values[0],
        bkl_top[(bkl_top['Neighborhood']=='Midwood') & (bkl_top['Month/Year']=='2022-08-01')]['Studio/One-Bed Median Rent'].values[0]],
    mode='lines', name='MW Net Δ', line=dict(color='#e377c2')))
fig_top_bkl_rent.add_trace(go.Scatter(x=['2010-01-01','2022-08-01'],
    y=[bkl_top[(bkl_top['Neighborhood']=='Prospect Heights') & (bkl_top['Month/Year']=='2010-01-01')]['Studio/One-Bed Median Rent'].values[0],
        bkl_top[(bkl_top['Neighborhood']=='Prospect Heights') & (bkl_top['Month/Year']=='2022-08-01')]['Studio/One-Bed Median Rent'].values[0]],
    mode='lines', name='PH Net Δ', line=dict(color='#ff7f0e')))
fig_top_bkl_rent.add_trace(go.Scatter(x=['2010-02-01','2022-08-01'],
    y=[bkl_top[(bkl_top['Neighborhood']=='Sheepshead Bay') & (bkl_top['Month/Year']=='2010-02-01')]['Studio/One-Bed Median Rent'].values[0],
        bkl_top[(bkl_top['Neighborhood']=='Sheepshead Bay') & (bkl_top['Month/Year']=='2022-08-01')]['Studio/One-Bed Median Rent'].values[0]],
    mode='lines', name='ShB Net Δ', line=dict(color='#17becf')))


#queens
fig_top_qn_rent = px.line(qn_top, x="Month/Year", y="Studio/One-Bed Median Rent", color="Neighborhood",
    title="Top 3 and Bottom 3 Queens Neighborhoods for Rate of Rent Increase 2010(12)-2022",
    markers=True)
fig_top_qn_rent.update_traces(opacity=0.4)
fig_top_qn_rent.update_traces(textposition="bottom right")
fig_top_qn_rent.update_layout(yaxis_title='Studio/One-Bed Median Rent ($USD)')
fig_top_qn_rent.add_trace(go.Scatter(x=['2010-01-01','2022-08-01'],
    y=[qn_top[(qn_top['Neighborhood']=='Astoria') & (qn_top['Month/Year']=='2010-01-01')]['Studio/One-Bed Median Rent'].values[0],
        qn_top[(qn_top['Neighborhood']=='Astoria') & (qn_top['Month/Year']=='2022-08-01')]['Studio/One-Bed Median Rent'].values[0]],
    mode='lines', name='Astoria Net Δ', line=dict(color='#9467bd')))
fig_top_qn_rent.add_trace(go.Scatter(x=['2010-01-01','2022-08-01'],
    y=[qn_top[(qn_top['Neighborhood']=='Corona') & (qn_top['Month/Year']=='2010-01-01')]['Studio/One-Bed Median Rent'].values[0],
        qn_top[(qn_top['Neighborhood']=='Corona') & (qn_top['Month/Year']=='2022-08-01')]['Studio/One-Bed Median Rent'].values[0]],
    mode='lines', name='Corona Net Δ', line=dict(color='#d62728')))
fig_top_qn_rent.add_trace(go.Scatter(x=['2012-10-01','2022-08-01'],
    y=[qn_top[(qn_top['Neighborhood']=='Elmhurst') & (qn_top['Month/Year']=='2012-10-01')]['Studio/One-Bed Median Rent'].values[0],
        qn_top[(qn_top['Neighborhood']=='Elmhurst') & (qn_top['Month/Year']=='2022-08-01')]['Studio/One-Bed Median Rent'].values[0]],
    mode='lines', name='Elmhurst Net Δ', line=dict(color='#2ca02c')))
fig_top_qn_rent.add_trace(go.Scatter(x=['2010-01-01','2022-08-01'],
    y=[qn_top[(qn_top['Neighborhood']=='Forest Hills') & (qn_top['Month/Year']=='2010-01-01')]['Studio/One-Bed Median Rent'].values[0],
        qn_top[(qn_top['Neighborhood']=='Forest Hills') & (qn_top['Month/Year']=='2022-08-01')]['Studio/One-Bed Median Rent'].values[0]],
    mode='lines', name='FH Net Δ', line=dict(color='#e377c2')))
fig_top_qn_rent.add_trace(go.Scatter(x=['2010-01-01','2022-08-01'],
    y=[qn_top[(qn_top['Neighborhood']=='Long Island City') & (qn_top['Month/Year']=='2010-01-01')]['Studio/One-Bed Median Rent'].values[0],
        qn_top[(qn_top['Neighborhood']=='Long Island City') & (qn_top['Month/Year']=='2022-08-01')]['Studio/One-Bed Median Rent'].values[0]],
    mode='lines', name='LIC Net Δ', line=dict(color='#ff7f0e')))
fig_top_qn_rent.add_trace(go.Scatter(x=['2010-01-01','2022-08-01'],
    y=[qn_top[(qn_top['Neighborhood']=='Rego Park') & (qn_top['Month/Year']=='2010-01-01')]['Studio/One-Bed Median Rent'].values[0],
        qn_top[(qn_top['Neighborhood']=='Rego Park') & (qn_top['Month/Year']=='2022-08-01')]['Studio/One-Bed Median Rent'].values[0]],
    mode='lines', name='RP Net Δ', line=dict(color='#17becf')))


def create_top_hood_graph(borough):
    boro_dict = {
        'Manhattan' : fig_top_mny_rent,
        'Bronx' : fig_top_bx_rent,
        'Brooklyn' : fig_top_bkl_rent,
        'Queens' : fig_top_qn_rent
                 }
    boro_top_nb_fig = boro_dict[borough]
    return boro_top_nb_fig


### 2022 Most and Least Expensive Neighborhoods by Borough (Condo Prices)
# not enough data to include the Bronx and Staten Island
query = f'SELECT * FROM OwnPrice'
dfo = pd.read_sql(query, cnxn)
dfo['date'] = pd.to_datetime(dfo[['year', 'month']].assign(DAY=1))

mny = dfo.loc[(dfo["boroughID"]==1) & (dfo["year"] == 2022)][["boroughID","neighborhood","condoMedianPrice"]].groupby("neighborhood").mean().sort_values(by="condoMedianPrice",ascending=False)
bkl = dfo.loc[(dfo["boroughID"]==3) & (dfo["year"] == 2022)][["boroughID","neighborhood","condoMedianPrice"]].groupby("neighborhood").mean().sort_values(by="condoMedianPrice",ascending=False)
qn = dfo.loc[(dfo["boroughID"]==4) & (dfo["year"] == 2022)][["boroughID","neighborhood","condoMedianPrice"]].groupby("neighborhood").mean().sort_values(by="condoMedianPrice",ascending=False)

mny = mny[mny["condoMedianPrice"].notnull()].reset_index()
bkl = bkl[bkl["condoMedianPrice"].notnull()].reset_index()
qn = qn[qn["condoMedianPrice"].notnull()].reset_index()

pd.set_option('display.float_format', lambda x: '%.0f' % x)
df = pd.concat([mny,bkl,qn]).reset_index().drop(['index'],axis=1)
df['boroughID']=df['boroughID'].astype(int)
df['condoMedianPrice']=df['condoMedianPrice'].astype('float')

mm = df[(df['neighborhood']=='East Harlem') | (df['neighborhood']=='Tribeca') |
(df['neighborhood']=='Sheepshead Bay') | (df['neighborhood']=='Brooklyn Heights') |
(df['neighborhood']=='Maspeth') | (df['neighborhood']=='Long Island City')
].reset_index().drop('index',axis=1)

mm['borough'] = mm['boroughID'].map({1:'Manhattan', 2:'Bronx', 3:'Brooklyn', 4:'Queens', 5:'Staten Island'})
mm.drop('boroughID',axis=1,inplace=True)
mm['condoMedianPrice'] = mm['condoMedianPrice'].round()

fig_exp = px.bar(mm, x="borough", y="condoMedianPrice", color='neighborhood', barmode="overlay",
    text=mm['condoMedianPrice'].apply(lambda x: "${:.0f}".format(x)), opacity=1)
fig_exp.update_traces(marker_line=dict(width=1, color='black'))
fig_exp.update_layout(title="2022 Most and Least Expensive Neighborhoods by Borough in terms of Condo Prices",
                  xaxis_title="Borough",
                  yaxis_title="Condo Median Price ($USD)",
                  legend_title="Neighborhood")

# not enough data to include the Bronx and Staten Island
query = f'SELECT * FROM RentPrice'
dfr = pd.read_sql(query, cnxn)

dfr['mean'] = dfr.iloc[:,4:6].mean(axis=1)

mny_r = dfr.loc[(dfr["boroughID"]==1) & (dfr["year"] == 2022)][["boroughID","neighborhood","mean"]].groupby("neighborhood").mean().sort_values(by="mean",ascending=False)
bkl_r = dfr.loc[(dfr["boroughID"]==3) & (dfr["year"] == 2022)][["boroughID","neighborhood","mean"]].groupby("neighborhood").mean().sort_values(by="mean",ascending=False)
qn_r = dfr.loc[(dfr["boroughID"]==4) & (dfr["year"] == 2022)][["boroughID","neighborhood","mean"]].groupby("neighborhood").mean().sort_values(by="mean",ascending=False)

pd.set_option('display.float_format', lambda x: '%.0f' % x)
df_r = pd.concat([mny_r,bkl_r,qn_r]).reset_index()
df_r['boroughID']=df_r['boroughID'].astype(int)

mm = df_r[(df_r['neighborhood']=='Inwood') | (df_r['neighborhood']=='Central Park South') |
(df_r['neighborhood']=='Dyker Heights') | (df_r['neighborhood']=='DUMBO') |
(df_r['neighborhood']=='Jamaica Hills') | (df_r['neighborhood']=='Long Island City')
].reset_index().drop('index',axis=1)

mm['borough'] = mm['boroughID'].map({1:'Manhattan', 2:'Bronx', 3:'Brooklyn', 4:'Queens', 5:'Staten Island'})
mm.drop('boroughID',axis=1,inplace=True)

mm['mean'] = mm['mean'].round()

import plotly.graph_objects as go
fig_least = px.bar(mm, x="borough", y="mean", color="neighborhood", barmode="overlay",
    text=mm['mean'].apply(lambda x: "${:.0f}".format(x)), opacity=1)
fig_least.update_traces(marker_line=dict(width=1, color='black'))
fig_least.update_layout(title="2022 Most and Least Expensive Neighborhoods by Borough in terms of Studio/One-Bedroom Rent",
                  xaxis_title="Borough",
                  yaxis_title="Average of Median Studio/One-Bedroom Rent ($USD)",
                  legend_title="Neighborhood")


### Before & During Pandemic plots (10): 5 for sales, 5 for rent

mny1 = dfo.loc[(dfo["boroughID"]==1) & (dfo["date"] >= "2020-04-01") & (dfo["date"] < "2021-04-01")]

mny2 = dfo.loc[(dfo["boroughID"]==1) & (dfo["date"] >= "2021-04-01")]

mny1.loc[:,'period'] = '(4/20-3/21)'
mny2.loc[:,'period'] = '(4/21-8/22)'

mny = pd.concat([mny1,mny2])
mny

mny_melt=pd.melt(mny, id_vars=['neighborhood','period'],
    value_vars=['sfrMedianPrice','condoMedianPrice','coopMedianPrice'],
    var_name='home type',value_name='price')
mny_melt['home type'] = mny_melt['home type'].map({
    'sfrMedianPrice':'Townhouse',
    'condoMedianPrice':'Condo',
    'coopMedianPrice': 'Co-Op'
})
mny_melt = mny_melt[mny_melt['home type'] != 'Townhouse'] # not enough data to generalize single family/townhouse in Manhattan
mny_melt['period'] = mny_melt[['home type', 'period']].agg(' '.join, axis=1)
mny_melt.drop('home type',axis=1,inplace=True)
mny_melt

fig_mny_own = go.Figure()

periods = ['Condo (4/20-3/21)', 'Condo (4/21-8/22)', 'Co-Op (4/20-3/21)', 'Co-Op (4/21-8/22)']

colors = ["rgba(135,206,255,0.5)", "rgba(99,184,255,0.5)", "rgba(255,99,71,0.5)",
"rgba(205,79,57,0.5)"]


outlines = ["royalblue", "royalblue", "indianred", "indianred"]

for (period,color,outline) in zip(periods,colors,outlines):
    fig_mny_own.add_trace(go.Violin(x=mny_melt['period'][(mny_melt['period'] == period)],
                            y=mny_melt['price'][mny_melt['period'] == period],
                            name=period,
                            fillcolor=color,
                            line_color=outline,
                            box_visible=True,
                            meanline_visible=True))
fig_mny_own.update_layout(title="Price of Manhattan Homes by Type during First Year of Pandemic (4/20-3/21) and After (4/21-8/22)",
                  xaxis_title = "Home Type (Buying Period)",
                  yaxis_title = "Sale Price ($USD)")

###
bx1 = dfo.loc[(dfo["boroughID"]==2) & (dfo["date"] >= "2020-04-01") & (dfo["date"] < "2021-01-01")]
bx2 = dfo.loc[(dfo["boroughID"]==2) & (dfo["date"] >= "2021-01-01")]

bx1.loc[:,'period'] = '(4/20-3/21)'
bx2.loc[:,'period'] = '(4/21-8/22)'

bx = pd.concat([bx1,bx2])

bx_melt=pd.melt(bx, id_vars=['neighborhood','period'],
    value_vars=['sfrMedianPrice','condoMedianPrice','coopMedianPrice'],
    var_name='home type',value_name='price')
bx_melt['home type'] = bx_melt['home type'].map({
    'sfrMedianPrice':'Townhouse',
    'condoMedianPrice':'Condo',
    'coopMedianPrice': 'Co-Op'
})
bx_melt = bx_melt[bx_melt['home type'] == 'Townhouse'] # not enough data for other house types
bx_melt['period'] = bx_melt[['home type', 'period']].agg(' '.join, axis=1)
bx_melt.drop('home type',axis=1,inplace=True)
bx_melt

fig_bx_own = go.Figure()

periods = ['Townhouse (4/20-3/21)', 'Townhouse (4/21-8/22)']

colors = ["rgba(135,206,255,0.5)", "rgba(99,184,255,0.5)"]

outlines = ["royalblue", "royalblue"]

for (period,color,outline) in zip(periods,colors,outlines):
    fig_bx_own.add_trace(go.Violin(x=bx_melt['period'][(bx_melt['period'] == period)],
                            y=bx_melt['price'][bx_melt['period'] == period],
                            name=period,
                            fillcolor=color,
                            line_color=outline,
                            box_visible=True,
                            meanline_visible=True))
fig_bx_own.update_layout(title="Price of Bronx Townhouses during First Year of Pandemic (4/20-3/21) and After (4/21-8/22)",
                 xaxis_title = "Home Type (Buying Period)",
                 yaxis_title = "Sale Price ($USD)")

###
bkl1 = dfo.loc[(dfo["boroughID"]==3) & (dfo["date"] >= "2020-04-01") & (dfo["date"] < "2021-04-01")]

bkl2 = dfo.loc[(dfo["boroughID"]==3) & (dfo["date"] >= "2021-04-01")]

bkl1.loc[:,'period'] = '(4/20-3/21)'
bkl2.loc[:,'period'] = '(4/21-8/22)'

bkl = pd.concat([bkl1,bkl2])
bkl

bkl_melt=pd.melt(bkl, id_vars=['neighborhood','period'],
    value_vars=['sfrMedianPrice','condoMedianPrice','coopMedianPrice'],
    var_name='home type',value_name='price')
bkl_melt['home type'] = bkl_melt['home type'].map({
    'sfrMedianPrice':'Townhouse',
    'condoMedianPrice':'Condo',
    'coopMedianPrice': 'Co-Op'
})
bkl_melt['period'] = bkl_melt[['home type', 'period']].agg(' '.join, axis=1)
bkl_melt.drop('home type',axis=1,inplace=True)


fig_bkl_own = go.Figure()

periods = ['Townhouse (4/20-3/21)', 'Townhouse (4/21-8/22)',
           'Condo (4/20-3/21)', 'Condo (4/21-8/22)',
           'Co-Op (4/20-3/21)', 'Co-Op (4/21-8/22)']

colors = ["rgba(135,206,255,0.5)","rgba(99,184,255,0.5)",
          "rgba(255,99,71,0.5)", "rgba(205,79,57,0.5)",
          "rgba(84,255,159,0.5)", "rgba(0,205,102,0.5)"]

outlines = ["royalblue", "royalblue", "indianred", "indianred",
            "seagreen", "seagreen"]

for (period,color,outline) in zip(periods,colors,outlines):
    fig_bkl_own.add_trace(go.Violin(x=bkl_melt['period'][(bkl_melt['period'] == period)],
                            y=bkl_melt['price'][bkl_melt['period'] == period],
                            name=period,
                            fillcolor=color,
                            line_color=outline,
                            box_visible=True,
                            meanline_visible=True))
fig_bkl_own.update_layout(title="Price of Brooklyn Homes by Type during First Year of Pandemic (4/20-3/21) and After (4/21-8/22)",
                  xaxis_title = "Home Type (Buying Period)",
                  yaxis_title = "Sale Price ($USD)")

###
qn1 = dfo.loc[(dfo["boroughID"]==4) & (dfo["date"] >= "2020-04-01") & (dfo["date"] < "2021-04-01")]

qn2 = dfo.loc[(dfo["boroughID"]==4) & (dfo["date"] >= "2021-04-01")]

qn1.loc[:,'period'] = '(4/20-3/21)'
qn2.loc[:,'period'] = '(4/21-8/22)'

qn = pd.concat([qn1,qn2])


qn_melt=pd.melt(qn, id_vars=['neighborhood','period'],
    value_vars=['sfrMedianPrice','condoMedianPrice','coopMedianPrice'],
    var_name='home type',value_name='price')
qn_melt['home type'] = qn_melt['home type'].map({
    'sfrMedianPrice':'Townhouse',
    'condoMedianPrice':'Condo',
    'coopMedianPrice': 'Co-Op'
})
qn_melt['period'] = qn_melt[['home type', 'period']].agg(' '.join, axis=1)
qn_melt.drop('home type',axis=1,inplace=True)


fig_qn_own = go.Figure()

periods = ['Townhouse (4/20-3/21)', 'Townhouse (4/21-8/22)',
           'Condo (4/20-3/21)', 'Condo (4/21-8/22)',
           'Co-Op (4/20-3/21)', 'Co-Op (4/21-8/22)']

colors = ["rgba(135,206,255,0.5)","rgba(99,184,255,0.5)",
          "rgba(255,99,71,0.5)", "rgba(205,79,57,0.5)",
          "rgba(84,255,159,0.5)", "rgba(0,205,102,0.5)"]

outlines = ["royalblue", "royalblue", "indianred", "indianred",
            "seagreen", "seagreen"]

for (period,color,outline) in zip(periods,colors,outlines):
    fig_qn_own.add_trace(go.Violin(x=qn_melt['period'][(qn_melt['period'] == period)],
                            y=qn_melt['price'][qn_melt['period'] == period],
                            name=period,
                            fillcolor=color,
                            line_color=outline,
                            box_visible=True,
                            meanline_visible=True))
fig_qn_own.update_layout(title="Price of Queens Homes by Type during First Year of Pandemic (4/20-3/21) and After (4/21-8/22)",
                  xaxis_title = "Home Type (Buying Period)",
                  yaxis_title = "Sale Price ($USD)")

###
sti1 = dfo.loc[(dfo["boroughID"]==5) & (dfo["date"] >= "2020-04-01") & (dfo["date"] < "2021-04-01")]

sti2 = dfo.loc[(dfo["boroughID"]==5) & (dfo["date"] >= "2021-04-01")]

sti1.loc[:,'period'] = '(4/20-3/21)'
sti2.loc[:,'period'] = '(4/21-8/22)'

sti = pd.concat([sti1,sti2])


sti_melt=pd.melt(sti, id_vars=['neighborhood','period'],
    value_vars=['sfrMedianPrice','condoMedianPrice','coopMedianPrice'],
    var_name='home type',value_name='price')
sti_melt['home type'] = sti_melt['home type'].map({
    'sfrMedianPrice':'Townhouse',
    'condoMedianPrice':'Condo',
    'coopMedianPrice': 'Co-Op'
})
sti_melt = sti_melt[sti_melt['home type'] != 'Co-Op'] # not enough data for coop
sti_melt['period'] = sti_melt[['home type', 'period']].agg(' '.join, axis=1)
sti_melt.drop('home type',axis=1,inplace=True)


fig_sti_own = go.Figure()

periods = ['Townhouse (4/20-3/21)', 'Townhouse (4/21-8/22)',
           'Condo (4/20-3/21)', 'Condo (4/21-8/22)']

colors = ["rgba(135,206,255,0.5)","rgba(99,184,255,0.5)",
          "rgba(255,99,71,0.5)", "rgba(205,79,57,0.5)"]

outlines = ["royalblue", "royalblue", "indianred", "indianred"]

for (period,color,outline) in zip(periods,colors,outlines):
    fig_sti_own.add_trace(go.Violin(x=sti_melt['period'][(sti_melt['period'] == period)],
                            y=sti_melt['price'][sti_melt['period'] == period],
                            name=period,
                            fillcolor=color,
                            line_color=outline,
                            box_visible=True,
                            meanline_visible=True))
fig_sti_own.update_layout(title="Price of Staten Island Homes by Type during First Year of Pandemic (4/20-3/21) and After (4/21-8/22)",
                  xaxis_title = "Home Type (Buying Period)",
                  yaxis_title = "Sale Price ($USD)")

###
dfr['Date'] = pd.to_datetime(dfr[['year', 'month']].assign(DAY=1))
mny1 = dfr.loc[(dfr["boroughID"]==1) & (dfr["Date"] >= "2020-04-01") & (dfr["Date"] < "2021-04-01")]

mny2 = dfr.loc[(dfr["boroughID"]==1) & (dfr["Date"] >= "2021-04-01")]

mny1.loc[:,'period'] = '(4/20-3/21)'
mny2.loc[:,'period'] = '(4/21-8/22)'

mny = pd.concat([mny1,mny2])
mny

mny_melt=pd.melt(mny, id_vars=['neighborhood','period'],
    value_vars=['studioMedianPrice','onebedMedianPrice','twobedMedianPrice', 'threebedMedianPrice'],
    var_name='home type',value_name='rent')
mny_melt['home type'] = mny_melt['home type'].map({
    'studioMedianPrice':'Studio',
    'onebedMedianPrice':'One Bed',
    'twobedMedianPrice': 'Two Bed',
    'threebedMedianPrice': 'Three Bed'
})
mny_melt['period'] = mny_melt[['home type', 'period']].agg(' '.join, axis=1)
mny_melt.drop('home type',axis=1,inplace=True)
mny_melt

fig_mny_rent = go.Figure()

periods = ['Studio (4/20-3/21)', 'Studio (4/21-8/22)',
           'One Bed (4/20-3/21)', 'One Bed (4/21-8/22)',
           'Two Bed (4/20-3/21)', 'Two Bed (4/21-8/22)',
           'Three Bed (4/20-3/21)', 'Three Bed (4/21-8/22)']

colors = ["rgba(135,206,255,0.5)","rgba(99,184,255,0.5)",
          "rgba(255,99,71,0.5)", "rgba(205,79,57,0.5)",
          "rgba(84,255,159,0.5)", "rgba(0,205,102,0.5)",
          "rgba(255,193,37,0.5)", "rgba(205,155,29,0.5)"]

outlines = ["royalblue", "royalblue", "indianred", "indianred",
            "seagreen", "seagreen", "darkgoldenrod", "darkgoldenrod"]

for (period,color,outline) in zip(periods,colors,outlines):
    fig_mny_rent.add_trace(go.Violin(x=mny_melt['period'][(mny_melt['period'] == period)],
                            y=mny_melt['rent'][mny_melt['period'] == period],
                            name=period,
                            fillcolor=color,
                            line_color=outline,
                            box_visible=True,
                            meanline_visible=True))
fig_mny_rent.update_layout(title="Manhattan Rental Prices by Number of Bedrooms during First Year of Pandemic (4/20-3/21) and After (4/21-8/22)",
                  xaxis_title = "Bedroom Count (Rent Period)",
                  yaxis_title = "Rent Price ($USD)")
###
bx1 = dfr.loc[(dfr["boroughID"]==2) & (dfr["Date"] >= "2020-04-01") & (dfr["Date"] < "2021-04-01")]

bx2 = dfr.loc[(dfr["boroughID"]==2) & (dfr["Date"] >= "2021-04-01")]


bx1.loc[:,'period'] = '(4/20-3/21)'
bx2.loc[:,'period'] = '(4/21-8/22)'

bx = pd.concat([bx1,bx2])
bx

bx_melt=pd.melt(bx, id_vars=['neighborhood','period'],
    value_vars=['studioMedianPrice','onebedMedianPrice','twobedMedianPrice', 'threebedMedianPrice'],
    var_name='home type',value_name='rent')
bx_melt['home type'] = bx_melt['home type'].map({
    'studioMedianPrice':'Studio',
    'onebedMedianPrice':'One Bed',
    'twobedMedianPrice': 'Two Bed',
    'threebedMedianPrice': 'Three Bed'
})
bx_melt['period'] = bx_melt[['home type', 'period']].agg(' '.join, axis=1)
bx_melt.drop('home type',axis=1,inplace=True)
bx_melt

fig_bx_rent = go.Figure()

periods = ['Studio (4/20-3/21)', 'Studio (4/21-8/22)',
           'One Bed (4/20-3/21)', 'One Bed (4/21-8/22)',
           'Two Bed (4/20-3/21)', 'Two Bed (4/21-8/22)',
           'Three Bed (4/20-3/21)', 'Three Bed (4/21-8/22)']

colors = ["rgba(135,206,255,0.5)","rgba(99,184,255,0.5)",
          "rgba(255,99,71,0.5)", "rgba(205,79,57,0.5)",
          "rgba(84,255,159,0.5)", "rgba(0,205,102,0.5)",
          "rgba(255,193,37,0.5)", "rgba(205,155,29,0.5)"]

outlines = ["royalblue", "royalblue", "indianred", "indianred",
            "seagreen", "seagreen", "darkgoldenrod", "darkgoldenrod"]

for (period,color,outline) in zip(periods,colors,outlines):
    fig_bx_rent.add_trace(go.Violin(x=bx_melt['period'][(bx_melt['period'] == period)],
                            y=bx_melt['rent'][bx_melt['period'] == period],
                            name=period,
                            fillcolor=color,
                            line_color=outline,
                            box_visible=True,
                            meanline_visible=True))
fig_bx_rent.update_layout(title="Bronx Rental Prices by Number of Bedrooms during First Year of Pandemic (4/20-3/21) and After (4/21-8/22)",
                  xaxis_title = "Bedroom Count (Rent Period)",
                  yaxis_title = "Rent Price ($USD)")
###
bkl1 = dfr.loc[(dfr["boroughID"]==3) & (dfr["Date"] >= "2020-04-01") & (dfr["Date"] < "2021-04-01")]

bkl2 = dfr.loc[(dfr["boroughID"]==3) & (dfr["Date"] >= "2021-04-01")]


bkl1.loc[:,'period'] = '(4/20-3/21)'
bkl2.loc[:,'period'] = '(4/21-8/22)'

bkl = pd.concat([bkl1,bkl2])
bkl

bkl_melt=pd.melt(bkl, id_vars=['neighborhood','period'],
    value_vars=['studioMedianPrice','onebedMedianPrice','twobedMedianPrice', 'threebedMedianPrice'],
    var_name='home type',value_name='rent')
bkl_melt['home type'] = bkl_melt['home type'].map({
    'studioMedianPrice':'Studio',
    'onebedMedianPrice':'One Bed',
    'twobedMedianPrice': 'Two Bed',
    'threebedMedianPrice': 'Three Bed'
})
bkl_melt['period'] = bkl_melt[['home type', 'period']].agg(' '.join, axis=1)
bkl_melt.drop('home type',axis=1,inplace=True)
bkl_melt

fig_bkl_rent = go.Figure()

periods = ['Studio (4/20-3/21)', 'Studio (4/21-8/22)',
           'One Bed (4/20-3/21)', 'One Bed (4/21-8/22)',
           'Two Bed (4/20-3/21)', 'Two Bed (4/21-8/22)',
           'Three Bed (4/20-3/21)', 'Three Bed (4/21-8/22)']

colors = ["rgba(135,206,255,0.5)","rgba(99,184,255,0.5)",
          "rgba(255,99,71,0.5)", "rgba(205,79,57,0.5)",
          "rgba(84,255,159,0.5)", "rgba(0,205,102,0.5)",
          "rgba(255,193,37,0.5)", "rgba(205,155,29,0.5)"]

outlines = ["royalblue", "royalblue", "indianred", "indianred",
            "seagreen", "seagreen", "darkgoldenrod", "darkgoldenrod"]

for (period,color,outline) in zip(periods,colors,outlines):
    fig_bkl_rent.add_trace(go.Violin(x=bkl_melt['period'][(bkl_melt['period'] == period)],
                            y=bkl_melt['rent'][bkl_melt['period'] == period],
                            name=period,
                            fillcolor=color,
                            line_color=outline,
                            box_visible=True,
                            meanline_visible=True))
fig_bkl_rent.update_layout(title="Brooklyn Rental Prices by Number of Bedrooms during First Year of Pandemic (4/20-3/21) and After (4/21-8/22)",
                  xaxis_title = "Bedroom Count (Rent Period)",
                  yaxis_title = "Rent Price ($USD)")
###
qn1 = dfr.loc[(dfr["boroughID"]==4) & (dfr["Date"] >= "2020-04-01") & (dfr["Date"] < "2021-04-01")]

qn2 = dfr.loc[(dfr["boroughID"]==4) & (dfr["Date"] >= "2021-04-01")]


qn1.loc[:,'period'] = '(4/20-3/21)'
qn2.loc[:,'period'] = '(4/21-8/22)'

qn = pd.concat([qn1,qn2])
qn

qn_melt=pd.melt(qn, id_vars=['neighborhood','period'],
    value_vars=['studioMedianPrice','onebedMedianPrice','twobedMedianPrice', 'threebedMedianPrice'],
    var_name='home type',value_name='rent')
qn_melt['home type'] = qn_melt['home type'].map({
    'studioMedianPrice':'Studio',
    'onebedMedianPrice':'One Bed',
    'twobedMedianPrice': 'Two Bed',
    'threebedMedianPrice': 'Three Bed'
})
qn_melt['period'] = qn_melt[['home type', 'period']].agg(' '.join, axis=1)
qn_melt.drop('home type',axis=1,inplace=True)
qn_melt

fig_qn_rent = go.Figure()

periods = ['Studio (4/20-3/21)', 'Studio (4/21-8/22)',
           'One Bed (4/20-3/21)', 'One Bed (4/21-8/22)',
           'Two Bed (4/20-3/21)', 'Two Bed (4/21-8/22)',
           'Three Bed (4/20-3/21)', 'Three Bed (4/21-8/22)']

colors = ["rgba(135,206,255,0.5)","rgba(99,184,255,0.5)",
          "rgba(255,99,71,0.5)", "rgba(205,79,57,0.5)",
          "rgba(84,255,159,0.5)", "rgba(0,205,102,0.5)",
          "rgba(255,193,37,0.5)", "rgba(205,155,29,0.5)"]

outlines = ["royalblue", "royalblue", "indianred", "indianred",
            "seagreen", "seagreen", "darkgoldenrod", "darkgoldenrod"]

for (period,color,outline) in zip(periods,colors,outlines):
    fig_qn_rent.add_trace(go.Violin(x=qn_melt['period'][(qn_melt['period'] == period)],
                            y=qn_melt['rent'][qn_melt['period'] == period],
                            name=period,
                            fillcolor=color,
                            line_color=outline,
                            box_visible=True,
                            meanline_visible=True))
fig_qn_rent.update_layout(title="Queens Rental Prices by Number of Bedrooms during First Year of Pandemic (4/20-3/21) and After (4/21-8/22)",
                  xaxis_title = "Bedroom Count (Rent Period)",
                  yaxis_title = "Rent Price ($USD)")
###
sti1 = dfr.loc[(dfr["boroughID"]==5) & (dfr["Date"] >= "2020-04-01") & (dfr["Date"] < "2021-04-01")]

sti2 = dfr.loc[(dfr["boroughID"]==5) & (dfr["Date"] >= "2021-04-01")]


sti1.loc[:,'period'] = '(4/20-3/21)'
sti2.loc[:,'period'] = '(4/21-8/22)'

sti = pd.concat([sti1,sti2])
sti

sti_melt=pd.melt(sti, id_vars=['neighborhood','period'],
    value_vars=['studioMedianPrice','onebedMedianPrice','twobedMedianPrice', 'threebedMedianPrice'],
    var_name='home type',value_name='rent')
sti_melt['home type'] = sti_melt['home type'].map({
    'studioMedianPrice':'Studio',
    'onebedMedianPrice':'One Bed',
    'twobedMedianPrice': 'Two Bed',
    'threebedMedianPrice': 'Three Bed'
})
sti_melt['period'] = sti_melt[['home type', 'period']].agg(' '.join, axis=1)
sti_melt.drop('home type',axis=1,inplace=True)
sti_melt

fig_sti_rent = go.Figure()

periods = ['Studio (4/20-3/21)', 'Studio (4/21-8/22)',
           'One Bed (4/20-3/21)', 'One Bed (4/21-8/22)',
           'Two Bed (4/20-3/21)', 'Two Bed (4/21-8/22)',
           'Three Bed (4/20-3/21)', 'Three Bed (4/21-8/22)']

colors = ["rgba(135,206,255,0.5)","rgba(99,184,255,0.5)",
          "rgba(255,99,71,0.5)", "rgba(205,79,57,0.5)",
          "rgba(84,255,159,0.5)", "rgba(0,205,102,0.5)",
          "rgba(255,193,37,0.5)", "rgba(205,155,29,0.5)"]

outlines = ["royalblue", "royalblue", "indianred", "indianred",
            "seagreen", "seagreen", "darkgoldenrod", "darkgoldenrod"]

for (period,color,outline) in zip(periods,colors,outlines):
    fig_sti_rent.add_trace(go.Violin(x=sti_melt['period'][(sti_melt['period'] == period)],
                            y=sti_melt['rent'][sti_melt['period'] == period],
                            name=period,
                            fillcolor=color,
                            line_color=outline,
                            box_visible=True,
                            meanline_visible=True))
fig_sti_rent.update_layout(title="Staten Island Rental Prices by Number of Bedrooms during First Year of Pandemic (4/20-3/21) and After (4/21-8/22)",
                  xaxis_title = "Bedroom Count (Rent Period)",
                  yaxis_title = "Rent Price ($USD)")

### Median Home Price by Month (rolling sales)
RollingSales = full_df.copy()
RollingSales['saleMonth'] = pd.DatetimeIndex(RollingSales['saleDate']).month
RollingSales = RollingSales[['saleMonth','boroughName','salePrice']].copy()
RollingSales['salePrice'] = RollingSales[['salePrice']]/1000

salesMan = RollingSales[RollingSales["boroughName"] == "Manhattan"]
salesBronx = RollingSales[RollingSales["boroughName"] == "Bronx"]
salesBrook = RollingSales[RollingSales["boroughName"] == "Brooklyn"]
salesQueens = RollingSales[RollingSales["boroughName"] == "Queens"]
salesStat = RollingSales[RollingSales["boroughName"] == "Staten Island"]

salesMan = salesMan.groupby(['saleMonth', 'boroughName']).median()
salesMan.insert(0, 'monthSale', range(1, 1 + len(salesMan)))
salesBronx = salesBronx.groupby(['saleMonth', 'boroughName']).median()
salesBronx.insert(0, 'monthSale', range(1, 1 + len(salesBronx)))
salesBrook = salesBrook.groupby(['saleMonth', 'boroughName']).median()
salesBrook.insert(0, 'monthSale', range(1, 1 + len(salesBrook)))
salesQueens = salesQueens.groupby(['saleMonth', 'boroughName']).median()
salesQueens.insert(0, 'monthSale', range(1, 1 + len(salesQueens)))
salesStat = salesStat.groupby(['saleMonth', 'boroughName']).median()
salesStat.insert(0, 'monthSale', range(1, 1 + len(salesStat)))

salesMan.monthSale[salesMan[salesMan.monthSale==12].index]=0
salesMan.monthSale[salesMan[salesMan.monthSale==11].index]=-1
salesMan.monthSale[salesMan[salesMan.monthSale==10].index]=-2
salesMan.monthSale[salesMan[salesMan.monthSale==9].index]=-3
salesMan = salesMan.sort_values("monthSale")
salesMan['monthSale'] = salesMan['monthSale'] + 4

salesBronx.monthSale[salesBronx[salesBronx.monthSale==12].index]=0
salesBronx.monthSale[salesBronx[salesBronx.monthSale==11].index]=-1
salesBronx.monthSale[salesBronx[salesBronx.monthSale==10].index]=-2
salesBronx.monthSale[salesBronx[salesBronx.monthSale==9].index]=-3
salesBronx = salesBronx.sort_values("monthSale")
salesBronx['monthSale'] = salesBronx['monthSale'] + 4

salesBrook.monthSale[salesBrook[salesBrook.monthSale==12].index]=0
salesBrook.monthSale[salesBrook[salesBrook.monthSale==11].index]=-1
salesBrook.monthSale[salesBrook[salesBrook.monthSale==10].index]=-2
salesBrook.monthSale[salesBrook[salesBrook.monthSale==9].index]=-3
salesBrook = salesBrook.sort_values("monthSale")
salesBrook['monthSale'] = salesBrook['monthSale'] + 4

salesQueens.monthSale[salesQueens[salesQueens.monthSale==12].index]=0
salesQueens.monthSale[salesQueens[salesQueens.monthSale==11].index]=-1
salesQueens.monthSale[salesQueens[salesQueens.monthSale==10].index]=-2
salesQueens.monthSale[salesQueens[salesQueens.monthSale==9].index]=-3
salesQueens = salesQueens.sort_values("monthSale")
salesQueens['monthSale'] = salesQueens['monthSale'] + 4

salesStat.monthSale[salesStat[salesStat.monthSale==12].index]=0
salesStat.monthSale[salesStat[salesStat.monthSale==11].index]=-1
salesStat.monthSale[salesStat[salesStat.monthSale==10].index]=-2
salesStat.monthSale[salesStat[salesStat.monthSale==9].index]=-3
salesStat = salesStat.sort_values("monthSale")
salesStat['monthSale'] = salesStat['monthSale'] + 4

df1 = salesMan
df2 = salesBronx
df3 = salesBrook
df4 = salesQueens
df5 = salesStat
dfs = {"Manhattan" : df1, "Bronx": df2, "Brooklyn" : df3, "Queens" : df4, "Staten Island" : df5}

figMedMan = go.Figure()
for i in dfs:
    figMedMan = figMedMan.add_trace(go.Scatter(x = dfs[i]["monthSale"],
                                   y = dfs[i]["salePrice"], 
                                   name = i))

figMedMan.update_layout(
        title = 'Median Sale Price by Month',
        xaxis_title = 'Month',
        yaxis_title = 'Median Sale Price (Thousands)',
        legend_title = 'Legend',
        width=800, height=400)

dfs = { "Bronx": df2, "Brooklyn" : df3, "Queens" : df4, "Staten Island" : df5}
figMedNoMan = go.Figure()
for i in dfs:
    figMedNoMan = figMedNoMan.add_trace(go.Scatter(x = dfs[i]["monthSale"],
                                   y = dfs[i]["salePrice"], 
                                   name = i))

figMedNoMan.update_layout(
        title = 'Median Sale Price by Month',
        xaxis_title = 'Month',
        yaxis_title = 'Median Sale Price (Thousands)',
        legend_title = 'Legend',
        width=800, height=400)                 

### How long until rent cost overtakes buy cost
rent = dfr.copy()
own = dfo.copy()
neighbor = df_nbd.copy()
borough = df_bor.copy()

boroughOwn = pd.merge(own, borough, on="boroughID")
boroughOwn = boroughOwn.drop(['neighborhood', 'month','sfrMedianPrice', 'condoMedianPrice'], axis=1)

rent['rentCost'] = rent[['studioMedianPrice', 'onebedMedianPrice', 'twobedMedianPrice','threebedMedianPrice']].mean(axis=1)
rent = rent.drop(['neighborhood','month','studioMedianPrice', 'onebedMedianPrice', 'twobedMedianPrice','threebedMedianPrice'], axis=1)

rentOwn = pd.merge(boroughOwn, rent,  how='left', left_on=['boroughID','year'], right_on = ['boroughID','year'])
rentOwn.dropna()

def create_rent_own(borough):
    temp_df = rentOwn[rentOwn["boroughName"] == borough]
    temp_df = temp_df.groupby(['year']).median()
    temp_df['yearEqui'] = (temp_df['coopMedianPrice'] / temp_df['rentCost']) / 12
    temp_df.insert(0, 'yearInt', range(2010, 2010 + len(temp_df)))

    buyRentBoro = go.Figure()
    buyRentBoro.add_trace(go.Scatter(x= temp_df.yearInt, y =temp_df.yearEqui, fill='tozeroy', name="Buy Cost > Rent Cost"  )) # fill down to xaxis
    buyRentBoro.add_trace(go.Scatter(x= temp_df.yearInt,y= [28,28,28,28,28,28,28,28,28,28,28,28,28,28,28,28], fill='tonexty', name="Rent Cost > Buy Cost"  )) # fill to trace0 y
    
    if borough == 'Staten Island':
        buyRentBoro.update_layout(
                    title = f'How Long Until Renting Cost Overtakes Buying Cost ({borough})',
                    xaxis_title = 'Year of Purchase',
                    yaxis_title = 'Years of Residency',
                    yaxis_range=[0, 25],
                    xaxis_range=[2012, 2022],
                    width=800, height=400)
    else: 
        buyRentBoro.update_layout(
                title = f'How Long Until Renting Cost Overtakes Buying Cost ({borough})',
                xaxis_title = 'Year of Purchase',
                yaxis_title = 'Years of Residency',
                yaxis_range=[0, 25],
                width=800, height=400)
    return buyRentBoro


### Machine Learning Model
with open('random_forest_model.pickle', 'rb') as f:
    rf = pickle.load(f)


query = f'SELECT * FROM RawRollingSales'
data = pd.read_sql(query, cnxn)

data = data.loc[data["SALE PRICE"] > 100000]

data["BOROUGH"] = data["BOROUGH"].astype(str)
data["BLOCK"] = data["BLOCK"].astype(str)
data["LOT"] = data["LOT"].astype(str)
data["ZIP CODE"] = data["ZIP CODE"].astype(int).astype(str)
data["TAX CLASS AT TIME OF SALE"] = data["TAX CLASS AT TIME OF SALE"].astype(str)
data["YEAR BUILT"] = data["YEAR BUILT"].astype(int)
data["SALE DATE"] = pd.to_datetime(data["SALE DATE"])

# remove outliers for each column if value is greater than 3 standard deviations from the mean
# change each outlier to np.nan
for column in data.columns:
    if (pd.api.types.is_numeric_dtype(data[column])):
        mean = data[column].mean()
        std = data[column].std()
        data[column] = data[column].apply(lambda x: np.nan if (x < (mean - 2 * std)) | (x > (mean + 2 * std)) else x)
# create new df with outlier rows cleaned
data.dropna(inplace=True)

# create age column
data["SALE YEAR"] = data["SALE DATE"].apply(lambda x: x.year)
data["AGE"] = data["SALE YEAR"] - data["YEAR BUILT"]

# create model with residential building class category only

# filter out non-residential building class categories
sales_res = data[data["BUILDING CLASS CATEGORY"].isin(['01 ONE FAMILY DWELLINGS', '02 TWO FAMILY DWELLINGS',
       '03 THREE FAMILY DWELLINGS', '07 RENTALS - WALKUP APARTMENTS',
       '08 RENTALS - ELEVATOR APARTMENTS',
       '14 RENTALS - 4-10 UNIT'])]

# drop TOTAL UNITS as correlation is >75% with residential units
# drop YEAR BUILT, AGE and SALE YEAR as they have low correlation to SALES PRICE
# for categorical variable, keep ZIP CODE, NEIGHBORHOOD, and BUILDING CLASS CATEGORY AT TIME OF SALE, TAX CLASS AT TIME OF SALE
sales_res.drop(["LOT", "ADDRESS", "YEAR BUILT", "SALE DATE", "SALE YEAR", "BOROUGH", "BLOCK",
                      "TOTAL UNITS", "BUILDING CLASS CATEGORY",
                      "AGE"], axis=1, inplace=True)

# split test and train
y = sales_res.pop("SALE PRICE")
X = sales_res.copy()
# create dummies in X
X_with_dummies = pd.get_dummies(X,drop_first=True)
# create test/train split
X_train, X_test, y_train, y_test = train_test_split(X_with_dummies, y, random_state=0, test_size=0.25)                     

predictions_rf = rf.predict(X_test)
residuals_rf = (y_test - predictions_rf)

### actual vs predicted for sale price
fig_rf = px.scatter(
    x=y_test, y=predictions_rf,
    trendline_color_override='royalblue',
    color_discrete_sequence=['crimson'],
    title="Actual vs. Predicted Sale Price for Random Forest Model",
    width=600, height=600
)
fig_rf.update_traces(marker=dict(
            color='rgba(220, 20, 60, 0.3)',
            size=6,
            line=dict(
                color='rgb(220, 20, 60)',
                width=1
            )
      )
)
fig_rf.update_layout(
    xaxis_title="Actual Value",
    yaxis_title="Predicted Value",
    legend_title="Legend Title"
)
fig_rf.update_layout({
    'plot_bgcolor': 'rgba(0, 0, 0, 0)',
    'paper_bgcolor': 'rgba(0, 0, 0, 0)'}
)
fig_rf.update_xaxes(showline=True, linewidth=2, linecolor='black',
                    showgrid=True, gridcolor='lightgray', zeroline=True,
                    zerolinecolor='lightgray', zerolinewidth=1
)
fig_rf.update_yaxes(showline=True, linewidth=2, linecolor='black',
                     showgrid=True, gridcolor='lightgray', zeroline=True,
                    zerolinecolor='lightgray', zerolinewidth=1
)
fig_rf.add_shape(type='line',
                x0=min(min(y_test), min(predictions_rf)),
                y0=min(min(y_test), min(predictions_rf)),
                x1=max(max(y_test), max(predictions_rf)),
                y1=max(max(y_test), max(predictions_rf)),
                line=dict(color='royalblue'),
                xref='x',
                yref='y'
)
### residuals 
fig_rf_res = px.scatter(
    x=predictions_rf, y=residuals_rf,
    color_discrete_sequence=['crimson'],
    title="Residuals for Random Forest Model",
    width=800, height=600
)
fig_rf_res.update_traces(marker=dict(
            color='rgba(220, 20, 60, 0.3)',
            size=6,
            line=dict(
                color='rgb(220, 20, 60)',
                width=1
            )
      )
)
fig_rf_res.update_layout(
    xaxis_title="Predicted Value",
    yaxis_title="Residuals",
    legend_title="Residuals Plot for XGBoost"
)
fig_rf_res.add_shape(type='line',
                x0=-1e6,
                y0=0,
                x1=31.5e6,
                y1=0,
                line=dict(color='royalblue'),
                xref='x',
                yref='y'
)
fig_rf_res.update_layout({
    'plot_bgcolor': 'rgba(0, 0, 0, 0)',
    'paper_bgcolor': 'rgba(0, 0, 0, 0)'}
)
fig_rf_res.update_xaxes(showline=True, linewidth=2, linecolor='black',
                    showgrid=True, gridcolor='lightgray', zeroline=True,
                    zerolinecolor='lightgray', zerolinewidth=1
)
fig_rf_res.update_yaxes(showline=True, linewidth=2, linecolor='black',
                     showgrid=True, gridcolor='lightgray', zeroline=True,
                    zerolinecolor='lightgray', zerolinewidth=1
)
###
# random forest feature importance in plotly express
rankings = rf.feature_importances_.tolist()
importance = pd.DataFrame(sorted(zip(X_train.columns,rankings),reverse=True),columns=["Feature","Importance"]).sort_values("Importance",ascending = False)

random_forest_feature_fig = px.bar(importance[0:20].sort_values("Importance"), x='Importance', y='Feature',
            color='Importance', orientation='h', color_continuous_scale=px.colors.sequential.Magenta,
            height=800, title='Random Forest Feature Importance')
random_forest_feature_fig.update_layout(coloraxis_showscale=False)



################################ Actual Styling starts below ########################################

# link fontawesome to get the chevron icons
FA = "https://use.fontawesome.com/releases/v5.8.1/css/all.css"

app = dash.Dash(external_stylesheets=[dbc.themes.BOOTSTRAP, FA], suppress_callback_exceptions=True)

# the style arguments for the sidebar. We use position:fixed and a fixed width
SIDEBAR_STYLE = {
    "position": "fixed",
    "top": 0,
    "left": 0,
    "bottom": 0,
    "width": "16rem",
    "padding": "2rem 1rem",
    "background-color": "#f8f9fa",
}

# the styles for the main content position it to the right of the sidebar and
# add some padding.
CONTENT_STYLE = {
    "margin-left": "18rem",
    "margin-right": "2rem",
    "padding": "2rem 1rem",
}

submenu_1 = [
    html.Li(
        # use Row and Col components to position the chevrons
        dbc.Row(
            [
                dbc.Col("Property Sale Trends"),
                dbc.Col(
                    html.I(className="fas fa-chevron-right me-3"),
                    width="auto",
                ),
            ],
            className="my-1",
        ),
        style={"cursor": "pointer"},
        id="submenu-1",
    ),
    # we use the Collapse component to hide and reveal the navigation links
    dbc.Collapse(
        [
            dbc.NavLink("Page 1.1: Prices and Events", href="/page-1/1"),
            dbc.NavLink("Page 1.2: Price over time", href="/page-1/2")
        ],
        id="submenu-1-collapse",
    ),
]

submenu_2 = [
    html.Li(
        dbc.Row(
            [
                dbc.Col("Maps"),
                dbc.Col(
                    html.I(className="fas fa-chevron-right me-3"),
                    width="auto",
                ),
            ],
            className="my-1",
        ),
        style={"cursor": "pointer"},
        id="submenu-2",
    ),
    dbc.Collapse(
        [
            dbc.NavLink("Page 2.1: Affordability Across NYC", href="/page-2/1")
        ],
        id="submenu-2-collapse",
    ),
]

submenu_3 = [
    html.Li(
        dbc.Row(
            [
                dbc.Col("Drilling Down"),
                dbc.Col(
                    html.I(className="fas fa-chevron-right me-3"),
                    width="auto",
                ),
            ],
            className="my-1",
        ),
        style={"cursor": "pointer"},
        id="submenu-3",
    ),
    dbc.Collapse(
        [
            dbc.NavLink("Page 3.1: Top 3 Neighborhoods", href="/page-3/1"),
            dbc.NavLink("Page 3.2: Most/Least Expensive Neighborhoods", href="/page-3/2"),
            dbc.NavLink("Page 3.3: Pandemic Price Shifts", href="/page-3/3"),
            dbc.NavLink("Page 3.4: Renting vs. Owning", href="/page-3/4")
        ],
        id="submenu-3-collapse",
    ),
]

submenu_4 = [
    html.Li(
        dbc.Row(
            [
                dbc.Col("Machine Learning"),
                dbc.Col(
                    html.I(className="fas fa-chevron-right me-3"),
                    width="auto",
                ),
            ],
            className="my-1",
        ),
        style={"cursor": "pointer"},
        id="submenu-4",
    ),
    dbc.Collapse(
        [
            dbc.NavLink("Page 4.1: Random Forest Model", href="/page-4/1"),
            dbc.NavLink("Page 4.2: Predict a Price", href="/page-4/2")
        ],
        id="submenu-4-collapse",
    ),
]

sidebar = html.Div(
    [
        html.H2("NYC Real Estate", className="display-4"),
        html.Hr(),
        html.P(
            "A look into price trends", className="lead"
        ),
        dbc.Nav(submenu_1 + submenu_2 + submenu_3 + submenu_4, vertical=True),
    ],
    style=SIDEBAR_STYLE,
    id="sidebar",
)

content = html.Div(id="page-content", style=CONTENT_STYLE)

app.layout = html.Div([dcc.Location(id="url"), sidebar, content])

# this function is used to toggle the is_open property of each Collapse
def toggle_collapse(n, is_open):
    if n:
        return not is_open
    return is_open


# this function applies the "open" class to rotate the chevron
def set_navitem_class(is_open):
    if is_open:
        return "open"
    return ""


for i in [1, 2, 3, 4]:
    app.callback(
        Output(f"submenu-{i}-collapse", "is_open"),
        [Input(f"submenu-{i}", "n_clicks")],
        [Input(f"submenu-{i}-collapse", "is_open")],
    )(toggle_collapse)

    app.callback(
        Output(f"submenu-{i}", "className"),
        [Input(f"submenu-{i}-collapse", "is_open")],
    )(set_navitem_class)


@app.callback(Output("page-content", "children"), 
            [Input("url", "pathname")])
def render_page_content(pathname):
    if pathname in ["/", "/page-1/1"]:
        return html.Div([
                    html.H1("The Rising Cost of Living In New York City"),
                    html.Div(
                        dbc.Row([
                            dbc.Col(
                                html.P("""The New York City real estate market is an especially competitive one,
                                        with the cost of living at risk of outpacing residents' earning potential.
                                        Record luxury condo sales exceeding the $200 million price tag make national
                                        headlines and average single family property prices have almost doubled in the last
                                        decade. 
                                        """),
                                width=6
                            )
                        ])
                    ),
                    dcc.Graph(
                            id='historical_events',
                            figure=fig_events
                    ),
                    dcc.Interval(
                        id='interval-component',
                        interval=5*1000, # in milliseconds
                        n_intervals=0
                    )
                ])
    elif pathname == "/page-1/2":
        return dbc.Container([
            html.H1([
                    dbc.Col(
                        "How has the market varied over the past year?")
            ]),
            html.Div([
                html.P([
                    dcc.RadioItems(
                    ['With Manhattan','Without Manhattan'],
                    'With Manhattan',
                    id='median_sale'
                )
                ]),
                dcc.Graph(id='median_sale_graph')
            ])
        ])
    elif pathname == "/page-2/1":
        return dbc.Container([
            html.H2([
                    dbc.Col(
                        "A closer look at home sale prices across NYC.")
            ]), 
            html.P([
                dcc.Dropdown(
                    ['Manhattan','Bronx','Brooklyn','Queens','Staten Island'],
                    'Manhattan',
                    id='borough'
                )
            ]),
            html.Div([
                dcc.Graph(id='zip map')
            ]),
            html.Br(),
            html.H2("How much are people earning in NYC?"),
            html.Div(
                dcc.Graph(figure=census_fig)
            )
        ])    
    elif pathname == "/page-3/1":
        return dbc.Container([
            html.H1("Which neighborhoods have seen the greatest and least change in prices over the past 12 years?"),
            html.P([
                dcc.Dropdown(
                    ['Manhattan','Bronx','Brooklyn','Queens'],
                    'Manhattan',
                    id='top_three_hoods'
                )
            ]),
            html.P([
                dcc.Graph(id='top_three_hoods_output')
            ])
        ])
    elif pathname == "/page-3/2":
        return dbc.Container([
            html.H1("Rent costs breakdown by Borough"),
            html.P([
                dcc.Dropdown(
                    ['Condos','Studio/One Bedroom'],
                    'Condos',
                    id='most_least_expensive_input'
                )
            ]),
            html.Div([
                dcc.Graph(id='most-least-expensive-output')
            ])
        ])
    elif pathname == "/page-3/3":
        return dbc.Container([
            html.H2(["A breakdown of home price changes since early 2020"]),
            html.Div([
                html.P(
                    ['Select a borough to see how home prices compare across the pandemic.']
                ),
                dcc.Dropdown(
                    ['Manhattan','Bronx','Brooklyn','Queens','Staten Island'],
                    'Manhattan',
                    id='COVID_own_input'
                )
            ]),
            html.Div([
                dcc.Graph(id='COVID_own_output')
            ]),
            html.H2(["A breakdown of rent price changes since early 2020"]),
            html.Div([
                html.P(
                    ['Select a borough to see how rent prices compare across the pandemic']
                ),
                dcc.Dropdown(
                    ['Manhattan','Bronx','Brooklyn','Queens','Staten Island'],
                    'Manhattan',
                    id='COVID_rent_input'
                )
            ]),
            html.Div([
                dcc.Graph(id='COVID_rent_output')
            ])            
        ])
    elif pathname == "/page-3/4":
        return dbc.Container([
            html.H1("How long do you need to rent before it makes more sense to buy?"),
            html.P('Please Select a Borough'), 
            dcc.Dropdown(
                ['Manhattan','Bronx','Brooklyn','Queens','Staten Island'],
                'Manhattan',
                id='borough_thresh'
            ),
            dcc.Graph(id='borough_thresh_output')


        ])
    elif pathname == "/page-4/1":
        return dbc.Container([
            html.H1("Machine Learning: Predicting pricing trends"),
            html.P("""Our model uses property sales data from the past year (September 2021 - August 2022) in New York City. 
                    The data has numeric and categorical features describing a property's physical characteristics, location, building classifications and price. 
                    Our model predicts the price of residential properties based on these features."""),
            html.Div([
                dbc.Row([
                    dbc.Col(
                        html.Div(dcc.Graph(figure=fig_rf, style={'display': 'inline-block'})),
                        width=6
                    ),
                    dbc.Col(
                        html.Div(dcc.Graph(figure=fig_rf_res, style={'display': 'inline-block'})),
                        width=6
                    )
                ], align='center'),
                html.Br(),

            ]),
            html.P(
                dcc.Graph(figure=random_forest_feature_fig)  
            )              
        ])    
    elif pathname == "/page-4/2":
        return dbc.Container([
            html.H1(
                "Now input your own features to get a price estimate."
            ),
            html.Div([
                dbc.Col([
                    dbc.Row([
                        dbc.Col(html.Label(children='Neighborhood:')),
                        dbc.Col(dcc.Dropdown(sales_res.NEIGHBORHOOD.unique(),
                        'ASTORIA',
                        id='neighborhood'))
                    ]),
                    html.Br(),
                    dbc.Row([
                        dbc.Col(html.Label(children='Zip Code:')),
                        dbc.Col(dcc.Dropdown(sales_res['ZIP CODE'].unique(),
                                            sales_res['ZIP CODE'].min(),
                                            id='zip_code'))
                    ]),
                    html.Br(),
                    dbc.Row([
                        dbc.Col(html.Label(children='Residential Units:')),
                        dbc.Col(dcc.Input(type='number',
                                            placeholder=1,
                                            id='residential_units'))
                    ]),
                    html.Br(),
                    dbc.Row([
                        dbc.Col(html.Label(children='Commercial Units:')),
                        dbc.Col(dcc.Input(type='number',
                                            placeholder=0,
                                            id='commercial_units'))
                    ]),
                    html.Br(),
                    dbc.Row([
                        dbc.Col(html.Label(children='Land Square Feet:')),
                        dbc.Col(dcc.Input(type='number',
                                            placeholder=750,
                                            id='land_square_feet'))
                    ]),
                    html.Br(),
                    dbc.Row([
                        dbc.Col(html.Label(children='Gross Square Feet:')),
                        dbc.Col(dcc.Input(type='number',
                                            placeholder=1000,
                                            id='gross_square_feet'))
                    ]),
                    html.Br(),
                    dbc.Row([
                        dbc.Col(html.Label(children='Tax Class:')),
                        dbc.Col(dcc.Dropdown(sales_res['TAX CLASS AT TIME OF SALE'].unique(),
                                            sales_res['TAX CLASS AT TIME OF SALE'].min(),
                                            id='tax_class'))
                    ]),
                    html.Br(),
                    dbc.Row([
                        dbc.Col(html.Label(children='Building Class:'), width={'order':'first'}),
                        dbc.Col(dcc.Dropdown(np.sort(sales_res['BUILDING CLASS AT TIME OF SALE'].unique()),
                                            sales_res['BUILDING CLASS AT TIME OF SALE'].min(),
                                            id='building_class'))
                    ])
                ], width=6)
            ]),
            html.Br(),
            dbc.Row([dbc.Button('Input', id='submit-val', n_clicks=0, size='sm')]),
            html.Br(),
            dbc.Row([html.Div(id='prediction output')])
        ])
    # If the user tries to reach a different page, return a 404 message
    return dbc.Container(
        [
            html.H1("Error 404:", className="text-danger"),
            html.Hr(),
            html.P(f"The pathname {pathname} was not recognised..."),
        ]
    )

@app.callback(Output('zip map', 'figure'),
            Input('borough','value'))
def pick_map(borough):
    if borough == 'Manhattan':
        return mn_fig
    elif borough == 'Bronx':
        return bx_fig
    elif borough == 'Brooklyn':
        return bk_fig   
    elif borough == 'Queens':
        return qn_fig
    else:
        return si_fig


@app.callback(Output('most-least-expensive-output', 'figure'),
              Input('most_least_expensive_input', 'value'))
def pick_most_least(most_least_expensive_input):
    if most_least_expensive_input == 'Condos':
        return fig_exp
    else:
        return fig_least

@app.callback(Output('COVID_own_output', 'figure'),
              Input('COVID_own_input', 'value'))
def pick_most_least(COVID_own_input):
    if COVID_own_input == 'Manhattan':
        return fig_mny_own
    elif COVID_own_input == 'Bronx':
        return fig_bx_own
    elif COVID_own_input == 'Brooklyn':
        return fig_bkl_own   
    elif COVID_own_input == 'Queens':
        return fig_qn_own
    else:
        return fig_sti_own

@app.callback(Output('COVID_rent_output', 'figure'),
              Input('COVID_rent_input', 'value'))
def pick_most_least(COVID_rent_input):
    if COVID_rent_input == 'Manhattan':
        return fig_mny_rent
    elif COVID_rent_input == 'Bronx':
        return fig_bx_rent
    elif COVID_rent_input == 'Brooklyn':
        return fig_bkl_rent  
    elif COVID_rent_input == 'Queens':
        return fig_qn_rent
    else:
        return fig_sti_rent

@app.callback(Output('median_sale_graph','figure'),
              Input('median_sale','value'))
def pick_median_sale_graph(median_sale):
    if median_sale == 'With Manhattan':
        return figMedMan
    elif median_sale == 'Without Manhattan':
        return figMedNoMan

@app.callback(Output('borough_thresh_output', 'figure'),
              Input('borough_thresh', 'value'))
def pick_rent_own_graph(borough_thresh):
    figThresh = create_rent_own(borough_thresh)
    return figThresh

@app.callback(Output('top_three_hoods_output', 'figure'),
              Input('top_three_hoods', 'value'))
def pick_top_hood_graph(top_three_hoods):
    fig_top_hoods = create_top_hood_graph(top_three_hoods)
    return fig_top_hoods

@app.callback(
    Output('prediction output', 'children'),
    Input('submit-val', 'n_clicks'),
    Input('neighborhood', 'value'),
    Input('zip_code', 'value'),
    Input('residential_units', 'value'),
    Input('commercial_units', 'value'),
    Input('land_square_feet', 'value'),
    Input('gross_square_feet', 'value'),
    Input('tax_class', 'value'),
    Input('building_class', 'value')
)
def update_ML_output(n_clicks,
                neighborhood, 
                zip_code, 
                residential_units,
                commercial_units,
                land_square_feet,
                gross_square_feet,
                tax_class,
                building_class):
    for input_values in [residential_units, commercial_units, land_square_feet, gross_square_feet]:
        if input_values is None:
            input_values = 0
    user_x = pd.DataFrame({'NEIGHBORHOOD': neighborhood,
                        'ZIP CODE': zip_code,
                        'RESIDENTIAL UNITS': residential_units,
                        'COMMERCIAL UNITS': commercial_units,
                        'LAND SQUARE FEET' : land_square_feet,
                        'GROSS SQUARE FEET' :  gross_square_feet,
                        'TAX CLASS AT TIME OF SALE': tax_class,
                        'BUILDING CLASS AT TIME OF SALE': building_class},
                        index=[0])
    user_dummies = pd.get_dummies(user_x)
    newpredict = user_dummies.reindex(labels = X_with_dummies.columns, axis = 1, fill_value = 0)
    user_predict = round(rf.predict(newpredict)[0], 2)

    formatted_price = "{:,.2f}".format(user_predict)
    
    return f'The predicted price is ${formatted_price}.'

@app.callback(Output('historical_events', 'figure'),
              Input('interval-component', 'n_intervals'))
def UpdateData(n):
    query_own = f'SELECT * FROM OwnPrice'
    df_update = pd.read_sql(query_own, cnxn)

    df_update['Date'] = pd.to_datetime(df_update[['year','month']].assign(DAY=1))
    monthly_df = df_update[['Date','sfrMedianPrice','condoMedianPrice','coopMedianPrice']]
    line_df = monthly_df.groupby('Date').agg('mean').rename(columns = {'sfrMedianPrice' : 'Single Family Residence', 
                                                                        'condoMedianPrice' : 'Condos',
                                                                        'coopMedianPrice' : 'Coops'})

    fig_events = px.line(line_df,
           x = line_df.index,
           y = line_df.columns)

    fig_events.update_layout(
            title = 'NYC Residential Property Average Median Prices 2010-2022',
            xaxis_title = 'Date',
            yaxis_title = 'Average Median Price',
            legend_title = 'Legend')

    fig_events.add_vrect(x0="2020-03-22", x1="2020-03-28", 
                  annotation_text="NYC Pause Program begins", annotation_position="top left",
                  fillcolor="black", opacity=0.9, line_width=5)

    fig_events.add_vrect(x0="2010-07-21",x1="2010-07-21", annotation_text="Dodd-Frank Act Passes", annotation_position="top left",
                  fillcolor="black", opacity=0.9, line_width=5)

    fig_events.add_vrect(x0="2019-06-14",x1="2019-06-14", annotation_text=f"Housing Stability &<br> Tenant Protection Act", annotation_position="top right",
                  fillcolor="black", opacity=0.9, line_width=5)

    fig_events.add_vrect(x0="2016-03-22",x1="2016-03-22", annotation_text=f"Zoning for Quality &<br> and Affordability Initiative", annotation_position="top right",
                  fillcolor="black", opacity=0.9, line_width=5)

    return fig_events




if __name__ == '__main__':
    app.run_server(debug=True)
