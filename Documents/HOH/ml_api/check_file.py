import os

path = r'C:\Users\DELL\Documents\HOH\credit_risk_model.pkl'
print(f"Path: {path}")
print(f"Exists: {os.path.exists(path)}")
print(f"Is File: {os.path.isfile(path)}")
try:
    with open(path, 'rb') as f:
        print("File is readable")
except Exception as e:
    print(f"Read error: {e}")
