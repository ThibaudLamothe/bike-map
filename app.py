############################################################################################
########################################## IMPORTS #########################################
############################################################################################

# Classic libraries
import os
import numpy as np
import pandas as pd

# Logging information
import logging
import logzero
from logzero import logger

# Dash imports
import dash
import dash_core_components as dcc
import dash_html_components as html
from dash.dependencies import Input, Output

# Plotly imports 
import plotly.express as px
import plotly.graph_objects as go

############################################################################################
########################################## APP #############################################
############################################################################################

# Deployment information
PORT = 8050

# Creating app
app = dash.Dash(
    __name__, meta_tags=[{"name": "viewport", "content": "width=device-width"}]
)

# Associating server
server = app.server
app.title = 'Bike Expedition'
app.config.suppress_callback_exceptions = True


############################################################################################
########################################## DATA ############################################
############################################################################################


def prepare_itineraire():
    
    # Define cities
    paris = ("Paris", 48.8588377,2.2770205)
    compiegne = ("Compiegne", 49.4005952,2.8198382)
    reims = ("Reims", 49.4005952,2.8198382)
    cm = ("Charleville-Mézières", 49.7801824,4.6603386)
    charleroi  = ("Charleroi", 50.422914,4.3575706)
    bruxelles = ("Bruxelles", 50.8549541,4.3053506)
    st_quentin = ("St-Quentin", 49.8476282,3.2440442)
    mons = ("Mons", 50.445754,3.8996656)
    maubeuge = ("Maubeuge", 50.2834202,3.9260861)

    # Define itineeraries
    it_1 = [paris, compiegne, reims, cm, charleroi, bruxelles]
    it_2 = [paris, compiegne, st_quentin, mons, bruxelles]
    it_3 = [paris, compiegne, st_quentin, maubeuge, bruxelles]

    return {
        "dfs":{
            it : pd.DataFrame({
                "city":[i[0] for i in itineraire],
                "lat":[i[1] for i in itineraire],
                "lon":[i[2] for i in itineraire]
                }) for it, itineraire in zip(['it_1', 'it_2', 'it_3'], [it_1, it_2, it_3])
        },
        "it_1": {
            "it":it_1,
            "name":"Itineraire 1",
            "days":["J1", "J2", "J3", "J4", "J5"],
            "dist": [85, 100, 85, 90, 75],
            "color": 'red'
        },
        "it_2": {
            "it":it_2,
            "name":"Itineraire 2",
            "days":["J1", "J2", "J3", "J4"],
            "dist": [85, 70, 95, 70],
            "color": 'green'
        },
        "it_3": {
            "it":it_3,
            "name":"Itineraire 3",
            "days":["J1", "J2", "J3", "J4"],
            "dist": [85, 70, 80, 90],
            "color": 'yellow'
        }
    }
DATA = prepare_itineraire()


############################################################################################
######################################### LAYOUT ###########################################
############################################################################################


def prepare_picture(name):
    return html.Div(
            className='teammate',
            children=[
                html.Img(src=app.get_asset_url('team/{}.png'.format(name.lower())), width=40, height=40),
                html.Span(name)
            ]
        )

team = html.Div(
    id='platforms_links',
    children=[                   
        prepare_picture("Gabriel"),
        prepare_picture("Sophie"),
        prepare_picture("Zhe"),
        prepare_picture("Ines"),
        prepare_picture("Romain"),
        prepare_picture("Jordan"),
        prepare_picture("Thibaud")
    ]
)

dropdown_itineraire = dcc.Dropdown(
    id='itinerary-dropdown',
    options=[
        {'label': DATA[it]['name'] + ' : ' + ' - '.join([i[0] for i in DATA[it]['it']]), 'value': it} for it in ['it_1', "it_2", 'it_3']
    ],
    value='it_1'
)

app.layout = html.Div(
    children=[

        # HEADER
        html.Div(
            className="header",
            children=[
                html.H1("Bike expedition 🚴‍♀️ - Discover the Northern-East France with us !", className="header__text"),
                html.Span('From 2020/08/24 to 2020/08/28, with our full team'),
            ],
        ),

        # CONTENT
        html.Section([

            # Team pictures
            team,
            
            # Itinerary selection
            html.Br(),
            html.P(children=[
                'Let\'s discover our multiple itineraries',
                html.A(
                    '(More here)',
                    href="https://docs.google.com/spreadsheets/d/1fMUApe4lpArK-PGnJKkm4WZqVGBmL3o9OVT5d2t2bbY/edit#gid=0"
                    )
                ]),
            dropdown_itineraire,
            
            # Line 1 : KPIS 
            html.Div(
                id='kpis',
                children = [ 
                    html.Div(id='kpi_1', className='mini_container'),
                    html.Div(id='kpi_2', className='mini_container')
                ],
            ),
        
            # Line 2 : MAP
            html.Div(
                id='graph_line',
                children = [
                    dcc.Graph(id='bike-map', config={'scrollZoom': False}),
                    dcc.Graph(id='histo-km'),
                ],
            ),
            # html.Br(),
        ]),
    ],
)
############################################################################################
######################################## CALLBACKS #########################################
############################################################################################


# Update KPIS
@app.callback(
    [Output(component_id='kpi_1', component_property='children'),
    Output(component_id='kpi_2', component_property='children')],
    [Input(component_id='itinerary-dropdown', component_property='value')]
)
def kpi_prep(input_value, data=DATA):
    kpi_1 = [' 🏅 Full km', html.Br(), np.sum(DATA[input_value]['dist'])]
    kpi_2 = [' 📅 Number of days', html.Br(), len(DATA[input_value]['dist'])]
    return kpi_1, kpi_2


# Update HISTO
@app.callback(
    Output(component_id='histo-km', component_property='figure'),
    [Input(component_id='itinerary-dropdown', component_property='value')]
)
def update_output_div(input_value, data=DATA):
    x = DATA[input_value]['days']
    y = DATA[input_value]['dist']
    data = [go.Bar(x=x, y=y)]
    layout = {
        "title":"Nombre de KM parcourus par jour",
        "paper_bgcolor":'rgba(0,0,0,0)',
        "plot_bgcolor":'rgba(0,0,0,0)'
        }
    return {'data':data, 'layout':layout}


# Update MAP
@app.callback(
    Output(component_id='bike-map', component_property='figure'),
    [Input(component_id='itinerary-dropdown', component_property='value')]
)
def update_output_map(input_value, data=DATA):
    df = DATA['dfs'][input_value]
    df['color'] = DATA[input_value]['color']

    
    fig = go.Figure(go.Scattermapbox(
        mode = "markers+lines",
        lon = df['lon'].values,
        lat = df['lat'].values,
        # color = df['color'].values,
        marker = {'size': 10}
        ))

    fig.update_layout(
    margin ={'l':0,'t':0,'b':0,'r':0},
    mapbox = {
        "style":"stamen-terrain",
        "zoom":5,
        'center': {'lat': 48.8588, 'lon': 2.2770},
        # 'zoom': 1
        }
        )
    return fig


############################################################################################
######################################### RUNNING ##########################################
############################################################################################

if __name__ == "__main__":
    
    # Display app start
    logger.error('*' * 80)
    logger.error('App initialisation')
    logger.error('*' * 80)

    # Starting flask server
    app.run_server(debug=True, port=PORT)
    