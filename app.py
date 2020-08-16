# Import required libraries
import pickle
import calendar
import copy
import pathlib
import dash
import math
import datetime as dt
import pandas as pd
from dash.dependencies import Input, Output, State, ClientsideFunction
import dash_core_components as dcc
import dash_html_components as html
import plotly.graph_objs as go


# get relative data folder
PATH = pathlib.Path(__file__).parent
DATA_PATH = PATH.joinpath("data").resolve()

app = dash.Dash(
    __name__, meta_tags=[{"name": "viewport", "content": "width=device-width"}]
)
server = app.server

# Create controls
country_name_cn_en = pd.read_csv(DATA_PATH.joinpath('country_name_cn_en.csv'))
COUNTRIES = country_name_cn_en.cn_name
# Globals
COLUMNS = ['today_confirm', 'today_dead', 'today_heal', 'today_suspect']
NUM_TO_CN_MONTH = {1: '一月', 2: '二月', 3: '三月', 4: '四月', 5: '五月', 6: '六月',
                   7: '七月', 8: '八月', 9: '九月', 10: '十月', 11: '十一月', 12: '十二月'}
DCAT_DICT = {'confirm': 'today_confirm', 'dead': 'today_dead', 'heal': 'today_heal', 'suspect': 'today_suspect'}
CNEN_DICT = dict(zip(country_name_cn_en.cn_name, country_name_cn_en.en_name))

country_options = [
    {"label": country, "value": country} for country in COUNTRIES
]

# Helpers
def get_dates(df):
    df['date'] = pd.to_datetime(df.date)
    df['year'] = df.date.apply(lambda x: x.year)
    df['month'] = df.date.apply(lambda x: x.month)
    df['day'] = df.date.apply(lambda x: x.day)

alltime_world = pd.read_csv(DATA_PATH.joinpath('alltime_world.csv'))
get_dates(alltime_world)

# Create global chart template
mapbox_access_token = "pk.eyJ1IjoicGxvdGx5bWFwYm94IiwiYSI6ImNrOWJqb2F4djBnMjEzbG50amg0dnJieG4ifQ.Zme1-Uzoi75IaFbieBDl3A"

layout = dict(
    autosize=True,
    automargin=True,
    margin=dict(l=30, r=30, b=20, t=40),
    hovermode="closest",
    plot_bgcolor="#F9F9F9",
    paper_bgcolor="#F9F9F9",
    legend=dict(font=dict(size=10), orientation="h"),
    title="各国数据地图",
    mapbox=dict(
        accesstoken=mapbox_access_token,
        style="light",
        center=dict(lon=-78.05, lat=42.54),
        zoom=7,
    ),
)

# Create app layout
# def serve_layout():
    # alltime_world = pd.read_csv(DATA_PATH.joinpath('alltime_world.csv'))
    # return html.Div(
app.layout = html.Div(
        [
            dcc.Store(id="aggregate_data"),
            # empty Div to trigger javascript file for graph resizing
            html.Div(id="output-clientside"),
            html.Div(
                [
                    html.Div(
                        [
                            html.Img(
                                src=app.get_asset_url("shulun-logo.png"),
                                id="plotly-image",
                                style={
                                    "height": "60px",
                                    "width": "auto",
                                    "margin-bottom": "25px",
                                },
                            )
                        ],
                        className="one-third column",
                    ),
                    html.Div(
                        [
                            html.Div(
                                [
                                    html.H3(
                                        "COVID-19肺炎疫情实时数据",
                                        style={"margin-bottom": "0px"},
                                    ),
                                    html.H5(
                                        id="clockbox",
                                        style={"margin-top": "0px"},
                                    ),
                                ]
                            )
                        ],
                        className="one-half column",
                        id="title",
                    ),
                    html.Div(
                        [
                            html.A(
                                html.Button("更多信息", id="learn-more-button"),
                                href="https://wp.m.163.com/163/page/news/virus_report/index.html",
                            )
                        ],
                        className="one-third column",
                        id="button",
                    ),
                ],
                id="header",
                className="row flex-display",
                style={"margin-bottom": "25px"},
            ),
            html.Div(
                [
                    html.Div(
                        [
                            html.P(
                                "选择月份:",
                                className="control_label",
                            ),
                            dcc.RangeSlider(
                                id="month_slider",
                                min=1,
                                max=12,
                                value=[1, 8],
                                className="dcc_control",
                            ),
                            html.Div(
                                "",
                                style={'padding': 10}
                            ),
                            html.P("选择数据种类:", className="control_label"),
                            dcc.RadioItems(
                                id="dcat_selector",
                                options=[
                                    {"label": "确诊", "value": "confirm"},
                                    {"label": "死亡", "value": "dead"},
                                    {"label": "治愈", "value": "heal"},
                                    {"label": "疑似", "value": "suspect"},
                                ],
                                value="confirm",
                                labelStyle={"display": "inline-block"},
                                className="dcc_control",
                            ),
                            html.Div(
                                "",
                                style={'padding': 10}
                            ),
                            html.P("选择国家（或地区）:", className="control_label"),
                            dcc.RadioItems(
                                id="country_selector",
                                options=[
                                    {"label": "全部国家", "value": "all"},
                                    {"label": "中国", "value": "china"},
                                    {"label": "自定义", "value": "custom"},
                                ],
                                value="china",
                                labelStyle={"display": "inline-block"},
                                className="dcc_control",
                            ),
                            dcc.Dropdown(
                                id="countries",
                                options=country_options,
                                multi=True,
                                value=list(COUNTRIES),
                                className="dcc_control",
                            ),
                        ],
                        className="pretty_container four columns",
                        id="cross-filter-options",
                    ),
                    html.Div(
                        [
                            html.Div(
                                [
                                    html.Div(
                                        [html.H6(id="total_confirm"), html.P("全部确诊")],
                                        id="confirm",
                                        className="mini_container",
                                    ),
                                    html.Div(
                                        [html.H6(id="total_dead"), html.P("全部死亡")],
                                        id="dead",
                                        className="mini_container",
                                    ),
                                    html.Div(
                                        [html.H6(id="total_heal"), html.P("全部治愈")],
                                        id="heal",
                                        className="mini_container",
                                    ),
                                    html.Div(
                                        [html.H6(id="total_suspect"), html.P("全部疑似")],
                                        id="suspect",
                                        className="mini_container",
                                    ),
                                ],
                                id="info-container",
                                className="row container-display",
                            ),
                            html.Div(
                                [dcc.Graph(id="count_graph")],
                                id="countGraphContainer",
                                className="pretty_container",
                            ),
                        ],
                        id="right-column",
                        className="eight columns",
                    ),
                ],
                className="row flex-display",
            ),
            html.Div(
                [
                    html.Div(
                        [dcc.Graph(id="main_graph")],
                        className="pretty_container seven columns",
                    ),
                    html.Div(
                        [dcc.Graph(id="individual_graph")],
                        className="pretty_container five columns",
                    ),
                ],
                className="row flex-display",
            ),
            html.Div(
                [
                    html.Div(
                        [dcc.Graph(id="pie_graph")],
                        className="pretty_container seven columns",
                    ),
                    html.Div(
                        [dcc.Graph(id="aggregate_graph")],
                        className="pretty_container five columns",
                    ),
                ],
                className="row flex-display",
            ),
            html.Div(alltime_world.to_json(orient='split'), id='cache', style={'display': 'none'})
        ],
        id="mainContainer",
        style={"display": "flex", "flex-direction": "column"},
    )

# app.layout = serve_layout


# Helper functions
def human_format(num):
    if num == 0:
        return "0"

    magnitude = int(math.log(num, 1000))
    mantissa = str(int(num / (1000 ** magnitude)))
    return mantissa + ["", "K", "M", "G", "T", "P"][magnitude]


def filter_dataframe(df, countries, month_slider):
    dff = df[
        df["name"].isin(countries)
        & (df["date"] > dt.datetime(2020, month_slider[0], 1))
        & (df["date"] < dt.datetime(2020, month_slider[1],
                calendar.monthrange(2020, month_slider[1])[1]))
    ]
    return dff


def produce_individual(df, countries, month_slider):
    
    df = filter_dataframe(df, countries, month_slider)
    df = df.groupby(['month'])[COLUMNS].sum()
    df['confirm_cum'] = df.today_confirm.cumsum()
    df['dead_cum'] = df.today_dead.cumsum()
    df['heal_cum'] = df.today_heal.cumsum()
    
    return list(df.index), list(df.dead_cum / df.confirm_cum), list(df.heal_cum / df.confirm_cum)


def produce_aggregate(df, countries, month_slider, agg_by='month'):

    df = filter_dataframe(df, countries, month_slider)
    df = df.groupby([agg_by])[COLUMNS].sum()
    df['confirm_cum'] = df.today_confirm.cumsum()
    df['dead_cum'] = df.today_dead.cumsum()
    df['heal_cum'] = df.today_heal.cumsum()
    df['suspect_cum'] = df.today_suspect.cumsum()

    return list(df.index), df.confirm_cum, df.dead_cum, df.heal_cum, df.suspect_cum


# Create callbacks
app.clientside_callback(
    ClientsideFunction(namespace="clientside", function_name="resize"),
    Output("output-clientside", "children"),
    [Input("count_graph", "figure")],
)

# @app.callback(
#     Output('cache', 'children'),
#     [Input('file-timestamp', 'value')]
# )
# def update_cache(value):
#     return alltime_world.to_json(orient='split')


# Radio -> multi
@app.callback(Output("countries", "value"), [Input("country_selector", "value")])
def display_ctype(selector):
    # print(selector)
    if selector == "all":
        return list(COUNTRIES)
    elif selector == "china":
        return ["中国"]
    return []


# Selectors -> confirm
@app.callback(
    Output("total_confirm", "children"),
    [
        Input("cache", "children"),
        Input("countries", "value"),
        Input("month_slider", "value"),
    ],
)
def update_confirm(json_data, countries, month_slider):

    alltime_world = pd.read_json(json_data, orient='split')
    get_dates(alltime_world)
    dff = filter_dataframe(alltime_world, countries, month_slider)
    
    return dff.today_confirm.sum()


# Selectors -> dead
@app.callback(
    Output("total_dead", "children"),
    [
        # Input("cache", "children"),
        Input("countries", "value"),
        Input("month_slider", "value"),
    ],
)
# def update_dead(json_data, countries, month_slider):
def update_dead(countries, month_slider):

    # alltime_world = pd.read_json(json_data, orient='split')
    # get_dates(alltime_world)
    dff = filter_dataframe(alltime_world, countries, month_slider)

    return dff.today_dead.sum()


# Selectors -> heal
@app.callback(
    Output("total_heal", "children"),
    [
        # Input("cache", "children"),
        Input("countries", "value"),
        Input("month_slider", "value"),
    ],
)
# def update_heal(json_data, countries, month_slider):
def update_heal(countries, month_slider):

    # alltime_world = pd.read_json(json_data, orient='split')
    # get_dates(alltime_world)
    dff = filter_dataframe(alltime_world, countries, month_slider)

    return dff.today_heal.sum()


# Selectors -> suspect
@app.callback(
    Output("total_suspect", "children"),
    [
        # Input("cache", "children"),
        Input("countries", "value"),
        Input("month_slider", "value"),
    ],
)
# def update_suspect(json_data, countries, month_slider):
def update_suspect(countries, month_slider):
    
    # alltime_world = pd.read_json(json_data, orient='split')
    # get_dates(alltime_world)
    dff = filter_dataframe(alltime_world, countries, month_slider)

    return dff.today_suspect.sum()


# Selectors -> main graph
@app.callback(
    Output("main_graph", "figure"),
    [
        # Input("cache", "children"),
        Input("dcat_selector", "value"),
        Input("month_slider", "value"),
    ]
)
# def make_main_figure(json_data, dcat, month_slider):
def make_main_figure(dcat, month_slider):

    # alltime_world = pd.read_json(json_data, orient='split')
    # get_dates(alltime_world)
    df = filter_dataframe(alltime_world, COUNTRIES, month_slider)
    df['en_name'] = [CNEN_DICT[k] if k in CNEN_DICT else '' for k in df['name']]
    df = df[df.en_name!='']
    df = df.groupby('en_name')[COLUMNS].sum()

    trace = go.Choropleth(
        locations=df.index,
        z=df[DCAT_DICT[dcat]],
        locationmode='country names',
        colorscale='matter',
        colorbar_title="病例数"
    )

    if dcat == 'confirm':
        trace['colorbar_title'] = "确诊数"
    elif dcat == 'dead':
        trace['colorbar_title'] = "死亡数"
    elif dcat == 'heal':
        trace['colorbar_title'] = "治愈数"
    elif dcat == 'suspect':
        trace['colorbar_title'] = "疑似数"

    layout['title_text'] = "COVID-19肺炎疫情全球地图"
    layout['geo'] = dict(
        showframe=False,
        showcoastlines=False,
        projection_type='equirectangular'
    )
    layout['annotations'] = dict(
        x=0.5, y=0.1,
        text='COVID-19', showarrow=False
    )

    figure = dict(data=[trace], layout=layout)
    return figure


# Main graph -> individual graph
@app.callback(
    Output("individual_graph", "figure"), 
    [
        # Input("cache", "children"),
        Input("countries", "value"),
        Input("month_slider", "value"),
    ]
)
# def make_individual_figure(json_data, countries, month_slider):
def make_individual_figure(countries, month_slider):

    layout_individual = copy.deepcopy(layout)
    # alltime_world = pd.read_json(json_data, orient='split')
    # get_dates(alltime_world)
    index, ifr, irr = produce_individual(alltime_world, countries, month_slider)

    if index is None:
        annotation = dict(
            text="No data available",
            x=0.5,
            y=0.5,
            align="center",
            showarrow=False,
            xref="paper",
            yref="paper",
        )
        layout_individual["annotations"] = [annotation]
        data = []
    else:
        data = [
            dict(
                type="scatter",
                mode="lines+markers",
                name="感染死亡率",
                x=[NUM_TO_CN_MONTH[n] for n in index],
                y=ifr,
                line=dict(shape="spline", smoothing=2, width=1, color="#fac1b7"),
                marker=dict(symbol="diamond-open"),
            ),
            dict(
                type="scatter",
                mode="lines+markers",
                name="感染治愈率",
                x=[NUM_TO_CN_MONTH[n] for n in index],
                y=irr,
                line=dict(shape="spline", smoothing=2, width=1, color="#a9bb95"),
                marker=dict(symbol="circle-open"),
            ),
        ]
        layout_individual["title"] = "感染死亡率和治愈率"
        layout_individual['yaxis'] = dict(tickformat=".0%")

    figure = dict(data=data, layout=layout_individual)
    return figure


# Selectors, main graph -> aggregate graph
@app.callback(
    Output("aggregate_graph", "figure"),
    [
        # Input("cache", "children"),
        Input("countries", "value"),
        Input("month_slider", "value"),
    ],
)
# def make_aggregate_figure(json_data, countries, month_slider):
def make_aggregate_figure(countries, month_slider):

    layout_aggregate = copy.deepcopy(layout)
    # alltime_world = pd.read_json(json_data, orient='split')
    # get_dates(alltime_world)
    index, confirm_cum, dead_cum, heal_cum, suspect_sum = produce_aggregate(alltime_world, countries, month_slider)

    data = [
        dict(
            type="scatter",
            mode="markers",
            marker=dict(symbol='square', size=8),
            name="累计确诊病例",
            x=[NUM_TO_CN_MONTH[n] for n in index],
            y=confirm_cum,
            line=dict(shape="spline", smoothing="2", color="#F9ADA0"),
        ),
        dict(
            type="scatter",
            mode="markers",
            marker=dict(symbol='circle', size=8),
            name="累计死亡病例",
            x=[NUM_TO_CN_MONTH[n] for n in index],
            y=dead_cum,
            line=dict(shape="spline", smoothing="2", color="#849E68"),
        ),
        dict(
            type="scatter",
            mode="markers",
            marker=dict(symbol='cross', size=8),
            name="累计治愈病例",
            x=[NUM_TO_CN_MONTH[n] for n in index],
            y=heal_cum,
            line=dict(shape="spline", smoothing="2", color="#59C3C3"),
        ),
        dict(
            type="scatter",
            mode="markers",
            marker=dict(symbol='star', size=8),
            name="累计疑似病例",
            x=[NUM_TO_CN_MONTH[n] for n in index],
            y=suspect_sum,
            line=dict(shape="spline", smoothing="2", color="#EFC050"),
        ),
    ]
    layout_aggregate["title"] = "各类累计病例"

    figure = dict(data=data, layout=layout_aggregate)
    return figure


# Selectors, main graph -> pie graph
@app.callback(
    Output("pie_graph", "figure"),
    [
        # Input("cache", "children"),
        Input("dcat_selector", "value"),
        Input("countries", "value"),
        Input("month_slider", "value"),
    ],
)
# def make_pie_figure(json_data, dcat, countries, month_slider):
def make_pie_figure(dcat, countries, month_slider):

    layout_pie = copy.deepcopy(layout)
    # alltime_world = pd.read_json(json_data, orient='split')
    # get_dates(alltime_world)
    df_cat = filter_dataframe(alltime_world, countries, month_slider)

    df = filter_dataframe(alltime_world, COUNTRIES, month_slider)
    df = df.groupby('name').sum().sort_values(DCAT_DICT[dcat], ascending=False).reset_index()
    df.loc[df.index >= 5, 'name'] = '其他'
    df = df.groupby('name')[DCAT_DICT[dcat]].sum()

    data = [
        dict(
            type="pie",
            labels=["总确诊", "总死亡", "总治愈", "总疑似"],
            values=[sum(df_cat.today_confirm), sum(df_cat.today_dead),
                    sum(df_cat.today_heal), sum(df_cat.today_suspect)],
            name="数据种类分解",
            text=[
                "总确诊",
                "总死亡",
                "总治愈",
                "总疑似",
            ],
            hoverinfo="text+value+percent",
            textinfo="label+percent+name",
            hole=0.5,
            marker=dict(colors=["#fac1b7", "#a9bb95", "#92d8d8", "#2ECC40"]),
            domain={"x": [0, 0.45], "y": [0.2, 0.8]},
        ),
        dict(
            type="pie",
            labels=list(df.index),
            values=list(df.values),
            name="各国数据分解",
            hoverinfo="label+text+value+percent",
            textinfo="label+percent+name",
            hole=0.5,
            domain={"x": [0.55, 1], "y": [0.2, 0.8]},
        ),
    ]
    layout_pie["title"] = "所选国各类数据比例（左） & 各国所选类数据比例（右）"
    layout_pie["font"] = dict(color="#777777")
    layout_pie["legend"] = dict(
        font=dict(color="#CCCCCC", size="10"), orientation="h", bgcolor="rgba(0,0,0,0)"
    )

    figure = dict(data=data, layout=layout_pie)
    return figure


# Selectors -> count graph
@app.callback(
    Output("count_graph", "figure"),
    [
        # Input("cache", "children"),
        Input("dcat_selector", "value"),
        Input("countries", "value"),
        Input("month_slider", "value"),
    ],
)
# def make_count_figure(json_data, dcat, countries, month_slider):
def make_count_figure(dcat, countries, month_slider):
    layout_count = copy.deepcopy(layout)
    # alltime_world = pd.read_json(json_data, orient='split')
    # get_dates(alltime_world)
    dff = filter_dataframe(alltime_world, countries, month_slider)
    dff = dff.groupby(['month'])[COLUMNS].sum().reset_index()

    colors = []
    for _ in range(month_slider[0], month_slider[1]+1):
        colors.append("rgb(123, 199, 255)")

    data = [
        dict(
            type="scatter",
            mode="markers",
            x=[NUM_TO_CN_MONTH[n] for n in dff.month],
            name="例",
            opacity=0,
            hoverinfo="skip",
        ),
        dict(
            type="bar",
            x=[NUM_TO_CN_MONTH[n] for n in dff.month],
            name="例",
            marker=dict(color=colors),
        ),
    ]

    if dcat == 'confirm':
        data[0]['y'] = dff.today_confirm / 2
        data[1]['y'] = dff.today_confirm
        layout_count['title'] = "各月确诊人数"
    elif dcat == 'dead':
        data[0]['y'] = dff.today_dead / 2
        data[1]['y'] = dff.today_dead
        layout_count['title'] = "各月死亡人数"
    elif dcat == 'heal':
        data[0]['y'] = dff.today_heal / 2
        data[1]['y'] = dff.today_heal
        layout_count['title'] = "各月治愈人数"
    elif dcat == 'suspect':
        data[0]['y'] = dff.today_suspect / 2
        data[1]['y'] = dff.today_suspect
        layout_count['title'] = "各月疑似人数"

    layout_count["dragmode"] = "select"
    layout_count["showlegend"] = False
    layout_count["autosize"] = True

    figure = dict(data=data, layout=layout_count)
    return figure


# Main
if __name__ == "__main__":
    app.run_server(port=80, host='0.0.0.0')
    # app.run_server(debug=True, port=8080)
