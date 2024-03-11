# import dash
# from dash import html
import os
from scrapy.crawler import CrawlerProcess
from corona_stats.spiders.coronaspider import CoronaSpiderSpider
from scrapy.signalmanager import dispatcher
from scrapy import signals
import plotly.graph_objs as go
import pandas as pd
import numpy as np
import dash
import dash_core_components as dcc
import dash_html_components as html
from dash.dependencies import Input, Output
from collections import defaultdict 
from theme import theme
import dash_bootstrap_components as dbc
import plotly.express as px

# Handler for the item scraped signal
def item_scraped(item, response, spider):
    # Initialize a list to hold scraped data
    global scraped_data 
    scraped_data  = item
    
def spider_closed(spider, reason):
    import json
    with open('scraped_data.json', 'w', encoding='utf-8') as f:
        json.dump(scraped_data, f, ensure_ascii=False, indent=4)
        
def run_scrapy_spider():
    process = CrawlerProcess()
    dispatcher.connect(item_scraped, signal=signals.item_scraped)
    # dispatcher.connect(spider_closed, signal=signals.spider_closed)
    process.crawl(CoronaSpiderSpider)
    process.start() 


# Function to load and display the scraped data in Dash
# def load_display_data():
#     # Initialize the Dash app
#     app = dash.Dash(__name__)

#     # Define the layout of the app using the scraped data
#     app.layout = html.Div([
#         html.H1('Coronavirus'), 
#         html.Ul([html.Li(f"{h['name']}") for h in scraped_data])
#     ])

#     return app


def replace_nan(data):
    """
    This function replaces empty or N/A values with np.nan so that it can be easier to manipulate the data later on.
    """
    for col in data.columns:
        data[col].replace(["N/A", "", " "], np.nan, inplace=True)


def create_clean_dataframe(countries_data):
    """
    This function takes a dict object and create a clean well formatted dataframe.

    Parameters:
        countries_data : dict object
            The dict that contains the countries data.
    Returns:
        data : dataframe
            Well formatted dataframe.
    """
    data = pd.DataFrame(countries_data).transpose()
    replace_nan(data)
    return data


"""Building the plotting functions"""

# ---------------------------------------------------------------------------

def plot_continent_data(data, keyword):
    """
    This function creates a Figure from continental data.

    Parameters:
        data : dataframe
            The whole dataset.
        keyword : str
            The keyword used to define the figure wanted, the available keyword : {"Total", "New"}

    Returns:
        fig : Figure
            The figure that will be drawed on plotly.
    """
    if keyword == "New":
        cols = ["NewCases", "NewRecovered", "NewDeaths"]
    else:
        cols = ["TotalCases", "TotalRecovered", "TotalDeaths"]
    res = data.groupby("Continent")[cols].sum()

    plot_data = []
    colors = ["#101e70", "#186e3c", "#cc1b35"]
    for col, color in zip(cols, colors):
        plot_data.append(go.Bar(x=res.index.to_list(), y=res[col], name=col, marker=dict(color=color)))

    layout = go.Layout(title=f"Corona {keyword} Cases/Recovered/Deaths",
                       xaxis=dict(title="Continents"),
                       yaxis=dict(title="Cases per Continent"))

    # print("Pot data", plot_data)
    fig = go.Figure(data=plot_data, layout=layout)
    return fig


def get_continent_sorted_data(data, continent, sortedby="TotalCases", ascending=False):
    """
    This function creates a sorted dataframe related to a continent and sorted by a columns.

    Parameters:
        data : dataframe
            The whole dataset.
        continent : str
            The continent we want to get the data from.
        sortedby : str, Default="TotalCases"
            The name of the column we want to sort by.
        ascending : Boolean, Default=False
            Either we want to sort in an ascending order or descending order.
    Returns:
        groupedbydata : dataframe
            A dataframe groupedby the continent.
    """
    return data.groupby("Continent").get_group(continent).sort_values(by=sortedby, ascending=ascending).reset_index()


def get_top_k_countries(data, k_countries=10, sortedby="TotalCases", ascending=False):
    """
    This function creates a k-len dataframe sorted by a key.

    Parameters:
        data : dataframe.
            The whole dataset.
        k_countries : int, Default=10
            The number of countries you want to plot.
        sortedby : str, Default="TotalCases".
            The column name we want to sort the data by
        ascending : Boolean, Default=False
            Either we want to sort in an ascending order or descending order.

    Returns:
        data : dataframe
            The k_contries lines dataframe sortedby the key given and in the wanted order.
    """
    return data.sort_values(by=sortedby, ascending=ascending).iloc[:k_countries]


def plot_top_k_countries(n_countries, sortby):
    """This function returns a figure where a number of countries are sorted by the value that resides in sortby."""
    res = get_top_k_countries(data, n_countries, sortby)
    plot_data = []

    plot_data.append(go.Bar(x=res.index.to_list(), y=res[sortby], name=sortby))

    layout = go.Layout(title=f"Top Countries orderedby {sortby}",
                       xaxis=dict(title="Countries"),
                       yaxis=dict(title=f"{sortby}"))

    fig = go.Figure(data=plot_data, layout=layout)
    return fig


def plot_boxplots(data, keyword="Deaths/1M pop"):
    """This function returns a figure of the boxplot related to each continent in regards to the keyword."""
    plot_data = []
    grouped_data = data.groupby("Continent")
    continents = data["Continent"].value_counts().index.to_list()
    for continent in continents:
        plot_data.append(go.Box(y=grouped_data.get_group(continent)[keyword], name=continent))
    layout = go.Layout(title=f"Boxplots using {keyword}",
                       xaxis=dict(title="Continents"),
                       yaxis=dict(title=f"{keyword}"))
    fig = go.Figure(data=plot_data, layout=layout)
    return fig


def plot_scatter(data):
    """This function returns a figure of the scatter of TotalCases and TotalDeaths related to each country in regards to the keyword."""
    fig = px.scatter(
        data, x="TotalCases", y="TotalDeaths",
        size="Population", color="Continent", hover_name=data.index,
        log_x=True, size_max=60
    )
    return fig

def plot_dount(data):
    # Calculate percentages for each category
    data['ActiveCasesPercent'] = data['ActiveCases'] / data['TotalCases'] * 100
    data['RecoveredPercent'] = data['TotalRecovered'] / data['TotalCases'] * 100
    data['DeathsPercent'] = data['TotalDeaths'] / data['TotalCases'] * 100

    # Fill missing values with 0
    data.fillna(0, inplace=True)

    # Create the donut graph
    init_dount_fig = go.Figure()

    for index, row in data.iterrows():
        init_dount_fig.add_trace(go.Pie(
            labels=['Active Cases', 'Recovered', 'Deaths'],
            values=[row['ActiveCasesPercent'], row['RecoveredPercent'], row['DeathsPercent']],
            hole=0.3,
            name=index
        ))

    init_dount_fig.update_layout(
        title="COVID-19 Distribution by Country",
        annotations=[dict(text=c, x=0.5, y=0.5, font_size=20, showarrow=False) for c in data.index],
        # height=600,
        # width=800
    )
    return init_dount_fig


def idk(data):
    for col in ['TotalRecovered', 'ActiveCases', 'Serious,Critical']:
        data[col] = pd.to_numeric(data[col], errors='coerce')

    # Create the scatter plot
    fig = go.Figure(data=go.Scatter(
        x=data['TotalCases'],
        y=data['Deaths/1M pop'],
        text=data.index, 
        mode='markers',
        marker=dict(
            size=data['Population'] / 1e7, 
            color=data['TotalTests'], 
            showscale=True 
        )
    ))

    fig.update_layout(
        title='Total Cases vs. Deaths per 1M Population by Country',
        xaxis_title='Total Cases',
        yaxis_title='Deaths per 1M Population',
        legend_title='Total Tests'
    )
    return fig

def init_figure():
    "This function initiate all the needed figure to start the app."
    return plot_scatter(data), plot_continent_data(data, keyword="Total"), plot_top_k_countries(10, "TotalCases"), plot_boxplots(data), plot_dount(data), idk(data)


def getTotals():
    total_deaths = data['TotalDeaths'].sum()
    total_cases = data['TotalCases'].sum()
    total_recoveries = data['TotalRecovered'].sum()
    "{:,}".format(total_cases)
    return "{:,}".format(total_cases), "{:,}".format(total_deaths), "{:,}".format(total_recoveries)

def read_json_to_variable(file_path):
    import json
    with open(file_path, 'r') as file:
        data = json.load(file)
    return data

# Initializing the app
app = dash.Dash(__name__)
server = app.server

"""Initiale Figures"""
# ---------------------------------------------------------------------------

# Run the Scrapy spider to scrape data
run_scrapy_spider()
countries_data = scraped_data


# print("countries_data:", countries_data)
# countries_data = read_json_to_variable("scraped_data.json")

data = create_clean_dataframe(countries_data)
# print("data", data)

fig, init_continent_fig, init_k_countries_plot, init_box_fig, init_dount_fig, gh = init_figure()

total_cases, total_deaths, total_recoveries = getTotals()

"""Building the app"""
# ---------------------------------------------------------------------------

# Initializing the app
app = dash.Dash(__name__)
server = app.server


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
                'display': 'flex', 
                # 'justifyContent': 'center', 
                # 'alignItems': 'center'
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
                        # 'display': 'flex', 
                        # 'justifyContent': 'center', 
                        # 'alignItems': 'center'
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
    return plot_top_k_countries(n_countries, attribute)


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
def update_donut_graph(selected_country):
    fig = go.Figure(go.Pie(
        labels=['Active Cases', 'Recovered', 'Deaths'],
        values=[data.loc[selected_country, 'ActiveCasesPercent'],
                data.loc[selected_country, 'RecoveredPercent'],
                data.loc[selected_country, 'DeathsPercent']],
        hole=0.3
    ))

    fig.update_layout(
        title=f"COVID-19 Distribution for {selected_country}",
        # height=500,
        # width=700
    )
    return fig

if __name__ == '__main__':
    # Run the Scrapy spider to scrape data
    # run_scrapy_spider()
    # print(scraped_data)
    # app = load_display_data()
    app.run_server(debug=True, port=8096)
