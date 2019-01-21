import os
import dash
import pandas as pd
import dash_core_components as dcc
import dash_html_components as html

external_stylesheets = ['https://codepen.io/chriddyp/pen/bWLwgP.css']

app = dash.Dash(__name__, external_stylesheets=external_stylesheets)

server = app.server

# Components

title = html.H2('Global Risks')
dropdown = dcc.Dropdown(
                id='dropdown',
                options=[{'label': i, 'value': i} for i in ['LA', 'NYC', 'MTL']],
                value='LA'
            )



app.layout = html.Div([
    title, 
    dropdown
])

if __name__ == '__main__':
    app.run_server(debug=True)