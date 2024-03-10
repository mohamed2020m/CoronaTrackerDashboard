
from dash import Dash, html

# Include Font Awesome
external_stylesheets = ['https://use.fontawesome.com/releases/v5.8.1/css/all.css']

app = Dash(__name__, external_stylesheets=external_stylesheets)

app.layout = html.Div(
    children=[
        html.Div(  # Container for centering the title and icon horizontally
            children=[
                html.I(className="fas fa-virus"),  # Font Awesome icon
                html.Span(' COVID-19 Dashboard', style={'marginLeft': '10px'})  # Title text with space
            ],
            style={
                'textAlign': 'center',  # Center the title and icon horizontally
                'fontSize': '24px',  # Adjust font size as needed
                'display': 'flex',  # Use flexbox for inline display of elements
                'justifyContent': 'center',  # Center children horizontally in the flex container
                'alignItems': 'center',  # Center children vertically in the flex container
            }
        ),
        # Additional content goes here
    ],
    style={'margin': '0 auto', 'width': '50%'}  # Adjust width as needed for your layout
)

if __name__ == '__main__':
    app.run_server(debug=True, port=8888)
