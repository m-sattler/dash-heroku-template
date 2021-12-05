import numpy as np
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import plotly.figure_factory as ff

import dash
import dash_core_components as dcc
import dash_html_components as html
from dash.dependencies import Input, Output

external_stylesheets = ['https://codepen.io/chriddyp/pen/bWLwgP.css']

#downloading the data 

gss = pd.read_csv("https://github.com/jkropko/DS-6001/raw/master/localdata/gss2018.csv",
                 encoding='cp1252', low_memory=False, na_values=['IAP','IAP,DK,NA,uncodeable', 'NOT SURE',
                                               'DK', 'IAP, DK, NA, uncodeable', '.a', "CAN'T CHOOSE"])


#cleaning the data 
mycols = ['id', 'wtss', 'sex', 'educ', 'region', 'age', 'coninc',
          'prestg10', 'mapres10', 'papres10', 'sei10', 'satjob',
          'fechld', 'fefam', 'fepol', 'fepresch', 'meovrwrk'] 
gss_clean = gss[mycols]
gss_clean = gss_clean.rename({'wtss':'weight', 
                              'educ':'education', 
                              'coninc':'income', 
                              'prestg10':'job_prestige',
                              'mapres10':'mother_job_prestige', 
                              'papres10':'father_job_prestige', 
                              'sei10':'socioeconomic_index', 
                              'fechld':'relationship', 
                              'fefam':'male_breadwinner', 
                              'fehire':'hire_women', 
                              'fejobaff':'preference_hire_women', 
                              'fepol':'men_bettersuited', 
                              'fepresch':'child_suffer',
                              'meovrwrk':'men_overwork'},axis=1)
gss_clean.age = gss_clean.age.replace({'89 or older':'89'})
gss_clean.age = gss_clean.age.astype('float')

#markdown text for dashboard
markdown_text='''The Gender wage Gap is the concept that women get paid less than men for the equal work they do. According to
the department of labor blog post women earn about 82% of what men of equal education and skill do. The blog also mentions that this 
is across all occupations it isn't just limited to a specifc career field. According to Forbes, Women face more obstacles when trying
to advance their careers. Some of the onstacles they listed are being caregivers and needed shorter commutes to be able to coordinate 
family time or school activities for the kids. Overall both sources state that the pay gap is prevelent and we still require a lot
of work to fix it. 

The GSS data comes from the General Social Survey (GSS) created and managed by National Opinion Research Center (NORC) at 
the University of Chicago (https://www.norc.org/Pages/default.aspx).They do research on social issues such as Climate change, 
Crime, and of course the GSS. On the GSS web page they indicate that the data is collected via in-person and telephone interviews
They sample nation wide and in it's latest iteration included a Spanish version to include that population in the survey results
as well. Overall it is great representative of the current affairs in the country. 


References:
US Dept. of Labor Blog 
https://blog.dol.gov/2021/03/19/5-facts-about-the-state-of-the-gender-pay-gap

Forbes
https://www.forbes.com/sites/tomspiggle/2021/05/25/the-gender-pay-gap-why-its-still-here/?sh=2c649d177baf

GSS
http://www.gss.norc.org/About-The-GSS

University of Chicago 
https://www.norc.org/Pages/default.aspx

'''

#creating interactive table 
gss_bar = gss_clean.groupby('sex', sort=False).agg({'income':'mean','job_prestige':'mean',
                                    'socioeconomic_index':'mean', 'education':'mean'})
gss_bar = gss_bar.rename({'income':'Avg. Income',
                                   'job_prestige':'Avg. Job Prestige',
                                   'socioeconomic_index':'Avg. Socioeconomic Index',
                                   'education':'Avg. Education','sex':'Sex'}, axis=1)
gss_bar=gss_bar.reset_index()

table = ff.create_table(gss_bar)
table.show()

colpercent = round(100*pd.crosstab(gss_clean.male_breadwinner, gss_clean.sex, normalize='columns'),2).reset_index()
colpercent = pd.melt(colpercent, id_vars = 'male_breadwinner')
colpercent = colpercent.rename({'value':'Percent'}, axis=1)

#creating first bar graph 
fig_1 = px.bar(colpercent, x='male_breadwinner', y='Percent', color='sex',
            labels={'male_breadwinner':'Male as the Breadwinner', 'Percent':'Percent'},
            title = 'Agreement with Male being the Breadwinner',
            hover_data = ['Percent', 'sex'],
            barmode = 'group')
fig_1.update_layout(showlegend=True)
fig_1.update(layout=dict(title=dict(x=0.5)))

#scatterplot
fig_2 = px.scatter(gss_clean.head(200), x='job_prestige', y='income', color = 'sex', 
                 trendline='ols',
                 height=600, width=600,
                 labels={'job_prestige':'Job Prestige Ranking', 
                        'income':'Annual Income'},
                 hover_data=['education', 'socioeconomic_index'])
fig_2.update(layout=dict(title=dict(x=0.5)))

#box plot 1 
fig_3 = px.box(gss_clean, x='income', y = 'sex', color = 'sex',
                   labels={'income':'Annual Income', 'sex':''})
fig_3.update(layout=dict(title=dict(x=0.5)))
fig_3.update_layout(showlegend=False)

#box plot 2
fig_4 = px.box(gss_clean, x='job_prestige', y = 'sex', color = 'sex',
                   labels={'job_prestige':'Job Prestige Ranking', 'sex':''})
fig_4.update(layout=dict(title=dict(x=0.5)))
fig_4.update_layout(showlegend=False)

#cleaning dataframe for grouping set-up 
df=gss_clean[["income","sex","job_prestige"]]

df['prestige_group'] = pd.cut(df.job_prestige, 6, labels=("Cat_1","Cat_2", "Cat_3","Cat_4","Cat_5",
                                                                     "Cat_6"))
df_clean=df

#removing all NA values
df_clean = df_clean[~df_clean.income.isnull()]
df_clean = df_clean[~df_clean.sex.isnull()]
df_clean = df_clean[~df_clean.job_prestige.isnull()]
df_clean = df_clean[~df_clean.prestige_group.isnull()]

df_clean['prestige_group'] = df_clean['prestige_group'].cat.reorder_categories(['Cat_1','Cat_2','Cat_3','Cat_4',
                                                                               'Cat_5','Cat_6'])

fig_5 = px.box(df_clean, x='sex', y='income', color='sex', 
             facet_col='prestige_group',
              facet_col_wrap=2,
             hover_data = ['sex'],
            labels={'sex':'', 'income':'Annual Income'})
fig_5.update(layout=dict(title=dict(x=0.5)))
fig_5.update_layout(showlegend=False)



### Create app
app = dash.Dash(__name__, external_stylesheets=external_stylesheets)
server = app.server

app.layout = html.Div(
    [
        html.H1("Dashboard Looking at Income and Job Prestige between Men and Women in the GSS Data "),
        
        dcc.Markdown(children = markdown_text),
        
        html.H2("Table Looking at the Average Values of Income, Job Prestige, Socioeconomic Index, and Education"),
        
        dcc.Graph(figure=table),
        
        html.H2("Showing the Level of Agreement with the Statment that the Man should be the Breadwinner"),
        
        dcc.Graph(figure=fig_1),
        
        html.H2("Comparing Job Prestige and Income between Men and Women"),
        
        dcc.Graph(figure=fig_2),

        html.Div([
            
            html.H2("Distibution of Income by Gender"),
            
            dcc.Graph(figure=fig_3)
            
        ], style = {'width':'48%', 'float':'left'}),
        
        html.Div([
            
            html.H2("Distibution of Job Prestige by Gender"),
            
            dcc.Graph(figure=fig_4)
            
        ], style = {'width':'48%', 'float':'right'}),
        
        html.H2("Income by Gender over 6 Job Prestige Categories"),
        
        dcc.Graph(figure=fig_5),
    
    ]
)

if __name__ == '__main__':
    app.run_server(debug=True, port=8050, host='0.0.0.0')
