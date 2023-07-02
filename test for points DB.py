from dash import Dash, dcc, html
from dash.dependencies import Output, Input, State
import requests
import sqlite3

external_stylesheets = ['assets/style.css']
app = Dash(__name__, external_stylesheets=external_stylesheets)

def read_json_url(url):
    response = requests.get(url)
    if response.status_code == 200:
        json_response = response.json()
        team_info_list = json_response["allinfo"]["TeamInfoList"]
        total_player_list = json_response["allinfo"]["TotalPlayerList"]
        return team_info_list, total_player_list
    else:
        raise ValueError(f"Unable to fetch data from URL. Status code: {response.status_code}")


def get_total_points(team_name):
    conn = sqlite3.connect("PATH TO SQL DB")
    cursor = conn.cursor()

    select_statement = "SELECT total_points FROM final_table WHERE team_name = ?"
    cursor.execute(select_statement, (team_name,))
    result = cursor.fetchone()
    if result:
        total_points = result[0]
    else:
        total_points = 0

    cursor.close()
    conn.close()

    return total_points


app.layout = html.Div(
    [
        html.Div(id="splash-screen-container"),
        dcc.Store(id="team-info-data-store"),
        dcc.Store(id="total-player-data-store"),
        dcc.Interval(id="update-interval-component", interval=2 * 1000, n_intervals=0),
        dcc.Interval(id="display-interval-component", interval=10 * 1000, n_intervals=0)
    ],
    style={"width": "1300px", "margin": "0 auto"}
)


@app.callback(
    Output("splash-screen-container", "children"),
    Input("display-interval-component", "n_intervals"),
    State("team-info-data-store", "data"),
    State("total-player-data-store", "data")
)
def update_splash_screens(n, team_info_data, total_player_data):
    team_info_data, total_player_data = read_json_url("http://127.0.0.1:5000/data1")

    start_index = (n // 4) % len(team_info_data)
    teams = team_info_data[start_index:] + team_info_data[:start_index]
    num_teams = len(teams)
    num_screens = (num_teams + 3) // 4
    current_screen = n % num_screens
    start_team_index = current_screen * 4
    end_team_index = min(start_team_index + 4, num_teams)
    splash_screens = []

    for i in range(start_team_index, end_team_index):
        team = teams[i]
        team_name = team["teamName"]
        total_points = get_total_points(team_name)

        splash_screens.append(html.Div(
            [
                html.Div(
                    [
                        html.Img(src=f"/assets/logos/{team_name}.png", className="team-logo"),
                        html.Div(
                            [
                                html.Div(team_name, className="team-name"),
                                html.Div(f"Total Points: {total_points}", className="team-rank"),
                                html.Div(f"Eliminations: {team['killNum']}", className="team-eliminations"),
                            ],
                            className="team-info",
                        ),
                    ],
                    className="team-logo-info-container",
                ),
            ],
            className="team-container",
            id=f"team-{i + 1}",
            style={
                "background-image": "url(assets/poze/test.png)",
                "background-repeat": "no-repeat",
                "background-size": "cover",
                "background-position": "center"
            }
        ))

    if end_team_index % 4 != 0:
        num_placeholders = 4 - (end_team_index % 4)
        for i in range(num_placeholders):
            placeholder_index = end_team_index + i + 1
            splash_screens.append(html.Div(
                [
                    html.Div(
                        [
                            html.Div(
                                [
                                    #html.Div("", className="team-name-placeholder"),
                                    #html.Div("", className="team-rank-placeholder"),
                                    #html.Div("", className="team-eliminations-placeholder"),
                                ],
                                className="team-info",
                            ),
                        ],
                        className="team-logo-info-container",
                    ),
                ],
                className="team-container",
                id=f"team-placeholder-{placeholder_index}",
                style={
                    "background-image": "url(assets/poze/test.png)",
                    "background-repeat": "no-repeat",
                    "background-size": "cover",
                    "background-position": "center"
                }
            ))

    return splash_screens


if __name__ == "__main__":
    app.run_server(debug=False, port=8054, host="127.0.0.1")
