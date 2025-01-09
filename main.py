# main.py
from dash import Dash, html, dcc, callback, Output, Input, State
import flask
from app.topic_analyzer import TopicAnalyzer
from app.config import Config
from datetime import datetime, timedelta
import plotly.express as px

server = flask.Flask(__name__)
app = Dash(__name__, server=server)

config = Config()
analyzer = TopicAnalyzer()

# Load initial month of data when app starts
analyzer.load_initial_data()

app.layout = html.Div([
    html.H1("Guardian News Topic Analysis"),
    
    html.Div([
        html.Div([
            html.Label("Date Range:"),
            dcc.DatePickerRange(
                id='date-picker',
                min_date_allowed=datetime.now() - timedelta(days=30),
                max_date_allowed=datetime.now(),
                start_date=datetime.now() - timedelta(days=7),
                end_date=datetime.now()
            ),
        ], style={'margin-bottom': '20px'}),
        
        html.Button("Analyze", id="analyze-button", n_clicks=0),
        
        dcc.Loading(
            id="loading",
            children=[html.Div(id="loading-output")],
            type="default",
        ),
    ], style={'margin': '20px'}),
    
    html.Div([
        html.Div(id='topic-overview'),
        dcc.Graph(id='topic-visualization'),
        dcc.Graph(id='hierarchy-visualization'),
        dcc.Graph(id='time-visualization'),
        dcc.Graph(id='document-visualization'),
        dcc.Graph(id='barchart-visualization'),
        dcc.Graph(id='terms-visualization'),
        dcc.Graph(id='probability-visualization'),
        html.Div(id='topics-over-time-info')
    ])
])

@callback(
    [Output('topic-visualization', 'figure'),
     Output('hierarchy-visualization', 'figure'),
     Output('time-visualization', 'figure'),
     Output('document-visualization', 'figure'),
     Output('barchart-visualization', 'figure'),
     Output('terms-visualization', 'figure'),
     Output('probability-visualization', 'figure'),
     Output('topic-overview', 'children'),
     Output('topics-over-time-info', 'children'),
     Output('loading-output', 'children')],
    [Input('analyze-button', 'n_clicks')],
    [State('date-picker', 'start_date'),
     State('date-picker', 'end_date')],
    prevent_initial_call=True
)
def update_analysis(n_clicks, start_date, end_date):
    if n_clicks is None:
        return [{}] * 7 + [None, None, None]
    
    try:
        start_date = datetime.strptime(start_date, '%Y-%m-%d') if start_date else None
        end_date = datetime.strptime(end_date, '%Y-%m-%d') if end_date else None
        
        results = analyzer.run_analysis(start_date, end_date)
        viz = results['visualizations']
        
        topic_info = html.Div([
            html.H3("Topic Analysis Results"),
            html.P(f"Analyzed articles from {start_date.strftime('%Y-%m-%d')} to {end_date.strftime('%Y-%m-%d')}"),
            html.Div([
                html.H4("Top Topics:"),
                html.Ul([
                    html.Li(f"Topic {topic}: {name}")
                    for topic, name in results['model'].get_topic_info().head().iterrows()
                ])
            ])
        ])
        
        temporal_info = html.Div([
            html.H3("Temporal Analysis"),
            html.P("Topic evolution over time...")
        ])
        
        return (
            viz['topic_viz'],
            viz['hierarchy_viz'],
            viz['time_viz'],
            viz['doc_viz'],
            viz['barchart_viz'],
            viz['terms_viz'],
            viz['prob_viz'],
            topic_info,
            temporal_info,
            "Analysis Complete!"
        )
    
    except Exception as e:
        return [{}] * 7 + [
            html.Div(f"Error: {str(e)}", style={'color': 'red'}),
            None,
            "Analysis Failed!"
        ]

if __name__ == '__main__':
    app.run_server(debug=True)
