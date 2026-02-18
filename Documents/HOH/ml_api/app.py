from flask import Flask, request, jsonify
import pandas as pd
import pickle
import os
import shap

app = Flask(__name__)

# Load the model
model_path = os.path.join(os.path.dirname(__file__), 'credit_risk_model.pkl')
try:
    with open(model_path, 'rb') as f:
        model = pickle.load(f)
    print("Model loaded successfully")
    try:
        if hasattr(model, 'feature_names_in_'):
            print(f"Expected Features: {model.feature_names_in_}")
        elif hasattr(model, 'get_booster'):
             print(f"Expected Features: {model.get_booster().feature_names}")
    except Exception as e:
        print(f"Could not read feature names: {e}")
except Exception as e:
    print(f"Error loading model: {e}")
    model = None

# Load the SHAP explainer
explainer_path = os.path.join(os.path.dirname(__file__), 'shap_explainer.pkl')
try:
    with open(explainer_path, 'rb') as f:
        explainer = pickle.load(f)
    print("SHAP explainer loaded successfully")
except Exception as e:
    print(f"Error loading SHAP explainer: {e}")
    explainer = None


@app.route('/predict', methods=['POST'])
def predict():
    if not model:
        return jsonify({'error': 'Model not loaded'}), 500

    try:
        data = request.get_json()
        
        # 1. Basic Extraction
        revol = data.get('RevolvingUtilizationOfUnsecuredLines', 0)
        age = data.get('age', 0)
        num30 = data.get('NumberOfTime30-59DaysPastDueNotWorse', 0)
        debt_ratio = data.get('DebtRatio', 0)
        income = data.get('MonthlyIncome', 0)
        num_open = data.get('NumberOfOpenCreditLinesAndLoans', 0)
        num90 = data.get('NumberOfTimes90DaysLate', 0)
        num_real_estate = data.get('NumberRealEstateLoansOrLines', 0)
        num60 = data.get('NumberOfTime60-89DaysPastDueNotWorse', 0)
        dependents = data.get('NumberOfDependents', 0)

        # 2. Feature Engineering
        # TotalPastDue
        total_past_due = num30 + num60 + num90
        
        # DebtIncomeRatio (Seems to be a rename or just DebtRatio)
        debt_income_ratio = debt_ratio
        
        # AnySeriousLate (Flag if 90 days late happened)
        any_serious_late = 1 if num90 > 0 else 0
        
        # AgeGroup (Simple binning: 1 for <20, 2 for 20s, 3 for 30s, etc.)
        def get_age_group(a):
            if a < 21: return 1
            elif a < 30: return 2
            elif a < 40: return 3
            elif a < 50: return 4
            elif a < 60: return 5
            elif a < 70: return 6
            elif a < 80: return 7
            else: return 8
            
        age_group = get_age_group(age)

        # 3. Create DataFrame with ALL features in correct order
        # Order derived from logs: 
        # ['RevolvingUtilizationOfUnsecuredLines', 'age', 'NumberOfTime30-59DaysPastDueNotWorse', 'DebtRatio', 'MonthlyIncome', 
        #  'NumberOfOpenCreditLinesAndLoans', 'NumberOfTimes90DaysLate', 'NumberRealEstateLoansOrLines', 
        #  'NumberOfTime60-89DaysPastDueNotWorse', 'NumberOfDependents', 'TotalPastDue', 'DebtIncomeRatio', 'AnySeriousLate', 'AgeGroup']
        
        features_dict = {
            'RevolvingUtilizationOfUnsecuredLines': revol,
            'age': age,
            'NumberOfTime30-59DaysPastDueNotWorse': num30,
            'DebtRatio': debt_ratio,
            'MonthlyIncome': income,
            'NumberOfOpenCreditLinesAndLoans': num_open,
            'NumberOfTimes90DaysLate': num90,
            'NumberRealEstateLoansOrLines': num_real_estate,
            'NumberOfTime60-89DaysPastDueNotWorse': num60,
            'NumberOfDependents': dependents,
            'TotalPastDue': total_past_due,
            'DebtIncomeRatio': debt_income_ratio,
            'AnySeriousLate': any_serious_late,
            'AgeGroup': age_group
        }

        input_data = pd.DataFrame([features_dict])
        
        # Ensure column order matches model expectation (Critical for XGBoost/sklearn pipelines)
        expected_cols = [
            'RevolvingUtilizationOfUnsecuredLines', 'age', 'NumberOfTime30-59DaysPastDueNotWorse', 'DebtRatio', 'MonthlyIncome',
            'NumberOfOpenCreditLinesAndLoans', 'NumberOfTimes90DaysLate', 'NumberRealEstateLoansOrLines',
            'NumberOfTime60-89DaysPastDueNotWorse', 'NumberOfDependents', 'TotalPastDue', 'DebtIncomeRatio', 'AnySeriousLate', 'AgeGroup'
        ]
        input_data = input_data[expected_cols]
        
        # Handle missing values
        input_data = input_data.fillna(0)
        
        # Predict
        try:
            prediction = model.predict_proba(input_data)[:, 1][0]
        except AttributeError:
            prediction = float(model.predict(input_data)[0])

        return jsonify({'score': float(prediction)})

    except Exception as e:
        print(f"Prediction error: {e}")
        return jsonify({'error': str(e)}), 400

@app.route('/explain', methods=['POST'])
def explain():
    if not model:
        return jsonify({'error': 'Model not loaded'}), 500
    
    if not explainer:
        return jsonify({'error': 'SHAP explainer not loaded'}), 500

    try:
        data = request.get_json()
        
        # 1. Basic Extraction (same as predict)
        revol = data.get('RevolvingUtilizationOfUnsecuredLines', 0)
        age = data.get('age', 0)
        num30 = data.get('NumberOfTime30-59DaysPastDueNotWorse', 0)
        debt_ratio = data.get('DebtRatio', 0)
        income = data.get('MonthlyIncome', 0)
        num_open = data.get('NumberOfOpenCreditLinesAndLoans', 0)
        num90 = data.get('NumberOfTimes90DaysLate', 0)
        num_real_estate = data.get('NumberRealEstateLoansOrLines', 0)
        num60 = data.get('NumberOfTime60-89DaysPastDueNotWorse', 0)
        dependents = data.get('NumberOfDependents', 0)

        # 2. Feature Engineering (same as predict)
        total_past_due = num30 + num60 + num90
        debt_income_ratio = debt_ratio
        any_serious_late = 1 if num90 > 0 else 0
        
        def get_age_group(a):
            if a < 21: return 1
            elif a < 30: return 2
            elif a < 40: return 3
            elif a < 50: return 4
            elif a < 60: return 5
            elif a < 70: return 6
            elif a < 80: return 7
            else: return 8
            
        age_group = get_age_group(age)

        # 3. Create DataFrame with ALL features in correct order
        features_dict = {
            'RevolvingUtilizationOfUnsecuredLines': revol,
            'age': age,
            'NumberOfTime30-59DaysPastDueNotWorse': num30,
            'DebtRatio': debt_ratio,
            'MonthlyIncome': income,
            'NumberOfOpenCreditLinesAndLoans': num_open,
            'NumberOfTimes90DaysLate': num90,
            'NumberRealEstateLoansOrLines': num_real_estate,
            'NumberOfTime60-89DaysPastDueNotWorse': num60,
            'NumberOfDependents': dependents,
            'TotalPastDue': total_past_due,
            'DebtIncomeRatio': debt_income_ratio,
            'AnySeriousLate': any_serious_late,
            'AgeGroup': age_group
        }

        input_data = pd.DataFrame([features_dict])
        
        # Ensure column order matches model expectation
        expected_cols = [
            'RevolvingUtilizationOfUnsecuredLines', 'age', 'NumberOfTime30-59DaysPastDueNotWorse', 'DebtRatio', 'MonthlyIncome',
            'NumberOfOpenCreditLinesAndLoans', 'NumberOfTimes90DaysLate', 'NumberRealEstateLoansOrLines',
            'NumberOfTime60-89DaysPastDueNotWorse', 'NumberOfDependents', 'TotalPastDue', 'DebtIncomeRatio', 'AnySeriousLate', 'AgeGroup'
        ]
        input_data = input_data[expected_cols]
        
        # Handle missing values
        input_data = input_data.fillna(0)
        
        # Generate SHAP values
        shap_values = explainer(input_data)
        
        # Extract SHAP values for the first (and only) instance
        # SHAP values structure depends on explainer type
        if hasattr(shap_values, 'values'):
            # For newer SHAP versions (Explanation object)
            values = shap_values.values[0].tolist()
            base_value = shap_values.base_values[0] if hasattr(shap_values, 'base_values') else 0
        else:
            # For older SHAP versions (numpy array)
            values = shap_values[0].tolist()
            base_value = explainer.expected_value if hasattr(explainer, 'expected_value') else 0

        # Return SHAP explanation
        return jsonify({
            'shap_values': values,
            'feature_names': expected_cols,
            'base_value': float(base_value),
            'feature_values': input_data.iloc[0].tolist()
        })

    except Exception as e:
        print(f"Explanation error: {e}")
        import traceback
        traceback.print_exc()
        return jsonify({'error': str(e)}), 400

if __name__ == '__main__':
    app.run(port=8000, debug=True)

