import pandas as pd
import dash
import dash_core_components as dcc
import dash_html_components as html
import dash_table
import pandas as pd
import plotly.graph_objs as go
from dash.dependencies import Input, Output, State
from sqlalchemy import create_engine

cnx = create_engine('mysql+pymysql://root:1234@localhost/rem')    
auto = pd.read_sql('SELECT * FROM auto_imports_ujian', cnx) 
auto_plot = auto.copy()

external_stylesheets = ['https://codepen.io/chriddyp/pen/bWLwgP.css']
app = dash.Dash(__name__, external_stylesheets=external_stylesheets)


def generate_table(dataframe, page_size=10):
    return dash_table.DataTable(
        id= 'dataTable',
        columns=[{'name': i ,'id' : i} for i in dataframe.columns],
        data = dataframe.to_dict('records'),
        page_action ='native',
        page_current = 0,
        page_size=page_size,
        style_table = {'overflowX': 'scroll'}
    )

app.layout = html.Div([
    html.H1('Ujian Modul 2 Dashboard Auto Imports'),
    html.P('Created by : Celine Kurniajaya'),
    html.Div([
        html.Div(children=[
            dcc.Tabs(value='tabs', id='tabs-1', children=[
                dcc.Tab(value='Tabel', label='DataFrame Table', children=[
                    html.Center(html.H1('DATAFRAME AUTO IMPORTS')),
                    html.Div(children=[
                                html.Div([
                                    html.P('Fuel-Type'),
                                    dcc.Dropdown(value='',
                                                 id='filter-fuel',
                                                 options=[{'label': i,'value': i} for i in auto_plot['Fuel-Type'].unique()])
                                ],
                                         className='col-3')
                            ],
                                     className='row'),
                            html.Br(),
                            html.Div([
                                html.P('Max Rows:'),
                                dcc.Input(id ='filter-row',
                                          type = 'number', 
                                          value = 10)
                            ], className = 'row col-3'),
                            html.Div(children =[
                                    html.Button('search',id = 'filter')
                             ],className = 'row col-4'),
                            html.Div(id='div-table',
                                     children=[generate_table(auto_plot)])
                ]),
                dcc.Tab(label='Bar-Chart', value='tab-2',children=[
                    html.Div(children=[
                        html.Div(children=[
                            html.P('Y1:'),
                            dcc.Dropdown(id='y-axis-1', options=[{'label':i,'value':i} for i in auto_plot.select_dtypes('number').columns],
                            value='Wheel-Base')
                        ], className='col-4'),
                        html.Div(children=[
                            html.P('Y2:'),
                            dcc.Dropdown(id='y-axis-2', options=[{'label':i,'value':i} for i in auto_plot.select_dtypes('number').columns],
                            value='Height')
                        ], className='col-4'),
                        html.Div(children=[
                            html.P('X:'),
                            dcc.Dropdown(id='x-axis-1', options=[{'label': 'Drive-Wheels', 'value': 'Drive-Wheels'},
                                    {'label': 'Engine-Location', 'value': 'Engine-Location'},
                                    {'label': 'Engine-Type', 'value': 'Engine-Type'}],
                            value='Drive-Wheels')
                        ], className='col-4'),
                        
                        html.Div([
                            dcc.Graph(
                                id='graph-bar',
                                figure= {
                                    'data' : [
                                        {'x' : auto_plot['Drive-Wheels'], 'y' : auto_plot['Wheel-Base'], 'type' : 'bar', 'name': 'Wheel-Base'},
                                        {'x' : auto_plot['Drive-Wheels'], 'y' : auto_plot['Height'], 'type' : 'bar', 'name': 'Height'}
                                    ],
                                    'layout' : {'title' : 'Bar Chart'}
                                }
                            )
                        ])
                    ]),
            ]),
            dcc.Tab(label='Scatter-Chart', value='tab-3', children=[
                    html.Div(children= dcc.Graph(
                        id='graph-scatter',
                        figure={'data' : [
                            go.Scatter(
                                text=auto_plot[auto_plot['Drive-Wheels'] == i ]['Make'],
                                x = auto_plot[auto_plot['Drive-Wheels'] == i ]['Horsepower'],
                                y = auto_plot[auto_plot['Drive-Wheels'] == i ]['Price'],
                                mode='markers',
                                name='{}'.format(i)
                            ) for i in auto_plot['Drive-Wheels'].unique()
                        ],
                        'layout' : go.Layout(
                            xaxis={'title' : 'Horsepower'},
                            yaxis={'title' : 'Price'},
                            hovermode='closest'
                        )
                        }
                    ))
                ]),
            dcc.Tab(label = 'Pie-Chart', value='tab-4', children=[
                html.Div(dcc.Dropdown(id='pie-dropdown', options=[{'label':i,'value':i} for i in auto_plot.select_dtypes('number').columns],value='Length'),
                className='col-4'),
                html.Div([
                    dcc.Graph(
                        id='graph-pie',
                        figure={
                            'data': [
                                go.Pie(labels=['{}'.format(i) for i in list(auto_plot['Fuel-Type'].unique())],
                                values=[auto_plot.groupby('Fuel-Type').mean()['Price'][i] for i in list(auto_plot['Fuel-Type'].unique())],
                                sort= False
                                )
                            ],
                            'layout' : {'title' : 'Mean Pie Chart'}
                        }
                    )
                ])
            ])
            ])
        ])
    ])
])

# Bar chart
@app.callback(
    Output(component_id='graph-bar', component_property='figure'),
    [Input(component_id='y-axis-1', component_property='value'),
    Input(component_id='y-axis-2', component_property='value'),
    Input(component_id='x-axis-1', component_property='value')]
)

def create_graph_bar(y1,y2,x1):
    figure = {
        'data' : [
            {'x' : auto_plot[x1], 'y' : auto_plot[y1], 'type' : 'bar', 'name' : y1},
            {'x' : auto_plot[x1], 'y' : auto_plot[y2], 'type' : 'bar', 'name' : y2}
        ],
        'layout' : {'title' : 'Bar Chart'}
    }
    return figure

# Pie Chart
@app.callback(
    Output(component_id='graph-pie', component_property='figure'),
    [Input(component_id='pie-dropdown', component_property='value')]
)

def create_graph_pie(columns):
    figure = {
        'data' : [
            go.Pie(labels=['{}'.format(i) for i in list(auto_plot['Fuel-System'].unique())],
            values=[auto_plot.groupby('Fuel-System').mean()[columns][i] for i in list(auto_plot['Fuel-System'].unique())],
            sort= False
            )
        ],
        'layout' : {'title' : 'Mean Pie Chart'}
    }
    return figure

@app.callback(
    Output(component_id = 'div-table', component_property = 'children'),
    [Input(component_id = 'filter', component_property = 'n_clicks')],
    [State(component_id = 'filter-row', component_property = 'value'),
    State(component_id = 'filter-fuel', component_property = 'value')
    ])

def update_table(n_clicks, row, fuel):
    if fuel == '':
        children = [generate_table(auto_plot, page_size = row)]
    else:
        children = [generate_table(auto_plot[auto_plot['Fuel-Type'] == fuel], page_size = row)]            
    return children


if __name__ == '__main__':
    app.run_server(debug=True)