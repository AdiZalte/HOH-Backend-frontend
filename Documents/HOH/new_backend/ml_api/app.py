from flask import Flask, request, jsonify
import pickle

# try error field
try:
    model = pickle.load(open("credit_model.pkl", "rb"))
except FileNotFoundError:
    print("WARNING: credit_model.pkl not found. Using dummy predictor.")
    model = None

app = Flask(__name__)

@app.route("/predict", methods=["POST"])
def predict():
    data = request.json
    
    if model:
        features = [[
            data["RevolvingUtilizationOfUnsecuredLines"],
            data["age"],
            data["DebtRatio"],
            data["MonthlyIncome"]
        ]]
        score = model.predict_proba(features)[0][1]
    else:
        # Dummy prediction logic (return random score between 0 and 1)
        import random
        score = random.random()

    return jsonify({"score": float(score)})

if __name__ == "__main__":
    app.run(port=8000)
