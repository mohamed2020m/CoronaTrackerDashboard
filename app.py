from helpers import  create_clean_dataframe, init_figure, getTotals
from layout import load_display_data
from scrap import get_scraped_data
import dash

if __name__ == '__main__':

    total_stats, countries_data = get_scraped_data()
    data = create_clean_dataframe(countries_data)

    fig, init_continent_fig, init_k_countries_plot, init_box_fig, init_dount_fig, gh = init_figure(data)
    total_cases, total_deaths, total_recoveries = total_stats["TotalCase"], total_stats["TotalDeaths"], total_stats["TotalRecovered"] 

    app = load_display_data(data, total_cases, total_deaths, total_recoveries, fig, init_continent_fig, init_k_countries_plot, init_box_fig, init_dount_fig, gh)
    
    # app = dash.Dash(__name__)
    server = app.server
    app.run_server(debug=True, port=8096)
