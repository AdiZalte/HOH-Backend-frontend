# 🏥 HOH Backend

This is the backend API for the **HOH** project part of the `HOH-Backend-frontend` repository.

The backend is built using **Node.js + Express** and connects to a **MySQL-compatible database**.  
It also integrates with a Machine Learning service to provide credit risk predictions and explanations.

---

## 📁 Project Structure
```
new_backend/
│
├── src/
│   ├── config/
│   │   └── db.js
│   │
│   ├── controllers/
│   │   └── customerController.js
│   │
│   ├── models/
│   │   └── customerModel.js
│   │
│   └── routes/
│       └── customerRoutes.js
│
├── server.js
├── package.json
├── .gitignore
└── README.md
```
---


## 🛠 Tech Stack

- Node.js
- Express.js
- MySQL2
- Axios
- Dotenv
- Cors
- JWT (jsonwebtoken)
---

## 📦 Installation

### 1. Clone the Repository
```
git clone https://github.com/AdiZalte/HOH-Backend-frontend.git  
cd HOH-Backend-frontend/Documents/HOH/new_backend
```
---

### 2. Install Dependencies
```
npm install
```
---

## ⚙️ Environment Setup

Create a `.env` file inside the `new_backend` folder and add:
```
DB_HOST=localhost  
DB_USER=root  
DB_PASS=your_password  
DB_NAME=your_database_name  
DB_PORT=3306  
```
Modify according to your database configuration.

---

## ▶️ Running the Server
```
npm start
```
Server runs on:
```
http://localhost:5001
```

---

## 📡 API Endpoints

### Base Route

GET /

Response:  
```
Backend is running
```

---

### Get Customer + Risk Score

GET /api/customer/:id

- Fetches customer data from database  
- Sends data to ML service (`/predict`)  
- Returns customer data with risk score  

---

### Get ML Explanation

GET /api/customer/:id/explain

- Fetches customer data  
- Sends data to ML service (`/explain`)  
- Returns explanation for the prediction  

---

## 🤖 ML Service Requirement

The backend expects a Machine Learning service running at:

http://localhost:8000

Required endpoints:

POST /predict  
POST /explain  

The ML service must accept JSON input and return prediction results.

---

## 🗄 Database Requirements

Expected table:

credit_risk

Sample fields used:

- RevolvingUtilizationOfUnsecuredLines  
- age  
- DebtRatio  
- MonthlyIncome  
- NumberOfOpenCreditLinesAndLoans  
- NumberOfTimes90DaysLate  

Ensure these columns exist in your database.

---

## 🔐 Authentication

JWT and Bcrypt packages are installed but authentication routes are not fully implemented yet.

---
