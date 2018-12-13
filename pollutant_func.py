#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Thu Dec 13 14:00:24 2018

@author: CharleneCuellarVite
"""

def max_all_sites(df):
    '''
    Since all counties have multiple measuring sites, this function returns the max pollutant value
    from all the sites in each county every day.
    
    Input-
    df: Complete Data Frame
    
    Output-
    county_data: DataFrame where the index are the dates, and columns are all the counties. the entries
                    are the max[pollutant value] from all sites on that day
                    
                    [County1] [County2]
            [Date1]   max val 
            [Date2] 
              
    '''

    import pandas as pd
    
    my_dates = list(df.index.unique())
    all_my_counties = list(df['COUNTY'].unique())
    county_data = pd.DataFrame(index=pd.to_datetime(my_dates),columns=all_my_counties) #set empty DataFrame

    for d in my_dates:

        current_day_df = df.loc[d]

        if type(current_day_df['COUNTY'])==str: #only one site was recorded on a specific day
            my_counties = current_day_df['COUNTY']
            county_df = current_day_df
            val = county_df[3]
            county_data.loc[pd.to_datetime(d)][c]=val

        else:
            my_counties = list(current_day_df['COUNTY'].unique())

            for c in my_counties:
                county_df = current_day_df.loc[current_day_df['COUNTY']==c]
                val = county_df.iloc[:,3].max()
                county_data.loc[pd.to_datetime(d)][c]=val
    
    return county_data


def county_pollutants(county,all_pollutants_df,pol_list):
    '''
    Place pollutants into one DataFrame for that county
    
    Output-
                [Pollutant1] [Pollutant2]
        [Date1]     
        [Date2]
    '''
    import pandas as pd
    
    county_pollutants_df = pd.DataFrame(index=all_pollutants_df.index,columns=pol_list) #empty NaN DF

    for p in pol_list:
        if county in list(all_pollutants_df[p].columns.values): #sometimes not all pollutants were recorded for
                                                                #that county
            temp_series = all_pollutants_df[p][county]
            county_pollutants_df[p]=temp_series
            
    return  county_pollutants_df 


def plot_pollutants(county,all_pollutants_df,pol_list):
    
    from matplotlib import pyplot as plt
    
    county_pollutants_df = county_pollutants(county,all_pollutants_df,pol_list)

    #plotting====
    #dictionary to hold all info for plotting
    pollutant_info={'co':['ppm','Carbon monoxide levels for %s'%county],
                  'no2':['ppb','Nitrogen dioxide (NO2) levels for %s'%county],
                  'ozone':['ppm','Ozone levels for %s'%county],
                  'pb':['ug/m3','Lead levels for %s'%county],
                  'pm2_5':['ug/m3','PM2.5 levels for %s'%county],
                  'pm10':['ug/m3','PM10 levels for %s'%county],
                  'so2':['ppb','Sulfur dioxide levels for %s'%county]}
    
    for p in pol_list:
    
        if county_pollutants_df[p].isnull().all(): #if there is no data for a pollutant, skip
            continue

        fig, axes = plt.subplots(figsize=(15, 5))

        axes.plot(county_pollutants_df.index, list(county_pollutants_df[p]),'.-')
        axes.set_xlabel('Date')
        axes.set_ylabel(pollutant_info[p][0])
        axes.set_title(pollutant_info[p][1])
        
        plt.show(fig)

def outlier_dates(cy,alp,all_pollutants_df,pol_list):
    '''
    cy = county
    alp = alpha value for outlier function
    '''
    from outliers import smirnov_grubbs as grubbs

    county_pollutants_df = county_pollutants(cy,all_pollutants_df,pol_list)
    
    pollutant_info={'co':['ppm','Carbon monoxide'],
                          'no2':['ppb','Nitrogen dioxide (NO2)'],
                          'ozone':['ppm','Ozone'],
                          'pb':['ug/m3','Lead'],
                          'pm2_5':['ug/m3','PM2.5'],
                          'pm10':['ug/m3','PM10'],
                          'so2':['ppb','Sulfur dioxide']}

    for p in pol_list:
        outliers = grubbs.max_test_outliers(list(county_pollutants_df[p]), alpha=alp)

        #When did this happen?
        if len(outliers)!=0:
            d = str(county_pollutants_df[county_pollutants_df[p]==outliers[0]].index[0])
            print('The %s %s outlier occured on %s'%(cy,pollutant_info[p][1],d[0:10]))

def plot_map(pollutant,date,all_pollutants_df):
    '''
    Output a map of all the counties and display the pollutant levels on a specific day
    '''
    from bokeh.sampledata.us_counties import data as counties
    
    #The Bokeh counties data has 58 counties listed in CA, but EPA never has all 58 counties
    #for the pollutants. Here I am copying all the lat/long data for the counties that I have======

    #from original BOKEH SAMPLE
    counties = {code: county for code, county in counties.items() if county["state"] == "ca"}

    county_xs = [county["lons"] for county in counties.values()]
    county_ys = [county["lats"] for county in counties.values()]
    county_names = [county['name'] for county in counties.values()]
    
    my_counties = all_pollutants_df[pollutant].columns
    
    #Change Log/Lat to use my_counties
    county_xs_new = []
    county_ys_new = []
    for c in my_counties:
        county_xs_new.append(county_xs[county_names.index(c)])
        county_ys_new.append(county_ys[county_names.index(c)])
    
    #Plot =========
    from bokeh.io import show,export_png
    # export_png is dependent on selenium. run:
    # conda install selenium phantomjs pillow

    from bokeh.models import LinearColorMapper, BasicTicker, ColorBar
    from bokeh.palettes import Viridis6 as palette
    from bokeh.plotting import figure
    
    color_mapper = LinearColorMapper(palette=palette)

    data=dict(
        x=county_xs_new,
        y=county_ys_new,
        name=my_counties,
        rate=list(all_pollutants_df[pollutant].loc[date]),
        )

    TOOLS = "pan,wheel_zoom,reset,hover,save"
    
    pollutant_info={'co':['ppm','Carbon monoxide'],
                  'no2':['ppb','Nitrogen dioxide (NO2)'],
                  'ozone':['ppm','Ozone'],
                  'pb':['ug/m3','Lead'],
                  'pm2_5':['ug/m3','PM2.5'],
                  'pm10':['ug/m3','PM10'],
                  'so2':['ppb','Sulfur dioxide']}

    p = figure(
        title="California %s, %s"%(pollutant_info[pollutant][1],date), tools=TOOLS,
        x_axis_location=None, y_axis_location=None,
        tooltips=[
            ("Name", "@name"), ("%s"%pollutant_info[pollutant][1], "@rate %s"%pollutant_info[pollutant][0]), ("(Long, Lat)", "($x, $y)")
            ])
    p.grid.grid_line_color = None
    p.hover.point_policy = "follow_mouse"

    p.patches('x', 'y', source=data,
        fill_color={'field': 'rate', 'transform': color_mapper},
        fill_alpha=0.7, line_color="white", line_width=0.5)
    
    color_bar = ColorBar(color_mapper=color_mapper, ticker=BasicTicker(),
                     label_standoff=12, border_line_color=None, location=(0,0))
    p.add_layout(color_bar, 'right')

        #export_png(p,'Results/CA_ozone_%s.png'%t.date())
    show(p)