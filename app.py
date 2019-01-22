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

df = pd.read_csv("wef_global_risk_v03.csv")


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
    return df_total

df_total = prepare_dataframe(df)

# Components


title = html.H2('Global Risks')
slider =     dcc.Slider(id='year-slider',
                        min=df_total.year.min(),
                        max=df_total.year.max(),
                        marks={str(year): str(year) for year in df['year'].unique()},
                        value=df_total.year.max())
scatter = dcc.Graph(id="global_risk_scatter",
                    style={"margin-top": "50",
                           "margin-left": "50",
                           "margin-right": "50"})


app.layout = html.Div([
    title,
    scatter,
    html.Div(slider,style={"margin-top": "50",
                           "margin-left": "50",
                           "margin-right": "50"})
])


@app.callback(
    dash.dependencies.Output('global_risk_scatter', 'figure'),
    [dash.dependencies.Input('year-slider', 'value')])
def update_figure(selected_year):
    df_filtered = df_total[df_total.year == selected_year]
    traces = []
    for i in df_filtered.category.unique():
        df_by_category = df_filtered[df_filtered['category'] == i]
        traces.append(go.Scatter(
            x=df_by_category['x_norm'],
            y=df_by_category['y_norm'],
            text=df_by_category['risk_renamed'],
            mode='markers',
            opacity=0.7,
            marker={
                'size': 15,
                'line': {'width': 0.5, 'color': 'black'},
                'color':colors[i],
                'symbol':'diamond'
            },
            name=i
        ))

    return {
        'data': traces,
        'layout': go.Layout(
            xaxis={'title': 'Normalized Likelihood','range': [-3, 3]},
            yaxis={'title': 'Normalized Impact', 'range': [-3, 3]},
            margin={'l': 40, 'b': 40, 't': 10, 'r': 10},
            legend={'x': 0, 'y': 1},
            hovermode='closest'
        )
    }




if __name__ == '__main__':
    app.run_server(debug=True)