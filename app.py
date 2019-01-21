import os
import dash
import pandas as pd
import dash_core_components as dcc
import dash_html_components as html
import plotly.graph_objs as go
from dash.dependencies import Input, Output

df = pd.read_csv("wef_global_risk_v03.csv")



def prepare_dataframe(df):
    """ Preprocesses dataframe

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
    df_total["x_normalized"]= df_total["x"]/df_total["x_mean"]
    df_total["y_normalized"]= df_total["y"]/df_total["y_mean"]
    df_total["xy"] = df_total["x"]*df_total["y"]
    df_total["xy_normalized"] = df_total["x_normalized"]*df_total["y_normalized"]
    return df_total

df_total = prepare_dataframe(df)
df_test = df_total.loc[(df_total["year"] == 2019) ]

external_stylesheets = ['https://codepen.io/chriddyp/pen/bWLwgP.css']

app = dash.Dash(__name__, external_stylesheets=external_stylesheets)

server = app.server

# Components

# Create a trace for each risk category 

for risk_renamed in 


trace = go.Scatter(
    x = df_test["x"],
    y = df_test["y"],
    mode = 'markers'
)
data = [trace]



title = html.H2('Global Risks')
slider =     dcc.Slider(id='year-slider',
                        min=2011,
                        max=2019,
                        marks={2011:"2011",2012:"2012",2013:"2013",2014:"2014",2015:"2015",2016:"2016",2017:"2017",2018:"2018",2019:"2019"},
                        value=2019)
scatter = dcc.Graph(id="global_risk_scatter",
                    figure={"data":data})

input_box = dcc.Input(id='my-id', value='initial value', type='text')
output_label = html.Div(id='my-div')


app.layout = html.Div([
    title,
    scatter,
    slider,
    input_box,
    output_label    
])

@app.callback(
    Output(component_id='my-div', component_property='children'),
    [Input(component_id='year-slider', component_property='value')]
)
def update_output_div(input_value):
    return 'You\'ve entered "{}"'.format(input_value)

if __name__ == '__main__':
    app.run_server(debug=True)