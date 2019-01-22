import os
import dash
import pandas as pd
import dash_core_components as dcc
import dash_html_components as html
import plotly.graph_objs as go
from dash.dependencies import Input, Output


external_stylesheets = ['https://codepen.io/chriddyp/pen/bWLwgP.css']

colors = {"Societal":"#e20820",
          "Environmental":"#1b814b",
          "Economic":"#187fc0",
          "Geopolitical":"#e3731b",
          "Technological":"#87246d"}

app = dash.Dash(__name__, external_stylesheets=external_stylesheets)

server = app.server

df = pd.read_csv("wef_global_risk_v04.csv")


def prepare_dataframe(df):
    """ Preprocesses dataframe
    -Normalizes likelihood and impact
    -Creates a multiplied likelihood times
    impact.
    -Adds ranks per year. 


    """
    df_average = df.groupby(by="year").mean()[["x","y"]]
    df_average.rename(columns={"x":"x_mean",
                               "y":"y_mean"},
                      inplace=True)
    df_total = pd.merge(left=df,
                        right=df_average,
                        how="left",
                        left_on="year",
                        right_index=True)
    df_std = df.groupby(by="year").std()[["x","y"]]
    df_std.rename(columns={"x":"x_std",
                               "y":"y_std"},
                      inplace=True)
    df_total = pd.merge(left=df_total,
                        right=df_std,
                        how="left",
                        left_on="year",
                        right_index=True)

    df_total["x_norm"]= (df_total["x"]-df_total["x_mean"])/df_total["x_std"]
    df_total["y_norm"]= (df_total["y"]-df_total["y_mean"])/df_total["y_std"]
    df_total["xy"] = df_total["x"]*df_total["y"]
    df_total["xy_norm"] = df_total["x_norm"]*df_total["y_norm"]

    df_total["x_rank"] = df_total.groupby("year")["x"].rank(axis=0,method="dense",ascending=False)
    df_total["y_rank"] = df_total.groupby("year")["y"].rank(axis=0,method="dense",ascending=False)
    df_total["xy_rank"] = df_total.groupby("year")["xy"].rank(axis=0,method="dense",ascending=False)
    df_total["xy_norm_rank"] = df_total.groupby("year")["xy_norm"].rank(axis=0,method="dense",ascending=False)
    df_total["text"] = df_total.apply(create_label,axis=1)
    return df_total

def create_label(row):
    text = row["risk_renamed"] + ", " + str(row["year"])
    return text

def populate_dropdown(df):
    """ Populate dropdown menu

    Args:
        df(dataframe): dataframe with options
    """
    options = []

    all_risks = list(df.risk_renamed.unique())
    if all_risks:
        all_risks.sort()
        for item in all_risks:
            options.append({"label":item,"value":item})
        return options
    else:
        return options

df_total = prepare_dataframe(df)

options = populate_dropdown(df_total)

# Components


title = html.H2('World Economic Forum Global Risks')

dropdown = dcc.Dropdown(id="dropdown",
                        options=options,
                        value=["Water crises","Extreme weather events"],
                        multi=True)

slider = dcc.RangeSlider(id='year-slider',
                         min=df_total.year.min(),
                         max=df_total.year.max(),
                         marks={str(year): str(year) for year in df['year'].unique()},
                         value=[df_total.year.max()-2,df_total.year.max()]
                         )

scatter = dcc.Graph(id="global_risk_scatter",
                    style={"margin-top": "50",
                           "margin-left": "50",
                           "margin-right": "50",
                           "height": 600})

line = dcc.Graph(id="global_risk_line",
                 style={"margin-top": "200",
                        "margin-left": "50",
                        "margin-right": "50",
                        "height": 600})


footer = dcc.Markdown("""
For each of the 30* [global risks](https://www.weforum.org/reports/the-global-risks-report-2019), respondents
were asked to assess (1) the
likelihood of the risk occurring
globally within the next 10 years,
and (2) its negative impact for
several countries or industries
over the same timeframe. 

The risks are categorized:
1. Economic (Blue)  
1. Societal (Red)  
1. Environmental (Green)  
1. Technological (Purple)  
1. Geopolitical (Orange)  

Source: [World Economic Forum.](https://www.weforum.org/reports/the-global-risks-report-2019)   
Author: Rutger Hofste.  
Infographics might contain errors.  
Source Code: [GitHub](https://github.com/rutgerhofste/wef-app)  
Download data (see WEF license): [GitHub](https://github.com/rutgerhofste/wef-app/blob/master/wef_global_risk_v04.csv)

*50 risks in 2012 and 2013
""")


filter_component = html.Div([html.H6("Select Risks"),
                             dropdown,
                             html.H6("Select Years"),
                             slider],
                             style={"margin-top": "50",
                                    "margin-left": "50",
                                    "margin-right": "50"})



app.layout = html.Div([
    title,
    filter_component,
    scatter,
    line,
    footer
])


@app.callback(
    dash.dependencies.Output('global_risk_scatter', 'figure'),
    [dash.dependencies.Input('year-slider', 'value'),
     dash.dependencies.Input('dropdown','value')])
def update_figure(slider_years,dropdown_values):
    df_filtered = df_total[(df_total.year >= slider_years[0]) & (df_total.year <= slider_years[1])]
    traces = []
    risks = list(df_filtered.risk_renamed.unique())
    if risks:
        risks.sort()
    else:
        pass

    for risk in risks:
        df_by_risk= df_filtered[df_filtered['risk_renamed'] == risk]

        category = df_by_risk["category"].iloc[0]

        traces.append(go.Scatter(
            x=df_by_risk['x_norm'],
            y=df_by_risk['y_norm'],
            text= df_by_risk["text"],
            mode='lines+markers',
            opacity=0.2,
            marker={
                'size': 15,
                'line': {'width': 0.5, 'color': 'black'},
                'color': colors[category],
                'symbol':'diamond-open'
            },
            name=risk,
            showlegend=False
        ))

    for dropdown_value in dropdown_values:
        df_by_risk = df_total[(df_total.year >= slider_years[0]) & (df_total.year <= slider_years[1]) & (df_total.risk_renamed==dropdown_value) ]
        if df_by_risk.shape[0] >0 :
            category = df_by_risk["category"].iloc[0]          
            traces.append(go.Scatter(
                x=df_by_risk['x_norm'],
                y=df_by_risk['y_norm'],
                text= df_by_risk["text"],
                mode='lines+markers',
                opacity=1,
                marker={
                    'size': 15,
                    'line': {'width': 0.5, 'color': 'black'},
                    'color': colors[category],
                    'symbol':'diamond'
                },
                name=risk,
                showlegend=False
            ))

    return {
        'data': traces,
        'layout': go.Layout(
            xaxis={'title': 'Normalized Likelihood','range': [-3, 3],'fixedrange': True},
            yaxis={'title': 'Normalized Impact', 'range': [-3, 3],'fixedrange': True},
            margin={'l': 40, 'b': 40, 't': 10, 'r': 10},
            hovermode='closest'
        )
    }

@app.callback(
    dash.dependencies.Output('global_risk_line', 'figure'),
    [dash.dependencies.Input('year-slider', 'value'),
     dash.dependencies.Input('dropdown','value')])
def update_line_figure(slider_years,dropdown_values):
    traces_lines = []


    risks = list(df_total.risk_renamed.unique())
    if risks:
        risks.sort()
    else:
        pass

    for risk in risks:
        df_by_risk= df_total[df_total['risk_renamed'] == risk]
        category = df_by_risk["category"].iloc[0]

        traces_lines.append(go.Scatter(
            x=df_by_risk['year'],
            y=df_by_risk['xy_rank'],
            text= df_by_risk["text"],
            mode='lines+markers',
            opacity=0.2,
            marker={
                'size': 15,
                'line': {'width': 0.5, 'color': 'black'},
                'color': colors[category],
                'symbol':'diamond-open'
            },
            name=risk,
            showlegend=False
        ))


    for dropdown_value in dropdown_values:
        df_filtered = df_total[(df_total.year >= slider_years[0]) & (df_total.year <= slider_years[1])]
        df_by_risk= df_filtered[df_filtered['risk_renamed'] == dropdown_value]
        category = df_by_risk["category"].iloc[0]
        if category:
            traces_lines.append(go.Scatter(
                x=df_by_risk['year'],
                y=df_by_risk['xy_rank'],
                text= df_by_risk["text"],
                mode='lines+markers',
                opacity=1,
                marker={
                    'size': 15,
                    'line': {'width': 0.5, 'color': 'black'},
                    'color': colors[category],
                    'symbol':'diamond'
                },
                showlegend=False)
            )            
    

    return {"data":traces_lines,
            'layout': go.Layout(
                xaxis={'title': 'year','range': [2012, 2019],'fixedrange': True},
                yaxis={'title': 'Risks ranked by likelihood*impact', 'range': [30,-1],'fixedrange': True},
                margin={'l': 40, 'b': 40, 't': 10, 'r': 10},
                hovermode='closest',
                modebar={})
            }


if __name__ == '__main__':
    app.run_server(debug=True)