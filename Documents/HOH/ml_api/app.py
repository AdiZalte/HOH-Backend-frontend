from flask import Flask, request, jsonify
import pandas as pd
import pickle
import os
import shap
import numpy as np

app = Flask(__name__)

# Model
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

# Explainer
explainer_path = os.path.join(os.path.dirname(__file__), 'shap_explainer.pkl')
try:
    with open(explainer_path, 'rb') as f:
        explainer = pickle.load(f)
    print("SHAP explainer loaded successfully")
except Exception as e:
    print(f"Error loading SHAP explainer file: {e}")
    print("Attempting to re-create explainer from model...")
    try:
        if model:
            # For XGBoost/sklearn models, TreeExplainer is best
            explainer = shap.TreeExplainer(model)
            print("Successfully re-created TreeExplainer")
        else:
            explainer = None
    except Exception as e2:
        print(f"Failed to create SHAP explainer: {e2}")
        explainer = None


@app.route('/predict', methods=['POST'])
def predict():
    if not model:
        return jsonify({'error': 'Model not loaded'}), 500

    try:
        data = request.get_json()
        
        # Extraction
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

        # Features
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

        # Dataframe
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
        
        # Extraction
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

        # Features
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

        # Dataframe
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
        
        # SHAP
        try:
            shap_values_obj = explainer(input_data)
        except Exception as e:
            print(f"Error calling explainer: {e}")
            # Fallback to older API
            shap_values_obj = explainer.shap_values(input_data)
        
        # Extract SHAP values safely
        # Newer SHAP (explainer(data)) returns an Explanation object
        if hasattr(shap_values_obj, 'values'):
            values = shap_values_obj.values
            base_value = shap_values_obj.base_values
            
            # Extract first instance
            if len(values.shape) > 1: values = values[0]
            if isinstance(base_value, (list, np.ndarray)) and len(base_value) > 0: base_value = base_value[0]
            
            # Handle multi-class (list or 3D array)
            if isinstance(values, list) or (hasattr(values, 'shape') and len(values.shape) > 1):
                values = values[1] if len(values) > 1 else values[0]
        else:
            # Older SHAP (explainer.shap_values(data)) returns a list or array
            values = shap_values_obj
            base_value = getattr(explainer, 'expected_value', 0)
            
            if isinstance(values, list):
                # For binary classification, typically returns [neg_values, pos_values]
                values = values[1] if len(values) > 1 else values[0]
            
            if len(values.shape) > 1:
                values = values[0]
                
            if isinstance(base_value, (list, np.ndarray)) and len(base_value) > 0:
                base_value = base_value[1] if len(base_value) > 1 else base_value[0]

        # Convert to list for JSON
        if hasattr(values, 'tolist'): values = values.tolist()
        if hasattr(base_value, 'tolist'): base_value = base_value.tolist()

        # Return
        return jsonify({
            'shap_values': values,
            'feature_names': expected_cols,
            'base_value': float(base_value) if isinstance(base_value, (int, float, np.float32, np.float64)) else base_value,
            'feature_values': input_data.iloc[0].tolist()
        })

    except Exception as e:
        print(f"Explanation error: {e}")
        import traceback
        traceback.print_exc()
        return jsonify({'error': str(e)}), 400

if __name__ == '__main__':
    app.run(port=8000, debug=True)

