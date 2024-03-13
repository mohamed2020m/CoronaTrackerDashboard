import plotly.graph_objs as go
import pandas as pd
import numpy as np
import plotly.express as px


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


def plot_top_k_countries(data, n_countries, sortby):
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

def init_figure(data):
    "This function initiate all the needed figure to start the app."
    return plot_scatter(data), plot_continent_data(data, keyword="Total"), plot_top_k_countries(data, 10, "TotalCases"), plot_boxplots(data), plot_dount(data), idk(data)


def getTotals(data):
    total_deaths = data['TotalDeaths'].sum()
    total_cases = data['TotalCases'].sum()
    total_recoveries = data['TotalRecovered'].sum()
    "{:,}".format(total_cases)
    return "{:,}".format(total_cases), "{:,}".format(total_deaths), "{:,}".format(total_recoveries)

def read_json_to_variable(data, file_path):
    import json
    with open(file_path, 'r') as file:
        data = json.load(file)
    return data
