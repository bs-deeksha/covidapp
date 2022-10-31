#!/usr/bin/env python
# coding: utf-8

import streamlit as s
import pandas as pd
import plotly.express as px
from numerize import numerize
import time

from snowflake.sqlalchemy import URL
from sqlalchemy import create_engine

print('Establishing Snowflake Connection')
snow_eng=create_engine(URL(account = 'eb83910.central-india.azure',
                        user = s.secrets['username'],
                        password = s.secrets['password'],
                        database = 'practice',
                        schema = 'public',
                        warehouse = 'practice'
                        ))

s.title('Covid Global Monthly Report')
# s.header('This is header')
# s.text('This is plain text')
# s.write("Upload your source csv file here")
# uploaded_file = s.file_uploader("Choose a file")
# df_report=pd.read_csv('C:/Users/deeksha.bs/Downloads/Streamlit_Practice/Covid_data.csv')

# @s.cache#(suppress_st_warning=True)
# start_time = time.time()

@s.experimental_memo(ttl=24*60*60)   
def load_df():
    start_time = time.time()
    # print('Establishing Snowflake Connection')
    # snow_eng=create_engine(URL(account = 'eb83910.central-india.azure',user = s.secrets['username'],password = s.secrets['password'],database = 'practice',schema = 'public',warehouse = 'practice'))
    df_report=pd.read_sql_query("select country_region,case_type,sum(cases) as cases,month,to_char(to_date(month,'yyyy-mon'),'yyyy') as year from practice.public.covid_global_monthly group by 1,2,4,5 order by to_date(month,'yyyy-mon')",snow_eng)
#     df_report=pd.read_sql_query("select * from practice.public.covid_global_report limit 10000000",snow_eng)
    # df_report=df_report.fillna(0)
    total_time = time.time() - start_time
    s.write(total_time)
    return df_report

# total_time = time.time() - start_time
# s.write(total_time)
# print("%s: %.4f ms" % (name, total_time * 1000.0))

df_report=load_df()
#Button to view full covid report as a display
if s.button('Click here to view full covid report'):
    s.write(df_report)
# else:
#     s.write('Bye')
# s.sidebar.selectbox("Select a country:",df_report['COUNTRY_REGION'].unique())

#Dropdown menu to view line charts based on the selected country

country_selection,year_selection = s.columns(2)
with country_selection:
    country=s.selectbox("Select a country:",df_report['country_region'].unique())
with year_selection:
    year=s.selectbox("Select a Year:",df_report['year'].unique())
# with case_type_sel:
#     case_type=s.selectbox("Select a case type:",df_report['case_type'].unique())
if country:
    df_country1=df_report[(df_report['country_region']==country) & (df_report['year']==year)]
    # df_country=df_report[(df_report['country_region']==country) & (df_report['year']==year) & (df_report['case_type']==case_type)]

    # df_country1=df_country.copy()
    # s.write(df_country)
    # df_country1['MONTH']=pd.to_datetime(df_country['MONTH'], format='%m/%d/%Y')
    
    #Min and Max count of cases to find out Percentage increse compared to last month
    
    Max_val_conf=df_country1[(df_country1['month']==df_country1['month'].max()) & (df_country1['case_type']=='Confirmed')].cases.sum()
    Min_val_conf=df_country1[(df_country1['month']==df_country1['month'].min()) & (df_country1['case_type']=='Confirmed')].cases.sum()
    if Min_val_conf==0 : Min_val_conf=1
    pct_conf=round(((Max_val_conf-Min_val_conf)/Min_val_conf),2)
    
    Max_val_rec=df_country1[(df_country1['month']==df_country1['month'].max()) & (df_country1['case_type']=='Recovered')].cases.sum()
    Min_val_rec=df_country1[(df_country1['month']==df_country1['month'].min()) & (df_country1['case_type']=='Recovered')].cases.sum()
    if Min_val_rec==0 : Min_val_rec=1
    pct_rec=round(((Max_val_rec-Min_val_rec)/Min_val_rec),2)
    
    Max_val_death=df_country1[(df_country1['month']==df_country1['month'].max()) & (df_country1['case_type']=='Deaths')].cases.sum()
    Min_val_death=df_country1[(df_country1['month']==df_country1['month'].min()) & (df_country1['case_type']=='Deaths')].cases.sum()
    if Min_val_death==0 : Min_val_death=1
    pct_death=round(((Max_val_death-Min_val_death)/Min_val_death),2)
    
    Max_val_sus=df_country1[(df_country1['month']==df_country1['month'].max()) & (df_country1['case_type']=='Active')].cases.sum()
    Min_val_sus=df_country1[(df_country1['month']==df_country1['month'].min()) & (df_country1['case_type']=='Active')].cases.sum()
    if Min_val_sus==0 : Min_val_sus=1
    pct_sus=round(((Max_val_sus-Min_val_sus)/Min_val_sus),2)
    
    
    # s.write(Max_val_rec,Min_val_rec,pct_rec,pct_death,pct_sus)
    monthly_button,Weekly_button = s.columns(2)
    with monthly_button:
        if s.button('Monthly'):
            fig=px.line(df_country1,x = "month", y = "cases", title = country, color = "case_type") 
            s.plotly_chart(fig)
        else:
            fig=px.line(df_country1,x = "month", y = "cases", title = country, color = "case_type") 
            s.plotly_chart(fig)
    with Weekly_button:
        if s.button('Weekly'):
            fig=px.line(df_country1,x = "week_of_year", y = "cases", title = country, color = "case_type") 
            s.plotly_chart(fig)
    
    #Linechart to display count of confirmed cases accross states as per the country selected
    # fig=px.line(df_country,x = "month", y = "cases", title = country, color = "case_type") 
    # s.plotly_chart(fig)
    
    #Metrics to show confirmed,recovered,death,suspected cases for each country along with pct
    confirmed,recovered,death,suspected = s.columns(4)
    with confirmed:
        s.metric('Total Confirmed Cases', numerize.numerize(int(df_country1[df_country1['case_type']=='Confirmed'].cases.sum())),"{:.2%}".format(pct_conf),"inverse")
    with recovered:
        s.metric('Total Recovered Cases', numerize.numerize(int(df_country1[df_country1['case_type']=='Recovered'].cases.sum())),"{:.2%}".format(pct_rec))
    with death:
        s.metric('Total Deaths', numerize.numerize(int(df_country1[df_country1['case_type']=='Deaths'].cases.sum())),"{:.2%}".format(pct_death),"inverse")
    with suspected:
        s.metric('Total Active Cases', numerize.numerize(int(df_country1[df_country1['case_type']=='Active'].cases.sum())),"{:.2%}".format(pct_sus),"inverse")

# #Minimum and maximum population variable declaration
# min=int(df_report['Population Per State'].min())
# max=int(df_report['Population Per State'].max())

# # s.write(min,max)
# #slider to display Population range of state
# values = s.slider('Select a range of Population',min,max,(min,max),10000000)
# df_pop=df_report[df_report['Population Per State'].between(values[0],values[1])]
# # s.write(df_pop)

# #pie chart to display covid cases as per the Population range
# piefig=px.pie(df_pop,"Province/State","Confirmed")
# s.plotly_chart(piefig)
# # s.write(s.secrets['secret'])


