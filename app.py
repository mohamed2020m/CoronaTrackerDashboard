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
        

# Handler for the item scraped signal
def item_scraped(item, response, spider):
    # Initialize a list to hold scraped data
    global scraped_data 
    scraped_data  = item
    
def run_scrapy_spider():
    process = CrawlerProcess()
    dispatcher.connect(item_scraped, signal=signals.item_scraped)
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
    colors = ["#031cfc", "#24b514", "#d11d1d"]
    for col, color in zip(cols, colors):
        plot_data.append(go.Bar(x=res.index.to_list(), y=res[col], name=col, marker=dict(color=color)))

    layout = go.Layout(title=f"Corona {keyword} Cases/Recovered/Deaths",
                       xaxis=dict(title="Continents"),
                       yaxis=dict(title="Cases per Continent"))

    print("Pot data", plot_data)
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


def init_figure():
    "This function initiate all the needed figure to start the app."
    return plot_continent_data(data, keyword="New"), plot_top_k_countries(10, "TotalCases"), plot_boxplots(data)



# Initializing the app
app = dash.Dash(__name__)
server = app.server

"""Initiale Figures"""
# ---------------------------------------------------------------------------

# Run the Scrapy spider to scrape data
run_scrapy_spider()
countries_data = scraped_data
# print("countries_data:", countries_data)

data = create_clean_dataframe(countries_data)
# print("data", data)

init_continent_fig, init_k_countries_plot, init_box_fig = init_figure()


"""Building the app"""
# ---------------------------------------------------------------------------

# Initializing the app
app = dash.Dash(__name__)
server = app.server

# Building the app layout
# app.layout = html.Div([
#     html.H1("Corona Tracker DashBoard", style={"text-align": "center"}),
#     html.Br(),
#     html.Div([
#         html.Br(),
#         html.H2("Corona Cases/Recovered/Deaths by Continent", style={"text-align": "center"}),
#         html.Br(),
#         dcc.Dropdown(id="select_keyword",
#                      options=[
#                          dict(label="Today's Data", value="New"),
#                          dict(label="Total Data", value="Total")],
#                      multi=False,
#                      value="New",
#                      style={"width": "40%"}
#                      ),

#         dcc.Graph(id="continent_corona_bar", figure=init_continent_fig)
#     ]),

#     html.Div([
#         html.Br(),
#         html.H2("Visualize Countries by attribute.", style={"text-align": "center"}),
#         html.Br(),
#         dcc.Dropdown(id="select_attribute",
#                      options=[
#                          dict(label="Total Cases", value='TotalCases'),
#                          dict(label="New Cases", value='NewCases'),
#                          dict(label="Total Cases per 1M population", value='Tot\xa0Cases/1M pop'),
#                          dict(label="Active Cases", value='ActiveCases'),
#                          dict(label="Serious, Critical Cases", value='Serious,Critical'),
#                          dict(label="Total Deaths", value='TotalDeaths'),
#                          dict(label="New Deaths", value='NewDeaths'),
#                          dict(label="Deaths per 1M population", value='Deaths/1M pop'),
#                          dict(label="Total Recovered", value='TotalRecovered'),
#                          dict(label="New Recovered", value='NewRecovered'),
#                          dict(label="Total Tests", value='TotalTests'),
#                          dict(label="Tests per 1M population", value='Tests/1Mpop')],
#                      multi=False,
#                      value="TotalCases",
#                      style={"width": "60%", 'display': 'inline-block'}
#                      ),
#         dcc.Dropdown(id="select_k_countries",
#                      options=[
#                          dict(label="Top 5", value=5),
#                          dict(label="Top 10", value=10),
#                          dict(label="Top 25", value=25),
#                          dict(label="Top 50", value=50),
#                      ],
#                      multi=False,
#                      value=10,
#                      style={"width": "30%", 'display': 'inline-block'}
#                      ),

#         dcc.Graph(id="k_countries_sorted", figure=init_k_countries_plot)
#     ]),

#     html.Div([
#         html.Br(),
#         html.H2("BoxPlot to explain the distribution of the variables", style={"text-align": "center"}),
#         html.Br(),
#         dcc.Dropdown(id="select_box_attribute",
#                      options=[
#                          dict(label="Deaths per 1M population", value='Deaths/1M pop'),
#                          dict(label="Tests per 1M population", value='Tests/1Mpop')
#                      ],
#                      multi=False,
#                      value="Deaths/1M pop",
#                      style={"width": "40%"}
#                      ),

#         dcc.Graph(id="continent_box_plot", figure=init_box_fig)
#     ])
# ])


# Define the provided theme
theme = {
    "accent": "#1f78b4",
    "accent_negative": "#C20000",
    "accent_positive": "#017500",
    "background_content": "#F9F9F9",
    "background_page": "#F2F2F2",
    "border": "#e2e2e2",
    "breakpoint_font": "1200px",
    "breakpoint_stack_blocks": "700px",
    "card_border": {
        "width": "0px 0px 0px 0px",
        "style": "solid",
        "color": "#e2e2e2",
        "radius": "0px"
    },
    "card_background_color": "#F9F9F9",
    "card_box_shadow": "0px 1px 3px rgba(0,0,0,0.12), 0px 1px 2px rgba(0,0,0,0.24)",
    "card_margin": "15px",
    "card_padding": "5px",
    "card_outline": {
        "width": "0px",
        "style": "solid",
        "color": "#e2e2e2"
    },
    "card_header_border": {
        "width": "0px 0px 1px 0px",
        "style": "solid",
        "color": "#e2e2e2",
        "radius": "0px"
    },
    "card_header_background_color": "#F9F9F9",
    "card_header_box_shadow": "0px 0px 0px rgba(0,0,0,0)",
    "card_header_margin": "0px",
    "card_header_padding": "10px",
    "colorway": [
        "#119dff",
        "#66c2a5",
        "#fc8d62",
        "#e78ac3",
        "#a6d854",
        "#ffd92f",
        "#e5c494",
        "#b3b3b3"
    ],
    "colorscale": [
        "#1f78b4",
        "#4786bc",
        "#6394c5",
        "#7ba3cd",
        "#92b1d5",
        "#a9c0de",
        "#bed0e6",
        "#d4dfee",
        "#eaeff7",
        "#ffffff"
    ],
    "font_family": "Open Sans",
    "font_size": "17px",
    "font_size_smaller_screen": "15px",
    "font_family_header": "Open Sans",
    "font_size_header": "24px",
    "font_family_headings": "Open Sans",
    "font_headings_size": None,
    "header_border": {
        "width": "0px 0px 0px 0px",
        "style": "solid",
        "color": "#e2e2e2",
        "radius": "0px"
    },
    "header_background_color": "#F9F9F9",
    "header_box_shadow": "0px 1px 3px rgba(0,0,0,0.12), 0px 1px 2px rgba(0,0,0,0.24)",
    "header_margin": "0px 0px 15px 0px",
    "header_padding": "0px",
    "text": "#606060",
    "report_font_family": "Computer Modern",
    "report_font_size": "12px",
    "report_background_page": "white",
    "report_background_content": "#FAFBFC",
    "report_text": "black"
}

app.layout = html.Div(style={'backgroundColor': theme['background_page'], 'color': theme['text'], 'padding': '20px'}, children=[
    html.H1("Corona Tracker Dashboard", style={"text-align": "center", "fontFamily": theme["font_family_header"], "color": theme["accent"]}),
    
    html.Div([
        html.H2("Corona Cases/Recovered/Deaths by Continent", style={"text-align": "center", "fontFamily": theme["font_family_header"], "color": theme["text"]}),
        dcc.Dropdown(id="select_keyword",
                     options=[
                         dict(label="Today's Data", value="New"),
                         dict(label="Total Data", value="Total")],
                     multi=False,
                     value="New",
                     style={"width": "40%", "margin": "auto", "color": theme["text"]}
                     ),
        dcc.Graph(id="continent_corona_bar", figure=init_continent_fig)
    ], style={'backgroundColor': theme['card_background_color'], 'padding': theme['card_padding'], 'borderRadius': theme['card_border']['radius'], 'margin': theme['card_margin']}),

    html.Div([
        html.H2("Visualize Countries by attribute.", style={"text-align": "center", "fontFamily": theme["font_family_header"], "color": theme["text"]}),
        dcc.Dropdown(id="select_attribute",
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
                         dict(label="Tests per 1M population", value='Tests/1Mpop')],
                     multi=False,
                     value="TotalCases",
                     style={"width": "60%", 'display': 'inline-block', "margin": "auto", "color": theme["text"]}
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
                     style={"width": "30%", 'display': 'inline-block', "margin": "auto", "color": theme["text"]}
                     ),
        dcc.Graph(id="k_countries_sorted", figure=init_k_countries_plot)
    ], style={'backgroundColor': theme['card_background_color'], 'padding': theme['card_padding'], 'borderRadius': theme['card_border']['radius'], 'margin': theme['card_margin']}),

    html.Div([
        html.H2("BoxPlot to explain the distribution of the variables", style={"text-align": "center", "fontFamily": theme["font_family_header"], "color": theme["text"]}),
        dcc.Dropdown(id="select_box_attribute",
                     options=[
                         dict(label="Deaths per 1M population", value='Deaths/1M pop'),
                         dict(label="Tests per 1M population", value='Tests/1Mpop')
                     ],
                     multi=False,
                     value="Deaths/1M pop",
                     style={"width": "40%", "margin": "auto", "color": theme["text"]}
                     ),
        dcc.Graph(id="continent_box_plot", figure=init_box_fig)
    ], style={'backgroundColor': theme['card_background_color'], 'padding': theme['card_padding'], 'borderRadius': theme['card_border']['radius'], 'margin': theme['card_margin']})
])



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


if __name__ == '__main__':
    # Run the Scrapy spider to scrape data
    # run_scrapy_spider()
    # print(scraped_data)
    # app = load_display_data()
    app.run_server(debug=True, port=8096)
