from dash import Dash, html, dcc, callback, Output, Input
import flask
from app.topic_analyzer import TopicAnalyzer
from app.config import Config
import plotly.express as px

server = flask.Flask(__name__)
app = Dash(__name__, server=server)

config = Config()
analyzer = TopicAnalyzer()

app.layout = html.Div([
    html.H1("Guardian News Topic Analysis"),
    
    html.Div([
        html.Button("Fetch and Analyze", id="analyze-button"),
        dcc.Loading(
            id="loading",
            children=[html.Div(id="loading-output")],
            type="default",
        ),
    ]),
    
    html.Div([
        html.Div(id='topic-overview'),
        dcc.Graph(id='topic-visualization'),
        dcc.Graph(id='hierarchy-visualization'),
        dcc.Graph(id='time-visualization'),
        dcc.Graph(id='document-visualization')
    ])
])

@callback(
    [Output('topic-visualization', 'figure'),
     Output('hierarchy-visualization', 'figure'),
     Output('time-visualization', 'figure'),
     Output('document-visualization', 'figure'),
     Output('topic-overview', 'children'),
     Output('loading-output', 'children')],
    Input('analyze-button', 'n_clicks'),
    prevent_initial_call=True
)
def update_graphs(n_clicks):
    if n_clicks is None:
        return [{}] * 4 + [None, None]
    
    # Fetch and analyze
    results = analyzer.run_analysis()
    
    return (
        results['topic_viz'],
        results['hierarchy_viz'],
        results['time_viz'],
        results['doc_viz'],
        html.Div([
            html.H3("Top Topics Found:"),
            html.Ul([
                html.Li(f"Topic {topic}: {name} (Count: {count})")
                for topic, name, count in results['top_topics']
            ])
        ]),
        "Analysis Complete!"
    )

if __name__ == '__main__':
    app.run_server(debug=True)
