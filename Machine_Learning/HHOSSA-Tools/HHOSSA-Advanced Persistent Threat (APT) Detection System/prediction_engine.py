import pickle
from flask import Flask, request, jsonify

app = Flask(__name__)

# Load the trained model (example with Light GBM)
model = pickle.load(open('lightgbm_model.pkl', 'rb'))

@app.route('/predict', methods=['POST'])
def predict():
    data = request.json
    features = [data[key] for key in data]
    prediction = model.predict([features])
    return jsonify({"prediction": int(prediction[0])})

if __name__ == "__main__":
    app.run(debug=True)
