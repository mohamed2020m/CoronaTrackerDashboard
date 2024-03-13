import plotly.graph_objs as go
import dash
import dash_core_components as dcc
import dash_html_components as html
from dash.dependencies import Input, Output
from theme import theme
import dash_bootstrap_components as dbc
from helpers import plot_continent_data, plot_top_k_countries, plot_boxplots



def load_display_data(data, total_cases, total_deaths, total_recoveries, fig, init_continent_fig, init_k_countries_plot, init_box_fig, init_dount_fig, gh):
    # Initialize the Dash app
    app = dash.Dash(__name__)


    app.layout = html.Div(
        style={'backgroundColor': theme['background_page'], 'color': theme['text'], 'padding': '20px'}, id="container",
        children=[
            # Title
            html.Div(
                children=[
                    html.H1("Corona Tracker Dashboard", id="title", style={"text-align": "center", "fontFamily": theme["font_family_header"], "color": theme["accent"]}),
                    html.I(className="fas fa-virus", style={'width': "50px"})
                ],
                style={
                    'textAlign': 'center', 
                    'fontSize': '24px',
                    'display': 'flex', 
                    'justifyContent': 'center', 
                    'alignItems': 'center',
                }
            ),

            html.Div(style={'margin': 50}),
            
            html.Div(
                style={
                    'display': 'flex'
                }, 
                children=[
                    html.Div(
                        style={
                            "width" : "25%",
                            'margin-right' : '10px',
                            'flex-direction': 'column',
                            'justifyContent': 'center', 
                            'alignItems': 'center'
                        }, 
                        children=[
                            html.Div(
                                style={
                                    'textAlign': 'center', 
                                    'margin': '10px', 
                                    'padding': '20px', 
                                    'border': '1px solid white', 
                                    'background': '#cc1b35',
                                    'borderRadius': '8px', 
                                    'boxShadow': '2px 2px 10px rgba(0,0,0,0.1)', 
                                    'width': '200px',
                                }, 
                                children=[
                                    html.H2('Total Deaths', style={'color': 'white'}),
                                    html.P(total_deaths, style={'fontSize': '24px', 'borderRadius': '8px', 'background': 'white','color': '#D32F2F'}),
                                ]
                            ),
                            html.Div(
                                style={
                                    'textAlign': 'center', 
                                    'margin': '10px', 
                                    'padding': '20px', 
                                    'border': '1px solid white', 
                                    'borderRadius': '8px', 
                                    'boxShadow': '2px 2px 10px rgba(0,0,0,0.1)', 
                                    'width': '200px',
                                    'background' : '#186e3c'
                                },
                                children=[
                                    html.H2('Total Recoveries', style={'color': 'white'}),
                                    html.P(total_recoveries, style={'fontSize': '24px', 'borderRadius': '8px', 'background': 'white','color': '#388E3C'})
                                ]
                            ),
                            html.Div(
                                style={
                                    'textAlign': 'center', 
                                    'margin': '10px', 
                                    'padding': '20px', 
                                    'border': '1px solid white', 
                                    'borderRadius': '8px', 
                                    'boxShadow': '2px 2px 10px rgba(0,0,0,0.1)', 
                                    'width': '200px',
                                    'background' : '#101e70'
                                }, 
                                children=[
                                    html.H2('Total Cases', style={'color': 'white'}),
                                    html.P(total_cases, style={'fontSize': '24px', 'borderRadius': '8px', 'background': 'white','color': '#1976D2'})
                                ]
                            )
                        ]
                    ),
                    html.Div(
                        style={
                            "width" : "75%"
                        }, 
                        children=[
                            html.Br(),
                            
                            dcc.Graph(
                                id='totalcases_by_totaldeath_for_each_country',
                                figure=fig
                            ),
                            html.H5("TotalCases and TotalDeath By Country", style={"text-align": "center", "fontFamily": theme["font_family_header"], "color": theme["text"]}),
                        ]
                    ),
                ]
            ),
            
            
            html.Div(style={'margin': 100}),
            
            html.Div([
                dbc.Row(
                    style={"display": 'flex'},
                    children = [ 
                        dbc.Col(
                            html.Div([
                                dcc.Dropdown(
                                    id="select_keyword",
                                    options=[
                                        dict(label="Today's Data", value="New"),
                                        dict(label="Total Data", value="Total")
                                    ],
                                    multi=False,
                                    value="New",
                                    style={ "color": theme["text"], 'margin-bottom':'10px'}
                                ),
                                dcc.Graph(id="continent_corona_bar", figure=init_continent_fig),
                                html.H5("Corona Cases/Recovered/Deaths by Continent", style={"text-align": "center", "fontFamily": theme["font_family_header"], "color": theme["text"]}),
                            ], style={ 'padding': theme['card_padding'], 'borderRadius': theme['card_border']['radius'], 'margin': theme['card_margin']}),
                            width={"size": 6},  
                            style={"width": "50%"},
                        ),
                        dbc.Col(
                            html.Div([
                                html.Div(children=[    
                                    dcc.Dropdown(
                                        id="select_attribute",
                                        options=[
                                            dict(label="Total Cases", value='TotalCases'),
                                            dict(label="New Cases", value='NewCases'),
                                            dict(label="Total Cases per 1M population", value='Tot\xa0Cases/1M pop'),
                                            dict(label="Active Cases", value='ActiveCases'),
                                            dict(label="Serious, Critical Cases", value='Serious,Critical'),
                                            dict(label="Total Deaths", value='TotalDeaths'),
                                            dict(label="New Deaths", value='NewDeaths'),
                                            dict(label="Deaths per 1M population", value='Deaths/1M pop'),
                                            dict(label="Total Recovered", value='TotalRecovered'),
                                            dict(label="New Recovered", value='NewRecovered'),
                                            dict(label="Total Tests", value='TotalTests'),
                                            dict(label="Tests per 1M population", value='Tests/1Mpop')
                                        ],
                                        multi=False,
                                        value="TotalCases",
                                        style={"width": "100%", 'display': 'inline-block',"color": theme["text"]}
                                    ),
                                    dcc.Dropdown(id="select_k_countries",
                                        options=[
                                            dict(label="Top 5", value=5),
                                            dict(label="Top 10", value=10),
                                            dict(label="Top 25", value=25),
                                            dict(label="Top 50", value=50),
                                        ],
                                        multi=False,
                                        value=10,
                                        style={"width": "100%", 'display': 'inline-block', "color": theme["text"]}
                                    ),
                                ], style={'display': 'flex'}),
                                dcc.Graph(id="k_countries_sorted", figure=init_k_countries_plot),
                                html.H5("Visualize Countries by attribute.", style={"text-align": "center", "fontFamily": theme["font_family_header"], "color": theme["text"]}),
                            ], style={ 'padding': theme['card_padding'], 'borderRadius': theme['card_border']['radius'], 'margin': theme['card_margin']}),
                            width={ "size": 6},  
                            style={"width": "50%"}
                        )
                    ]
                ),
            ]),

            html.Div([
                dbc.Row(
                    style={"display": 'flex'},
                    children = [ 
                        dbc.Col(
                            html.Div([
                                dcc.Dropdown(
                                    id="select_box_attribute",
                                    options=[
                                        dict(label="Deaths per 1M population", value='Deaths/1M pop'),
                                        dict(label="Tests per 1M population", value='Tests/1Mpop')
                                    ],
                                    multi=False,
                                    value="Deaths/1M pop",
                                    style={"color": theme["text"], 'margin-bottom':'10px'}
                                ),
                                dcc.Graph(id="continent_box_plot", figure=init_box_fig),
                                html.H5("BoxPlot to explain the distribution of the variables", style={"text-align": "center", "fontFamily": theme["font_family_header"], "color": theme["text"]}),
                            ], 
                            style={'padding': theme['card_padding'], 'borderRadius': theme['card_border']['radius'], 'margin': theme['card_margin']}),
                            width={"size": 6},  
                            style={"width": "50%"},
                        ),
                        dbc.Col(
                            html.Div([
                                dcc.Dropdown(
                                    id='country-dropdown',
                                    options=[{'label': country, 'value': country} for country in data.index],
                                    value='USA',
                                    clearable=False,
                                    style={"color": theme["text"], 'margin-bottom':'10px'}
                                ),
                                dcc.Graph(id="covid_donut_graph", figure=init_dount_fig),
                                html.H5("COVID-19 Distribution by Country", style={"text-align": "center", "fontFamily": theme["font_family_header"], "color": theme["text"]}),
                            ], 
                            style={ 'padding': theme['card_padding'], 'borderRadius': theme['card_border']['radius'], 'margin': theme['card_margin']}),
                            width={"size": 6},  
                            style={"width": "50%"},
                        )
                    ]
                ),
            ]),
            

            html.Div([
                dcc.Graph(id="gh", figure=gh),
                html.H5("COVID-19 Impact Analysis: Total Cases vs. Mortality Rate per Million, Highlighted by Population and Testing Capacity", style={"text-align": "center", "fontFamily": theme["font_family_header"], "color": theme["text"]}),
                ], 
                style={ 'padding': theme['card_padding'], 'borderRadius': theme['card_border']['radius'], 'margin': theme['card_margin']}
            ), 
            
            html.Div([
                html.P("All right reserved for Mohamed Essabir", style={'text-align':'center'})
            ]),
        ]
    )



    # Defining the application callbacks

    @app.callback(
        Output("continent_corona_bar", "figure"),
        Input("select_keyword", "value")
    )
    def update_continent_corona_bar(value):
        return plot_continent_data(data, keyword=value)


    @app.callback(
        Output("k_countries_sorted", "figure"),
        Input("select_attribute", "value"),
        Input("select_k_countries", "value")
    )
    def update_k_countries_sorted(attribute, n_countries):
        return plot_top_k_countries(data, n_countries, attribute)


    @app.callback(
        Output("continent_box_plot", "figure"),
        Input("select_box_attribute", "value")
    )
    def update_continent_box_plot(value):
        return plot_boxplots(data, keyword=value)


    @app.callback(
        Output('covid_donut_graph', 'figure'),
        [Input('country-dropdown', 'value')]
    )
    def update_donut_graph(value):
        fig = go.Figure(go.Pie(
            labels=['Active Cases', 'Recovered', 'Deaths'],
            values=[data.loc[value, 'ActiveCasesPercent'],
                    data.loc[value, 'RecoveredPercent'],
                    data.loc[value, 'DeathsPercent']],
            hole=0.3
        ))

        fig.update_layout(
            title=f"COVID-19 Distribution for {value}",
            # height=500,
            # width=700
        )
        return fig
        
    return app
