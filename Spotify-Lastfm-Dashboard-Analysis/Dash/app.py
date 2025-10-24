# app.py

# _________________________________Importing the necessary libraries______________________________

import base64
import csv
import json
import math
import re
import time
import ast
import warnings
from urllib.request import urlopen
import country_converter as coco
import dash
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from dash import Input, Output, callback_context, dcc, html
from dash.dependencies import Input, Output, State
from time_of_day_function import time_of_day

warnings.filterwarnings('ignore')

# _________________________________Data Loading and Preprocessing____________________________________

# Load the data
data = pd.read_csv("final_dataset2024.csv", low_memory=False)

# Preprocess the data
data['username'] = data['username'].astype(str)
data['endTime'] = pd.to_datetime(data['endTime'])

# Extract some important information
top_tracks = data.groupby('track_name')['hPlayed'].sum().nlargest(10).reset_index()
top_artists = data.groupby('artist_name')['hPlayed'].sum().nlargest(10).reset_index()
country_streams = data.groupby('Country')['hPlayed'].sum().reset_index()

unique_genres = data['genero'].dropna()
unique_genres = unique_genres[unique_genres.apply(lambda x: isinstance(x, str))]

# Dictionary `user_names` where the keys are the usernames and the values are the specific names
user_names = {
    '31vvjn27vuior64yili42rn2ihau': 'Alice Mangara',
    '11141944489': 'Vasco Santos',
}

# Load GeoJSON data
with urlopen('https://raw.githubusercontent.com/johan/world.geo.json/master/countries.geo.json') as response:
    world_geojson = json.load(response)

# Dictionary to store latitude and longitude for each country
iso_a3_to_coordinates = {}
# Read latitude and longitude data from CSV file
with open('countries_lat_lon_v2.csv', mode='r', encoding='utf-8-sig') as file:
    reader = csv.DictReader(file)
    for row in reader:
        iso_a3_to_coordinates[row['ISOA3']] = {'lat': float(row['latitude']), 'lon': float(row['longitude'])}

# Dictionary mapping month numbers to names
month_names = {
    1: 'January', 2: 'February', 3: 'March', 4: 'April',
    5: 'May', 6: 'June', 7: 'July', 8: 'August',
    9: 'September', 10: 'October', 11: 'November', 12: 'December'
}
# Dictionary mapping month names to numbers
month_numbers = {v: k for k, v in month_names.items()}

# ___________________________________Creating the Dash App___________________________________________

# Function to generate the habit indicator image based on the user
def generate_habit_indicator(n_clicks, n_clicks_image, username):
    if n_clicks > 0 and username is not None:
        habit, n_hours_streamed = time_of_day(username, data)
        n_hours_streamed = round(n_hours_streamed)
    else:
        habit, n_hours_streamed = 'unknown', None

    if habit == 'morning':
        image_path = 'morning.png'
    elif habit == 'afternoon':
        image_path = 'afternoon.png'
    elif habit == 'night':
        image_path = 'night.png'
    elif habit == 'unknown':
        image_path = None
        layout = html.Div([
            html.P(' ')
        ])
    
    # Read the image
    if image_path:
        with open(image_path, 'rb') as f:
            img_bytes = f.read()
        img_base64 = base64.b64encode(img_bytes).decode('utf-8')
    else:
        return layout

    if n_clicks_image > 0:
        # Return the layout with the image and message
        return html.Div([
            html.Div([
                html.Img(
                    id='image-clickable',
                    src='data:image/png;base64,{}'.format(img_base64),
                    style={'width': '200px', 'height': '200px', 'border-radius': '50%', 'animation': 'zoom 3s alternate infinite'}
                ),
                # Pop-up styled as a box centered below the image
                html.Div(
                    id='popup',
                    style={'display': 'block', 'width': '150px', 'padding': '10px', 'background-color': 'white', 'border-radius': '5px', 'text-align': 'center', 'position': 'absolute', 'z-index': '1', 'box-shadow': '0 4px 8px 0 rgba(0, 0, 0, 0.2)', 'animation': 'fade-in 1s'},
                    children=[
                        html.P("Your a night owl!", style={'font-size': '15px', 'color': 'rgb(25, 21, 55)'}),
                        html.P("You've spent most of your time listening to music at night.", style={'font-size': '15px', 'color': 'rgb(25, 21, 55)'}),
                        html.P(f"You've listened to approximately {n_hours_streamed} hours at night!", style={'font-size': '15px', 'color': 'rgb(25, 21, 55)'}),
                    ]
                )
            ], style={'bottom': '20px','top':'20px', 'right': '20px'})
        ], style={'margin-top': '0px', 'padding-top': '0px'})
    else:
        # Return the layout with the image only
        return html.Div([
            html.Div([
                html.Img(src='data:image/png;base64,{}'.format(img_base64), style={'width': '200px', 'height': '200px', 'border-radius': '50%', 'animation': 'zoom 3s alternate infinite'}),
            ], style={'bottom': '20px','top':'20px', 'right': '20px', 'text-align': 'right'})
        ], style={'margin-top': '0px', 'padding-top': '0px'})

# Function to generate the map based on selected filters
def generate_map(n_clicks, year, username, genre, clicked_country=None, reset_button=None):
    if n_clicks > 0:
        if year is None and genre is None:
            # Filter data only by user
            data_filtered = data[data['username'] == username]
        elif year is None and genre is not None:
            # Filter data only by user and genre
            data_filtered = data[(data['genero'] == genre) & (data['username'] == username)]
        elif year is not None and genre is None:
            # Filter data only by user and year
            data_filtered = data[(data['year_Played'] == year) & (data['username'] == username)]
        else:
            # Filter data based on selected user, year and genre
            data_filtered = data[(data['year_Played'] == year) & (data['username'] == username) & (data['genero'] == genre)]

    # Group by country and sum the streamed hours
    country_streams_filtered = data_filtered.groupby('Country')['hPlayed'].sum().reset_index()

    ctx = callback_context
    triggered_input = ctx.triggered[0]["prop_id"].split(".")[0] if ctx.triggered else None
    if triggered_input == 'geo-chart':
        # Handle click event on the map
        if clicked_country:
            # If a country is clicked, zoom into that country
            fig = px.choropleth_mapbox(country_streams_filtered, geojson=world_geojson, locations='Country', color='hPlayed',
                                        color_continuous_scale="RdYlGn",
                                        range_color=(0, 100),
                                        mapbox_style="carto-positron",
                                        zoom=3.5, 
                                        center={"lat": clicked_country['lat'], "lon": clicked_country['lon']},
                                        opacity=0.5,
                                        labels={'unemp': 'unemployment rate'}
                                        )
        else:
            # If no country is clicked, reset the map to initial zoom and position
            fig = px.choropleth_mapbox(country_streams_filtered, geojson=world_geojson, locations='Country', color='hPlayed',
                                        color_continuous_scale="RdYlGn",
                                        range_color=(0, 100),
                                        mapbox_style="carto-positron",
                                        zoom=1, 
                                        center={"lat": 0, "lon": 0},
                                        opacity=0.5,
                                        labels={'unemp': 'unemployment rate'}
                                        )
    elif triggered_input == 'reset-button' and reset_button:
        # Handle click event on the reset button
        fig = px.choropleth_mapbox(country_streams_filtered, geojson=world_geojson, locations='Country', color='hPlayed',
                                    color_continuous_scale="RdYlGn",
                                    range_color=(0, 100),
                                    mapbox_style="carto-positron",
                                    zoom=1, 
                                    center={"lat": 0, "lon": 0},
                                    opacity=0.5,
                                    labels={'unemp': 'unemployment rate'}
                                    )
    else:
        # No event triggered, return map with default zoom and position
        fig = px.choropleth_mapbox(country_streams_filtered, geojson=world_geojson, locations='Country', color='hPlayed',
                                    color_continuous_scale="RdYlGn",
                                    range_color=(0, 100),
                                    mapbox_style="carto-positron",
                                    zoom=1, 
                                    center={"lat": 0, "lon": 0},
                                    opacity=0.5,
                                    labels={'unemp': 'unemployment rate'}
                                    )

    fig.update_layout(margin={"r": 0, "t": 0, "l": 0, "b": 0},
                    dragmode=False)
    
    return fig

# Function to generate the popup that appear on the map
def map_popup(n_clicks, username, year, iso_a3=None):
    if n_clicks > 0:
        if year is None:
            # Filter data only by user
            data_filtered = data[data['username'] == username]
        else:
            # Filter data based on selected user and year
            data_filtered = data[(data['year_Played'] == year) & (data['username'] == username)]

        if iso_a3:
            filtered_data = data_filtered[data_filtered['Country'] == iso_a3]
            # Convert ISO to Country name
            country_name = coco.convert(names=iso_a3, to='name_short')
        else:
            filtered_data = data_filtered
            country_name = 'Worldwide'

        # Get top genre for the selected country
        if not filtered_data.groupby('genero')['hPlayed'].sum().nlargest(1).empty:
            top_genre = filtered_data.groupby('genero')['hPlayed'].sum().nlargest(1).index[0]
        else:
            top_genre = None

        # Get top artist for the selected country
        if not filtered_data.groupby('artist_name')['hPlayed'].sum().nlargest(1).empty:
            top_artist = filtered_data.groupby('artist_name')['hPlayed'].sum().nlargest(1).index[0]
        else:
            top_artist = None

        # Get image of the top artist
        if not filtered_data[filtered_data['artist_name'] == top_artist]['images'].empty:
            top_artist_image = filtered_data[filtered_data['artist_name'] == top_artist]['images'].iloc[0]
            top_artist_image = extract_image_url(top_artist_image)
        else:
            top_artist_image = None

        # Get similiar artists for the top artist
        if not filtered_data[filtered_data['artist_name'] == top_artist]['similar_artists'].empty:
            similar_artists = filtered_data[filtered_data['artist_name'] == top_artist]['similar_artists'].iloc[0]
            similar_artists = ast.literal_eval(similar_artists)
        else:
            similar_artists = None

        # Get images for similar artists
        if similar_artists:
            similar_1 = similar_artists[0]
            similar_2 = similar_artists[1]
            similar_3 = similar_artists[2]
            if not filtered_data[filtered_data['artist_name'] == similar_artists[0]]['images'].empty:
                similar_artist0_images = filtered_data[filtered_data['artist_name'] == similar_artists[0]]['images'].iloc[0]
                similar_artist0_image = extract_image_url(similar_artist0_images)
            else:
                similar_artist0_image = None

            if not filtered_data[filtered_data['artist_name'] == similar_artists[1]]['images'].empty:
                similar_artist1_images = filtered_data[filtered_data['artist_name'] == similar_artists[1]]['images'].iloc[0]
                similar_artist1_image = extract_image_url(similar_artist1_images)
            else:
                similar_artist1_image = None

            if not filtered_data[filtered_data['artist_name'] == similar_artists[2]]['images'].empty:
                similar_artist2_images = filtered_data[filtered_data['artist_name'] == similar_artists[2]]['images'].iloc[0]
                similar_artist2_image = extract_image_url(similar_artist2_images)
            else:
                similar_artist2_image = None

        else:
            similar_1 = None
            similar_2 = None
            similar_3 = None
            similar_artist0_image = None
            similar_artist1_image = None
            similar_artist2_image = None

        # Get followers and listeners for the top artist
        if not filtered_data[filtered_data['artist_name'] == top_artist]['followers'].empty:
            followers = filtered_data[filtered_data['artist_name'] == top_artist]['followers'].iloc[0]
            followers = "{:,}".format(int(followers))
        else:
            followers = None

        if not filtered_data[filtered_data['artist_name'] == top_artist]['listeners'].empty:
            listeners = filtered_data[filtered_data['artist_name'] == top_artist]['listeners'].iloc[0]
            listeners = "{:,}".format(int(listeners))
        else:
            listeners = None

        return html.Div([
            html.H3(f"Country: {country_name}"),
            html.P([html.Strong("Most Genre listened: "), f"{top_genre}"]),
            html.P([html.Strong("Most Artist listened: "), f"{top_artist}"]),
            html.Img(src=top_artist_image, style={'width': '50px', 'height': '50px', 'border-radius': '50%'}),
            html.P([html.Strong("Followers: "), f"{followers}"]),
            html.P([html.Strong("Listeners: "), f"{listeners}"]),
            html.P([html.Strong("Similar artists: ")]),
            html.Div([
                html.Div([
                    html.P(similar_1),
                    html.Div(
                        children=[
                            html.Img(src=similar_artist0_image, style={'width': '50px', 'height': '50px', 'border-radius': '50%'})
                        ],
                        style={'display': 'flex', 'justify-content': 'center', 'align-items': 'center'}
                    )
                ], style={'marginRight': '20px'}),
                html.Div([
                    html.P(similar_2),
                    html.Div(
                        children=[
                            html.Img(src=similar_artist1_image, style={'width': '50px', 'height': '50px', 'border-radius': '50%'})
                        ],
                        style={'display': 'flex', 'justify-content': 'center', 'align-items': 'center'}
                    )
                ], style={'marginRight': '20px'}),
                html.Div([
                    html.P(similar_3),
                    html.Div(
                        children=[
                        html.Img(src=similar_artist2_image, style={'width': '50px', 'height': '50px', 'border-radius': '50%'})
                        ],
                        style={'display': 'flex', 'justify-content': 'center', 'align-items': 'center'}
                    )
                ], style={'marginRight': '20px'}),
            ], style={'display': 'flex', 'alignItems': 'center'}),
                        ])

###____________________________________Tops tables________________________________________________###

# Function to fix the image URL format
def extract_image_url(image_url):
    if isinstance(image_url, str):
        image_url_corrigido = re.sub(r"'", '"', image_url)
        image_url_corrigido = re.sub(r'([{,])(\s*)([A-Za-z0-9_\-]+)\s*:', r'\1\2"\3":', image_url_corrigido)

        try:
            lista_dicionarios = json.loads(image_url_corrigido)
            if lista_dicionarios:
                primeiro_dicionario = lista_dicionarios[0]
                valor = list(primeiro_dicionario.values())[0]
                return valor
            else:
                return None
        except json.JSONDecodeError as e:
            print("Erro ao decodificar JSON:", e)
            return None
    else:
        return None

# Function to fetch top tracks data based on selected filters
def get_top_tracks(year, username, genre, clicked_country=None):
    if year is None and genre is None:
        # Filter data only by user
        user_data = data[data['username'] == username]
    elif year is None and genre is not None:
        # Filter data only by user and genre
        user_data = data[(data['genero'] == genre) & (data['username'] == username)]
    elif year is not None and genre is None:
        # Filter data only by user and year
        user_data = data[(data['year_Played'] == year) & (data['username'] == username)]
    else:
        # Filter data based on selected user, year and genre
        user_data = data[(data['year_Played'] == year) & (data['username'] == username) & (data['genero'] == genre)]

    if clicked_country:
        # Filter data based on the clicked country
        user_data = user_data[user_data['Country'] == clicked_country]

    user_data['image_url'] = user_data['images'].apply(extract_image_url)
    
    # Group by track and aggregate
    top_tracks = user_data.groupby('track_name').agg(
        hPlayed=('hPlayed', 'sum'),
        artist_name=('artist_name', lambda x: x.mode()[0]),
        image_url=('image_url', 'first')
    ).nlargest(5, 'hPlayed').reset_index()
    
    return top_tracks

# Function to fetch top artists data based on selected filters
def get_top_artists(year, username, genre, clicked_country=None):
    if year is None and genre is None:
        # Filter data only by user
        user_data = data[data['username'] == username]
    elif year is None and genre is not None:
        # Filter data only by user and genre
        user_data = data[(data['genero'] == genre) & (data['username'] == username)]
    elif year is not None and genre is None:
        # Filter data only by user and year
        user_data = data[(data['year_Played'] == year) & (data['username'] == username)]
    else:
        # Filter data based on selected user, year and genre
        user_data = data[(data['year_Played'] == year) & (data['username'] == username) & (data['genero'] == genre)]

    if clicked_country:
        # Filter data based on the clicked country
        user_data = user_data[user_data['Country'] == clicked_country]
    
    # Aplicando a função extract_image_url para extrair a URL da imagem
    user_data['image_url'] = user_data['images'].apply(extract_image_url)
    
    # Group by artist and aggregate
    top_artists = user_data.groupby('artist_name').agg(
        hPlayed=('hPlayed', 'sum'),
        track_name=('track_name', lambda x: x.mode()[0]),
        image_url=('image_url', 'first')
    ).nlargest(5, 'hPlayed').reset_index()
    
    return top_artists

###________________________________________________________________________________________________###

# Function to generate the plot for top tracks by month based on selected filters
def generate_tracks_plot(n_clicks, year, username, genre, clicked_country=None):
    if n_clicks > 0:
        if year is None and genre is None:
            # Filter data only by username
            data_filtered = data[data['username'] == username]
        elif year is None and genre is not None:
            # Filter data only by user and genre
            data_filtered = data[(data['genero'] == genre) & (data['username'] == username)]
        elif year is not None and genre is None:
            # Filter data only by user and year
            data_filtered = data[(data['year_Played'] == year) & (data['username'] == username)]
        else:
            # Filter data based on selected user, year and genre
            data_filtered = data[(data['year_Played'] == year) & (data['username'] == username) & (data['genero'] == genre)]
        
    if clicked_country:
        # Filter data based on the clicked country
        data_filtered = data_filtered[data_filtered['Country'] == clicked_country]

    data_grouped = data_filtered.groupby(['month_Played', 'artist_name', 'track_name'])['hPlayed'].sum().reset_index()
    song_of_month = data_grouped.groupby('month_Played').apply(lambda x: x.loc[x['hPlayed'].idxmax()])
    song_of_month['artist_track'] = song_of_month['artist_name'] + ' - ' + song_of_month['track_name']
    # Extract the unique months from the data
    unique_months = song_of_month['month_Played'].unique()
    # Create the ticktext based on the unique months
    ticktext = [month_names[month] for month in unique_months]
    # Define a list of colors for the bars
    colors = ['#67000d', '#a50026', '#d73027', '#f46d43', '#fdae61', '#fee08b', '#d9ef8b', '#a6d96a', '#66bd63', '#1a9850', '#006837', '#00441b']
    traces = []
    for i, row in song_of_month.iterrows():
        # Assign a color to each bar based on its index in the loop
        color_index = i % len(colors)
        trace = go.Bar(
            x=[row['month_Played']],
            y=[row['hPlayed']],
            name=row['artist_track'],
            hoverinfo='text',
            hovertext=row['artist_track'],
            marker=dict(
            color=colors[color_index],
            line=dict(color='rgb(245, 243, 235)', width=1)
        )
        )
        traces.append(trace)
    layout = go.Layout(
        xaxis=dict(title='Month', tickmode='array', tickvals=unique_months, ticktext=ticktext),
        yaxis=dict(title='Hours Played'),
        barmode='group',
        showlegend=False,
        plot_bgcolor='white', 
        paper_bgcolor='white'  
    )
    fig = go.Figure(data=traces, layout=layout)
    return fig

# Function to generate the plot for top artists by month based on selected filters
def generate_pie_chart(n_clicks, year, username, genre, clicked_country=None):
    if n_clicks > 0:
        if year is None and genre is None:
            # Filter data only by username
            data_filtered = data[data['username'] == username]
        elif year is None and genre is not None:
            # Filter data only by user and genre
            data_filtered = data[(data['genero'] == genre) & (data['username'] == username)]
        elif year is not None and genre is None:
            # Filter data only by user and year
            data_filtered = data[(data['year_Played'] == year) & (data['username'] == username)]
        else:
            # Filter data based on selected user, year and genre
            data_filtered = data[(data['year_Played'] == year) & (data['username'] == username) & (data['genero'] == genre)]

    if clicked_country:
        # Filter data based on the clicked country
        data_filtered = data_filtered[data_filtered['Country'] == clicked_country]

    # Group by month and artist and sum the streamed hours
    data_grouped = data_filtered.groupby(['month_Played', 'artist_name'])['hPlayed'].sum().reset_index()
    artist_of_month = data_grouped['hPlayed'].groupby(data_grouped['month_Played']).idxmax()
    artist_of_month = data_grouped.loc[artist_of_month]

    # Dictionary mapping month numbers to names
    month_names = {
        1: 'January',
        2: 'February',
        3: 'March',
        4: 'April',
        5: 'May',
        6: 'June',
        7: 'July',
        8: 'August',
        9: 'September',
        10: 'October',
        11: 'November',
        12: 'December'
    }

    # Replace month numbers with names
    artist_of_month['month_Played'] = artist_of_month['month_Played'].map(month_names)
    
    colors_green = ['#e5f5e0', '#c7e9c0', '#a1d99b', '#74c476', '#509d67','#b2c68c']
    colors_red = ['#fee5d9', '#fcbba1', '#fc9272', '#fb6a4a', '#d5625e','#f0f083']
    
    pie_data = go.Pie(
        labels=artist_of_month['month_Played'],
        values=artist_of_month['hPlayed'],
        hoverinfo='text+label',
        hovertext=artist_of_month['artist_name'],
        text=artist_of_month['artist_name'],
        textinfo='text',
        hole=0.3,
        sort=False,
        marker=dict(
            colors=colors_green + colors_red,
            line=dict(color='rgb(245, 243, 235)', width=1)
        )
    )
    layout = go.Layout(
        plot_bgcolor='white',
        paper_bgcolor='white',
    )
    fig = go.Figure(data=[pie_data], layout=layout)
    return fig

# Function to generate the bar plot for the slice hover of the pie chart (when no year is selected)
def generate_bar_pie(artist_name, month):
    # Convert the month name to the corresponding number
    month_number = month_numbers[month]
    # Filter data for the specified artist and month
    artist_data = data[(data['artist_name'] == artist_name) & (data['month_Played'] == month_number)]
    
    hist_data = artist_data.groupby(['year_Played'])['hPlayed'].sum().reset_index()
    
    fig = px.bar(hist_data, x='year_Played', y='hPlayed', 
                 title=f'Hours played for {artist_name} in {month} by year',
                 labels={'year_Played': 'Year', 'hPlayed': 'Hours Played'})
    
    # Set x-axis tick values to only display years
    fig.update_xaxes(tickvals=hist_data['year_Played'])
    
    return fig

# Function to generate the streamgraph based on selected filters
def generate_streamgraph(n_clicks, year, username, genre, clicked_country=None):
    if n_clicks > 0:
        if year is None and genre is None:
            # Filter data only by username
            combined_audio_data_year_user = data[data['username'] == username]
        elif year is None and genre is not None:
            # Filter data only by user and genre
            combined_audio_data_year_user = data[(data['genero'] == genre) & (data['username'] == username)]
        elif year is not None and genre is None:
            # Filter data only by user and year
            combined_audio_data_year_user = data[(data['year_Played'] == year) & (data['username'] == username)]
        else:
            # Filter data based on selected user, year and genre
            combined_audio_data_year_user = data[(data['year_Played'] == year) & (data['username'] == username) & (data['genero'] == genre)]

    if clicked_country:
        # Filter data based on the clicked country
        combined_audio_data_year_user = combined_audio_data_year_user[combined_audio_data_year_user['Country'] == clicked_country]

    # Group by artist and sum the streamed hours
    top_artists = combined_audio_data_year_user.groupby('artist_name').agg(
        hPlayed=('hPlayed', 'sum')
    ).nlargest(5, 'hPlayed').index
    
    fig = go.Figure()
    
    colors_green = ['#e5f5e0', '#c7e9c0', '#a1d99b', '#74c476', '#31a354']
    colors_red = ['#fee5d9', '#fcbba1', '#fc9272', '#fb6a4a', '#de2d26']
    
    for idx, artist in enumerate(reversed(top_artists)):
        artist_data = combined_audio_data_year_user[combined_audio_data_year_user['artist_name'] == artist].groupby(combined_audio_data_year_user['endTime'].dt.to_period('M')).agg(
            total_hours=('hPlayed', 'sum')
        )
        fig.add_trace(go.Scatter(
            x=artist_data.index.to_timestamp(),
            y=artist_data['total_hours'],
            mode='lines',
            stackgroup='one',
            name=artist,
            line=dict(shape='spline', color=colors_green[idx % len(colors_green)]) if idx % 2 == 0 else dict(shape='spline', color=colors_red[idx % len(colors_red)])
        ))
    
    fig.update_layout(
        xaxis_title='Time',
        yaxis_title='Total Hours Played',
        hovermode='x unified',
        plot_bgcolor='white',
        paper_bgcolor='white',
        showlegend=True,
        legend=dict(
            orientation="h",
            yanchor="bottom",
            y=1.02,
            xanchor="right",
            x=1
        ),
        margin=dict(t=20, b=20)
    )

    return fig

###____________________________________Music Metrics________________________________________________###

df = data.copy()
# Filter out rows with missing values in specified columns
df_filtered = df.dropna(subset=['danceability_%', 'energy_%', 'key', 'speechiness_%', 
                                 'acousticness_%', 'instrumentalness_%', 'liveness_%', 'valence_%'])

# Function to generate the metrics graph based on selected filters
def generate_metrics_graph(n_clicks_filters, n_clicks_generate, year, username, genre, artist, track, filter_value):
    fig = go.Figure()
    metrics = ['danceability_%', 'energy_%', 'speechiness_%', 'acousticness_%', 'instrumentalness_%', 'liveness_%', 'valence_%']
    track_color = '#c7e9c0'
    user_color = '#74c476' 
    artist_avg_color = '#fc9272'
    genre_avg_color = '#305e4a' 

    if n_clicks_filters > 0:
        if year is None and genre is None:
            # Filter data only by user
            data_filtered = df[df['username'] == username]
        elif year is None and genre is not None:
            # Filter data only by user and genre
            data_filtered = df[(df['username'] == username) & (df['genero'] == genre)]
        elif year is not None and genre is None:
            # Filter data only by user and year
            data_filtered = df[(df['year_Played'] == year) & (df['username'] == username)]
        else:
            # Filter data based on selected user, year and genre
            data_filtered = df[(df['year_Played'] == year) & (df['username'] == username) & (df['genero'] == genre)]

        user_avg = (data_filtered[metrics] * 100).mean()
        for metric, value in zip(metrics, user_avg):
            fig.add_trace(go.Bar(
                x=[metric],
                y=[value],
                hoverinfo='y',
                name=f'User Avg: {metric}',
                marker=dict(color=user_color),
                showlegend=True
            ))
        fig.update_layout(
            title="User Average Music Metrics",
            xaxis=dict(title='Metrics'),
            yaxis=dict(title='Percent (%)'),
            barmode='stack',
            showlegend=True,
            template='plotly_white',

        )
        if n_clicks_generate > 0:
            if artist is not None and track is not None:
                data = data_filtered[(data_filtered['artist_name'] == artist) & (data_filtered['track_name'] == track)]
                if len(data) == 0:
                    return {
                        'data': [],
                        'layout': {
                            'title': "No data found for the selected artist and track."
                        }
                    }

                values = (data[metrics] * 100).values[0]

                artist_avg = (data_filtered[data_filtered['artist_name'] == artist][metrics] * 100).mean()

                genre = data['genero'].values[0]
                genre_avg = (data_filtered[data_filtered['genero'] == genre][metrics] * 100).mean()

                if filter_value == 'artist_avg':
                    avg_values = artist_avg
                    avg_color = artist_avg_color
                    avg_name = 'Artist Avg'
                elif filter_value == 'genre_avg':
                    avg_values = genre_avg
                    avg_color = genre_avg_color
                    avg_name = f'{genre} Avg'
                else:
                    avg_values = None


                for i, metric in enumerate(metrics):
                    fig.add_trace(go.Bar(
                        x=[metric],
                        y=[values[i]],
                        hoverinfo='y',
                        name='Track',
                        marker=dict(color=track_color),
                        showlegend=i == 0
                    ))
                    if avg_values is not None:
                        fig.add_trace(go.Scatter(
                            x=[metric],
                            y=[avg_values[i]],
                            name=avg_name,
                            mode='lines+markers',
                            line=dict(color=avg_color, width=4),
                            fill='tozeroy',
                            showlegend=i == 0
                        ))

                    fig.update_layout(
                        barmode='stack',
                        showlegend=True,
                        template='plotly_white'
                    )

                fig.update_layout(
                    title=f"Music Metrics for {track} - {artist}",
                    xaxis=dict(title='Metrics'),
                    yaxis=dict(title='Percent (%)'),
                    barmode='stack',
                    showlegend=True,
                    template='plotly_white'
                )
            else:
                fig = go.Figure()
                for metric, value in zip(metrics, user_avg):
                    fig.add_trace(go.Bar(
                        x=[metric],
                        y=[value],
                        hoverinfo='y',
                        name=f'User Avg: {metric}',
                        marker=dict(color=user_color),
                        showlegend=True
                    ))
                fig.update_layout(
                    title="User Average Music Metrics",
                    xaxis=dict(title='Metrics'),
                    yaxis=dict(title='Percent (%)'),
                    barmode='stack',
                    showlegend=True,
                    template='plotly_white'
                )
        
    return fig

###________________________________________________________________________________________________###

# Define dash app__________________________________________________________________________________
app = dash.Dash(__name__, suppress_callback_exceptions=True)

# Define the Dash app Layout_______________________________________________________________________
# CSS styles with the emoji animation and image zoom animation
external_stylesheets = ['https://codepen.io/chriddyp/pen/bWLwgP.css', '/assets/style.css']

# Modify the options list comprehension to include specific names based on the usernames
username_options = [{'label': f"{user_names[user]}", 'value': user} for user in user_names.keys()]

# Define the main filters popup structure with CSS
modal = html.Div(
    id='modal',
    className='modal',
    style={'display': 'block'},
    children=[
        html.Div(
            id='modal-content',
            className='modal-content',
            children=[
                html.Span('Close', id='close-modal-btn', className='close'),
                html.H2('Filters'),
                html.Div(
                    className='dropdown-container',
                    children=[
                        html.Div([
                            html.Label('Select User'),
                            dcc.Dropdown(
                                id='user-modal-dropdown',
                                options=username_options,
                                value=None,
                                searchable=True,
                            )
                        ], className='dropdown-item'),
                        html.Div([
                            html.Label('Select Year'),
                            dcc.Dropdown(
                                id='year-modal-dropdown',
                                options=[{'label': str(year), 'value': year} for year in range(2020, 2024)],
                                value=None,
                                searchable=True,
                            )
                        ], className='dropdown-item'),
                        html.Div([
                            html.Label('Select Genre'),
                            dcc.Dropdown(
                                id='genre-modal-dropdown',
                                options=[{'label': str(genre), 'value': genre} for genre in sorted(unique_genres.unique())],
                                value=None,
                                searchable=True,
                            )
                        ], className='dropdown-item'),
                    ],
                    style={'display': 'flex', 'gap': '20px'}
                ),
                html.Div(
                    children=[
                        html.Button('Apply Filters', id='apply-filters-btn', n_clicks=0, className='apply-filter-button')
                    ],
                    style={'textAlign': 'center', 'marginTop': '30px'}
                )
            ]
        )
    ]
)

# Define the main layout of the Dash app
app.layout = html.Div(
    children=[
        html.Div(
            children=[
                html.Div(
                    children=[
                        html.P(children="🎼", className="header-emoji"),
                        html.H1(
                            children="Know Your Song", className="header-title"
                        ),
                        html.P(
                            children=(
                                "Everything you need to know about your music behaviour"
                            ),
                            className="header-description",
                        ),
                    ],
                    className="header",
                ),
                html.Div(
                    className="open-filter-container",
                    children=[
                        html.Button('Open Filters', id='open-modal-btn', n_clicks=0, className='open-filter-btn'),
                    ], style={'textAlign': 'center', 'marginTop': '20px'}
                ),
                html.Div(
                    id='user-info',
                    className="user-info-container",
                    n_clicks=0,
                ),
            ],
            className="header-container",
        ),
        modal,
        html.Div(
            children=[
                html.Div(
                    children=[
                        html.H3("Geographic distribution of your music", className="graph-title"),
                        dcc.Graph(
                            id="geo-chart",
                            config={"displayModeBar": False},
                            className="chart",
                        ),
                        html.Button('Reset', id='reset-button', className='reset-button', n_clicks=0, style={'position': 'absolute', 'top': '10px', 'right': '10px'}),
                    ],
                    className="card-2",
                ),
                html.Div(
                    id="country-info",
                    className="info-message-container",
                ),
            ],
            className="wrapper-2",
        ),
        html.Div(
            children=[
                html.Div(
                    id="top-artists",
                    children=[
                        html.H3("Top 5 Most Streamed Artists", className="graph-title"),
                        html.Table(
                            id='top-artists-table',
                            children=[
                                html.Thead(
                                    html.Tr([
                                        html.Th("Cover", style={'text-align': 'center'}),
                                        html.Th("Hours", style={'text-align': 'center'}),
                                        html.Th("Artist Name", style={'text-align': 'center'})
                                    ])
                                ),
                                html.Tbody(
                                    id='table-body'
                                )
                            ],
                            className="table",
                        )
                    ],
                    className="card",
                ),
                html.Div(
                    id="top-tracks",
                    children=[
                        html.H3("Top 5 Most Streamed Tracks", className="graph-title"),
                        html.Table(
                            id='top-tracks-table',
                            children=[
                                html.Thead(
                                    html.Tr([
                                        html.Th("Cover", style={'text-align': 'center'}),
                                        html.Th("Hours", style={'text-align': 'center'}),
                                        html.Th("Track Name", style={'text-align': 'center'})
                                    ])
                                ),
                                html.Tbody(
                                    id='table2-body'
                                )
                            ],
                            className="table",
                        )
                    ],
                    className="card",
                ),
            ],
            className="wrapper1",
        ),
        html.Div(
            children=[
                html.Div(
                    children=[
                        html.H3("Most listened song of each month", className="graph-title"),
                        dcc.Graph(
                            id="song-chart",
                            config={"displayModeBar": False},
                            className="chart",
                        ),
                    ],
                    className="card",
                ),
                html.Div(
                    children=[
                        html.H3("Most listened artist of each month", className="graph-title"),
                        html.Div(
                            children=[
                                dcc.Graph(
                                    id="artist-chart",
                                    config={"displayModeBar": False},
                                    className="chart",
                                ),
                            ],
                            style={'text-align': 'center', 'position': 'relative'}
                        ),
                        html.Button("Reset", id="reset-button_2", className="reset-btn", style={'position': 'absolute', 'top': '10px', 'right': '10px'}),
                        html.Div(
                            dcc.Graph(
                                id="bar-chart",
                                config={"displayModeBar": False},
                            ),
                            id='bar-container',
                            style={
                                'display': 'none',
                                'position': 'absolute',
                                'z-index': '1000',
                                'background': 'white',
                                'border': '1px solid #ccc',
                                'padding': '10px',
                                'width': 'calc(100% - 20px)',
                                'max-width': '900px',
                                'overflow': 'hidden'
                            }
                        ),
                    ],
                    className="card",
                    style={'position': 'relative'}
                ),
            ],
            className="wrapper2",
        ),
        html.Div(
            children=[
                html.Div(
                    children=[
                        html.H3("Streamgraph of Listening History Over Time", className="graph-title"),
                        dcc.Graph(
                            id="streamgraph-chart",
                            config={"displayModeBar": False},
                            className="chart",
                        ),
                    ],
                    className="card",
                ),
                html.Div(
                    children=[
                        html.H3("Music Metrics", className="graph-title"),
                        dcc.Graph(
                            id="metric-graph",
                            config={"displayModeBar": False},
                            className="chart",
                        ),
                        html.Button('Open Filters', id='open-popup-btn', n_clicks=0, className='open-popup-button'),
                        html.Div(
                            id='popup-metrics',
                            className='popup-metrics',
                            children=[
                                html.Div(
                                    className='popup-content',
                                    children=[
                                        html.Span('Close', id='close-popup-btn', className='close'),
                                        html.Div(
                                            className="dropdown-container",
                                            children=[
                                                html.Div(
                                                    className="dropdown-container",
                                                    children=[
                                                        html.Label("Artist:"),
                                                        dcc.Dropdown(
                                                            id='artist-dropdown',
                                                            options=[{'label': artist, 'value': artist} for artist in sorted(df_filtered['artist_name'].unique())],
                                                            value=None,
                                                            searchable=True,
                                                            clearable=True,
                                                            className="dropdown green"
                                                        ),
                                                    ],
                                                ),
                                                html.Div(
                                                    className="dropdown-container",
                                                    children=[
                                                        html.Label("Track:"),
                                                        dcc.Dropdown(
                                                            id='track-dropdown',
                                                            options=[],
                                                            value=None,
                                                            searchable=True,
                                                            clearable=True,
                                                            className="dropdown green"
                                                        ),
                                                    ],
                                                ),
                                                html.Div(
                                                    className="dropdown-container",
                                                    children=[
                                                        html.Label("Filter:"),
                                                        dcc.Dropdown(
                                                            id='filter-dropdown',
                                                            options=[
                                                                {'label': 'Average Artist', 'value': 'artist_avg'},
                                                                {'label': 'Average Genre', 'value': 'genre_avg'}
                                                            ],
                                                            value=None,
                                                            searchable=False,
                                                            clearable=True,
                                                            className="dropdown green"
                                                        ),
                                                    ],
                                                ),
                                                html.Button('Generate Visualization', id='generate-btn', n_clicks=0, className='generate-button'),
                                            ],
                                        ),
                                    ],
                                ),
                            ],
                            style={'display': 'none'}
                        ),
                    ],
                    className="card",
                    style ={'position': 'relative'}
                ),
                dcc.Store(id='popup-visible', data=False),
            ],
            className="wrapper3",
        ),
    ]
)

# Define the Dash app Callbacks___________________________________________________________________
# Callback to toggle filters popup display
@app.callback(
    Output('modal', 'style'),
    [Input('open-modal-btn', 'n_clicks'),
     Input('close-modal-btn', 'n_clicks')],
    [State('modal', 'style')]
)
def toggle_modal(open_clicks, close_clicks, style):
    ctx = dash.callback_context
    if ctx.triggered_id:
        button_id = ctx.triggered_id.split('.')[0]
        if button_id == 'open-modal-btn':
            if open_clicks is not None and (close_clicks is None or open_clicks >= close_clicks):
                style['display'] = 'block'  # Show the modal
        elif button_id == 'close-modal-btn':
            style['display'] = 'none'  # Hide the modal
    return style

# Callback to update the user info div based on the selected username
@app.callback(
    Output('user-info', 'children'),
    [Input('apply-filters-btn', 'n_clicks'),
     Input('user-info', 'n_clicks'),
     Input('user-modal-dropdown', 'value')],
    prevent_initial_call=True # Prevent the callback from running at the start
)
def update_user_info(n_clicks, n_clicks_image, username):
    if n_clicks > 0:
        return generate_habit_indicator(n_clicks, n_clicks_image, username)

# Callback to hide the user-info pop-up after a certain period of time
@app.callback(
    Output('popup', 'style'),
    [Input('user-info', 'n_clicks')],
    [State('popup', 'style')]
)
def hide_popup(n_clicks, style):
    if n_clicks:
        # If the image is clicked, wait for 5 seconds before hiding the pop-up
        time.sleep(4)
        style['display'] = 'none'
    return style

# Callback to update the map based on the selected filters
@app.callback(
    [Output('geo-chart', 'figure'), Output('country-info', 'children')],
    [Input('apply-filters-btn', 'n_clicks'),
     Input('year-modal-dropdown', 'value'),
     Input('user-modal-dropdown', 'value'),
     Input('genre-modal-dropdown', 'value'),
     Input('geo-chart', 'clickData'),
     Input('reset-button', 'n_clicks')],
    prevent_initial_call=True # Prevent the callback from running at the start
)
def update_geomap(n_clicks, year, username, genre, click_data, reset_button_clicks):
    ctx = callback_context
    triggered_input = ctx.triggered[0]["prop_id"].split(".")[0] if ctx.triggered else None

    if triggered_input == 'geo-chart':
        # Handle click event on the map
        clicked_country = None
        clicked_country_info = None
        
        if click_data and 'points' in click_data:
            # Extract ISO A3 code of clicked country
            clicked_country_data = click_data['points'][0]
            iso_a3 = clicked_country_data.get('location')

            if iso_a3:
                # Lookup latitude and longitude based on ISO A3 code
                if iso_a3 in iso_a3_to_coordinates:
                    lat = iso_a3_to_coordinates[iso_a3]['lat']
                    lon = iso_a3_to_coordinates[iso_a3]['lon']
                    clicked_country = {"location": iso_a3, "lat": lat, "lon": lon}

                    # Prepare information about the clicked country for display
                    clicked_country_info = map_popup(n_clicks, username, year, iso_a3=iso_a3)

        return generate_map(n_clicks, year=year, username=username, genre=genre, clicked_country=clicked_country), clicked_country_info or ''
    elif triggered_input == 'reset-button' and reset_button_clicks:
        # Handle click event on the reset button
        fig = generate_map(n_clicks, year=year, username=username, genre=genre, clicked_country=None)
        side_info = map_popup(n_clicks, username, year)
        return fig, side_info
    else:
        # No event triggered, return default map and clear country info
        side_info = map_popup(n_clicks, username, year)
        return generate_map(n_clicks=n_clicks, year=year, username=username, genre=genre), side_info or ''

# Callback to update the top artists table based on the selected filters
@app.callback(
    Output('table-body', 'children'),
    [Input('year-modal-dropdown', 'value'),
     Input('user-modal-dropdown', 'value'),
     Input('genre-modal-dropdown', 'value'),
     Input('geo-chart', 'clickData'),
     Input('reset-button', 'n_clicks')],
    prevent_initial_call=True # Prevent the callback from running at the start
)
def update_top_artists_table(year, username, genre, click_data, reset_button_clicks):
    ctx = callback_context
    triggered_input = ctx.triggered[0]["prop_id"].split(".")[0] if ctx.triggered else None

    if triggered_input == 'geo-chart':
        if click_data and 'points' in click_data:
            # Extract ISO A3 code of clicked country
            clicked_country_data = click_data['points'][0]
            iso_a3 = clicked_country_data.get('location')
        
            if iso_a3:
                top_artists = get_top_artists(year, username, genre, clicked_country=iso_a3)
                table_rows = []
                for i in range(min(5, len(top_artists))):
                    artist_name = top_artists.iloc[i]['artist_name']
                    hPlayed = top_artists.iloc[i]['hPlayed']
                    hPlayed_rounded = math.ceil(hPlayed)
                    image_url = top_artists.iloc[i]['image_url']
                    table_row = html.Tr([
                        html.Td(
                            html.Div(
                                html.Img(src=image_url, style={'width': '50px', 'height': '50px', 'border-radius': '50%'}),
                                style={'display': 'flex', 'align-items': 'center', 'justify-content': 'center'},
                            ),
                        ),
                        html.Td(hPlayed_rounded, style={'text-align': 'center'}),
                        html.Td(artist_name, style={'text-align': 'center'})
                    ])
                    table_rows.append(table_row)
                return table_rows

    if triggered_input == 'reset-button' and reset_button_clicks:
        top_artists = get_top_artists(year, username, genre)
        table_rows = []
        for i in range(min(5, len(top_artists))):
            artist_name = top_artists.iloc[i]['artist_name']
            hPlayed = top_artists.iloc[i]['hPlayed']
            hPlayed_rounded = math.ceil(hPlayed)
            image_url = top_artists.iloc[i]['image_url']
            table_row = html.Tr([
                html.Td(
                    html.Div(
                        html.Img(src=image_url, style={'width': '50px', 'height': '50px', 'border-radius': '50%'}),
                        style={'display': 'flex', 'align-items': 'center', 'justify-content': 'center'},
                    ),
                ),
                html.Td(hPlayed_rounded, style={'text-align': 'center'}),
                html.Td(artist_name, style={'text-align': 'center'})
            ])
            table_rows.append(table_row)
        return table_rows
        
    top_artists = get_top_artists(year, username, genre)
    table_rows = []
    for i in range(min(5, len(top_artists))):
        artist_name = top_artists.iloc[i]['artist_name']
        hPlayed = top_artists.iloc[i]['hPlayed']
        hPlayed_rounded = math.ceil(hPlayed)
        image_url = top_artists.iloc[i]['image_url']
        table_row = html.Tr([
                html.Td(
                    html.Div(
                        html.Img(src=image_url, style={'width': '50px', 'height': '50px', 'border-radius': '50%'}),
                        style={'display': 'flex', 'align-items': 'center', 'justify-content': 'center'},
                    ),
                ),
                html.Td(hPlayed_rounded, style={'text-align': 'center'}),
                html.Td(artist_name, style={'text-align': 'center'})
            ])
        table_rows.append(table_row)
    return table_rows

# Callback to update the top tracks table based on the selected filters
@app.callback(
    Output('table2-body', 'children'),
    [Input('year-modal-dropdown', 'value'),
     Input('user-modal-dropdown', 'value'),
     Input('genre-modal-dropdown', 'value'),
     Input('geo-chart', 'clickData'),
     Input('reset-button', 'n_clicks')],
    prevent_initial_call=True # Prevent the callback from running at the start
)
def update_top_tracks_table(year, username, genre, click_data, reset_button_clicks):
    ctx = callback_context
    triggered_input = ctx.triggered[0]["prop_id"].split(".")[0] if ctx.triggered else None

    if triggered_input == 'geo-chart':
        if click_data and 'points' in click_data:
            # Extract ISO A3 code of clicked country
            clicked_country_data = click_data['points'][0]
            iso_a3 = clicked_country_data.get('location')
        
            if iso_a3:
                top_tracks = get_top_tracks(year, username, genre, clicked_country=iso_a3)
                table_rows = []
                for i in range(min(5, len(top_tracks))):
                    track_name = top_tracks.iloc[i]['track_name']
                    hPlayed = top_tracks.iloc[i]['hPlayed']
                    hPlayed_rounded = math.ceil(hPlayed)
                    image_url = top_tracks.iloc[i]['image_url']
                    table_row = html.Tr([
                        html.Td(
                            html.Div(
                                html.Img(src=image_url, style={'width': '50px', 'height': '50px', 'border-radius': '50%'}),
                                style={'display': 'flex', 'align-items': 'center', 'justify-content': 'center'},
                            ),
                        ),
                        html.Td(hPlayed_rounded, style={'text-align': 'center'}),
                        html.Td(track_name, style={'text-align': 'center'})
                    ])
                    table_rows.append(table_row)
                return table_rows

    if triggered_input == 'reset-button' and reset_button_clicks:
        top_tracks = get_top_tracks(year, username, genre)
        table_rows = []
        for i in range(min(5, len(top_tracks))):
            track_name = top_tracks.iloc[i]['track_name']
            hPlayed = top_tracks.iloc[i]['hPlayed']
            hPlayed_rounded = math.ceil(hPlayed)
            image_url = top_tracks.iloc[i]['image_url']
            table_row = html.Tr([
                html.Td(
                    html.Div(
                        html.Img(src=image_url, style={'width': '50px', 'height': '50px', 'border-radius': '50%'}),
                        style={'display': 'flex', 'align-items': 'center', 'justify-content': 'center'},
                    ),
                ),
                html.Td(hPlayed_rounded, style={'text-align': 'center'}),
                html.Td(track_name, style={'text-align': 'center'})
            ])
            table_rows.append(table_row)
        return table_rows
    
    top_tracks = get_top_tracks(year, username, genre)
    table_rows = []
    for i in range(min(5, len(top_tracks))):
        track_name = top_tracks.iloc[i]['track_name']
        hPlayed = top_tracks.iloc[i]['hPlayed']
        hPlayed_rounded = math.ceil(hPlayed)
        image_url = top_tracks.iloc[i]['image_url']
        table_row = html.Tr([
            html.Td(
                    html.Div(
                        html.Img(src=image_url, style={'width': '50px', 'height': '50px', 'border-radius': '50%'}),
                        style={'display': 'flex', 'align-items': 'center', 'justify-content': 'center'},
                    ),
                ),
                html.Td(hPlayed_rounded, style={'text-align': 'center'}),
                html.Td(track_name, style={'text-align': 'center'})
            ])
        table_rows.append(table_row)
    return table_rows

# Callback to update the song chart based on the selected filters
@app.callback(
    Output('song-chart', 'figure'),
    [Input('apply-filters-btn', 'n_clicks'),
     Input('year-modal-dropdown', 'value'),
     Input('user-modal-dropdown', 'value'),
     Input('genre-modal-dropdown', 'value'),
     Input('geo-chart', 'clickData'),
     Input('reset-button', 'n_clicks')],
    prevent_initial_call=True # Prevent the callback from running at the start
)
def update_song_chart(n_clicks, year, username, genre, click_data, reset_button_clicks):
    ctx = callback_context
    triggered_input = ctx.triggered[0]["prop_id"].split(".")[0] if ctx.triggered else None

    if triggered_input == 'geo-chart':
        if click_data and 'points' in click_data:
            # Extract ISO A3 code of clicked country
            clicked_country_data = click_data['points'][0]
            iso_a3 = clicked_country_data.get('location')
        
            if iso_a3:
                return generate_tracks_plot(n_clicks, year, username, genre, clicked_country=iso_a3)
    if triggered_input == 'reset-button' and reset_button_clicks:
        return generate_tracks_plot(n_clicks, year, username, genre)
        
    return generate_tracks_plot(n_clicks, year, username, genre)

# Callback to display the bar plot when hovering over the artist chart
@app.callback(
    [Output('bar-chart', 'figure'),
     Output('bar-container', 'style')],
    [Input('apply-filters-btn', 'n_clicks'),
     Input('year-modal-dropdown', 'value'),
     Input('artist-chart', 'hoverData'),
     Input('reset-button_2', 'n_clicks')],
    [State('bar-container', 'style')],
    prevent_initial_call=True # Prevent the callback from running at the start
)
def display_hover_bar(apply_n_cliks, year, hoverData, n_clicks, current_style):
    ctx = dash.callback_context
    triggered_input = ctx.triggered[0]["prop_id"].split(".")[0] if ctx.triggered else None

    if triggered_input == 'reset-button_2' and n_clicks:
        return go.Figure(), {'display': 'none'}
    
    if year is None:
        # Extract the artist and month from hover data
        point = hoverData['points'][0]
        artist_name = point['text']
        month = point['label']
        
        # Generate the bar plot
        fig = generate_bar_pie(artist_name, month)
        
        # Calculate the position of the bar plot based on the hover position
        bbox = point['bbox']
        x = bbox['x0'] + (bbox['x1'] - bbox['x0']) / 2
        y = bbox['y0'] + (bbox['y1'] - bbox['y0']) / 2
        
        # Adjust the style to position the bar plot
        style = {
            'display': 'block',
            'left': f'{x}px',
            'top': f'{y}px',
        }
        
        return fig, style
    elif triggered_input == 'apply-filters-btn' and apply_n_cliks:
        return go.Figure(), {'display': 'none'}

# Callback to update the artist chart based on the selected filters
@app.callback(
    Output('artist-chart', 'figure'),
    [Input('apply-filters-btn', 'n_clicks'),
     Input('year-modal-dropdown', 'value'),
     Input('user-modal-dropdown', 'value'),
     Input('genre-modal-dropdown', 'value'),
     Input('geo-chart', 'clickData'),
     Input('reset-button', 'n_clicks')],
    prevent_initial_call=True # Prevent the callback from running at the start
)
def update_artist_chart(n_clicks, year, username, genre, click_data, reset_button_clicks):
    ctx = callback_context
    triggered_input = ctx.triggered[0]["prop_id"].split(".")[0] if ctx.triggered else None

    if triggered_input == 'geo-chart':
        if click_data and 'points' in click_data:
            # Extract ISO A3 code of clicked country
            clicked_country_data = click_data['points'][0]
            iso_a3 = clicked_country_data.get('location')
        
            if iso_a3:
                return generate_pie_chart(n_clicks, year, username, genre, clicked_country=iso_a3)
    if triggered_input == 'reset-button' and reset_button_clicks:
        return generate_pie_chart(n_clicks, year, username, genre)
        
    return generate_pie_chart(n_clicks, year, username, genre)

# Callback to update the Streamgraph based on the selected filters
@app.callback(
    Output('streamgraph-chart', 'figure'),
    [Input('apply-filters-btn', 'n_clicks'),
     Input('year-modal-dropdown', 'value'),
     Input('user-modal-dropdown', 'value'),
     Input('genre-modal-dropdown', 'value'),
     Input('geo-chart', 'clickData'),
     Input('reset-button', 'n_clicks')],
    prevent_initial_call=True # Prevent the callback from running at the start
)
def update_streamgraph_chart(n_clicks, year, username, genre, click_data, reset_button_clicks):
    ctx = callback_context
    triggered_input = ctx.triggered[0]["prop_id"].split(".")[0] if ctx.triggered else None

    if triggered_input == 'geo-chart':
        if click_data and 'points' in click_data:
            # Extract ISO A3 code of clicked country
            clicked_country_data = click_data['points'][0]
            iso_a3 = clicked_country_data.get('location')
        
            if iso_a3:
                return generate_streamgraph(n_clicks, year, username, genre, clicked_country=iso_a3)
    if triggered_input == 'reset-button' and reset_button_clicks:
        return generate_streamgraph(n_clicks, year, username, genre)    
    
    return generate_streamgraph(n_clicks, year, username, genre)

# Callback to toggle the visibility of the filters pop-up of the metrics graph
@app.callback(
    Output('popup-metrics', 'style'),
    [Input('open-popup-btn', 'n_clicks'),
     Input('close-popup-btn', 'n_clicks')],
    [State('popup-visible', 'data')],
)
def toggle_popup(open_n_clicks, close_n_clicks, is_visible):
    ctx = dash.callback_context

    if not ctx.triggered:
        return {'display': 'none'}
    else:
        button_id = ctx.triggered[0]['prop_id'].split('.')[0]

    if button_id == 'open-popup-btn' and not is_visible:
        return {'display': 'flex'}
    elif button_id == 'close-popup-btn' and is_visible:
        return {'display': 'none'}

    return {'display': 'none'}

# Callback to update artist dropdown options based on selected user, on the filters pop-up of the metrics graph 
@app.callback(
    Output('artist-dropdown', 'options'),
    [Input('user-modal-dropdown', 'value'),
     Input('geo-chart', 'clickData'),
     Input('reset-button', 'n_clicks')]
)
def update_artist_dropdown(username, click_data, reset_button_clicks):
    ctx = callback_context
    triggered_input = ctx.triggered[0]["prop_id"].split(".")[0] if ctx.triggered else None

    if username is None:
        return []
    else:
        if triggered_input == 'geo-chart':
            if click_data and 'points' in click_data:
                # Extract ISO A3 code of clicked country
                clicked_country_data = click_data['points'][0]
                iso_a3 = clicked_country_data.get('location')
            
                if iso_a3:
                    artists = sorted(df_filtered[(df_filtered['Country'] == iso_a3) & (df_filtered['username'] == username)]['artist_name'].unique())
                    options = [{'label': artist, 'value': artist} for artist in artists]
                    return options
                
        if triggered_input == 'reset-button' and reset_button_clicks:
            artists = sorted(df_filtered[df_filtered['username'] == username]['artist_name'].unique())
            options = [{'label': artist, 'value': artist} for artist in artists]
            return options
        
        artists = sorted(df_filtered[df_filtered['username'] == username]['artist_name'].unique())
        options = [{'label': artist, 'value': artist} for artist in artists]
        return options

# Callback to update track dropdown options based on selected artist, on the filters pop-up of the metrics graph 
@app.callback(
    Output('track-dropdown', 'options'),
    [Input('artist-dropdown', 'value')]
)
def update_track_dropdown(artist):
    if artist is None:
        return []
    else:
        tracks = sorted(df_filtered[df_filtered['artist_name'] == artist]['track_name'].unique())
        options = [{'label': track, 'value': track} for track in tracks]
        return options

# Callback to update the metrics graph based on the selected filters
@app.callback(
    Output('metric-graph', 'figure'),
    [Input('apply-filters-btn', 'n_clicks'),
     Input('generate-btn', 'n_clicks'),
     Input('year-modal-dropdown', 'value'),
     Input('user-modal-dropdown', 'value'),
     Input('genre-modal-dropdown', 'value'),
     Input('artist-dropdown', 'value'),
     Input('track-dropdown', 'value'),
     Input('filter-dropdown', 'value')],
    prevent_initial_call=True # Prevent the callback from running at the start
)
def update_metrics_graph(n_clicks_filters, n_clicks_generate, year, username, genre, artist, track, filter_value):
    return generate_metrics_graph(n_clicks_filters, n_clicks_generate, year, username, genre, artist, track, filter_value)

# Execute the Dash app____________________________________________________________________________
if __name__ == "__main__":
    app.run_server(debug=True)