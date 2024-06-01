from flask import Flask, render_template
import plotly
import plotly.express as px
import pandas as pd
import json

app = Flask(__name__)

@app.route('/')
def index():
    df = pd.read_csv('path_to_dataset/DAPT_2020.csv')
    fig = px.scatter(df, x='feature1', y='feature2', color='target')
    graphJSON = json.dumps(fig, cls=plotly.utils.PlotlyJSONEncoder)
    
    return render_template('dashboard.html', graphJSON=graphJSON)

if __name__ == "__main__":
    app.run(debug=True)
