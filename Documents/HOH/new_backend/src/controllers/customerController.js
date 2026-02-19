const Customer = require("../models/customerModel");
const axios = require("axios");

exports.getCustomerAndScore = (req, res) => {
  const { id } = req.params;

  Customer.getCustomerById(id, async (err, result) => {
    if (err) {
      console.error("DB Error:", err);
      return res.status(500).json({ error: "Database error" });
    }

    if (result.length === 0) {
      return res.status(404).json({ msg: "ID not found in TiDB" });
    }

    const customer = result[0];
    let riskScore = "Error calculating score";

    try {
      console.log("Customer-Data-Keys:", Object.keys(customer));

      // Data
      const mlData = {
        RevolvingUtilizationOfUnsecuredLines: Number(customer.RevolvingUtilizationOfUnsecuredLines),
        age: Number(customer.age),
        'NumberOfTime30-59DaysPastDueNotWorse': Number(customer['NumberOfTime30-59DaysPastDueNotWorse']),
        DebtRatio: Number(customer.DebtRatio),
        MonthlyIncome: Number(customer.MonthlyIncome),
        NumberOfOpenCreditLinesAndLoans: Number(customer.NumberOfOpenCreditLinesAndLoans),
        NumberOfTimes90DaysLate: Number(customer.NumberOfTimes90DaysLate),
        NumberRealEstateLoansOrLines: Number(customer.NumberRealEstateLoansOrLines),
        'NumberOfTime60-89DaysPastDueNotWorse': Number(customer['NumberOfTime60-89DaysPastDueNotWorse']),
        NumberOfDependents: Number(customer.NumberOfDependents)
      };

      console.log("Sending-ML-Data:", JSON.stringify(mlData));

      // Prediction
      const mlResponse = await axios.post("http://localhost:8000/predict", mlData);
      riskScore = mlResponse.data.score;
      console.log(`ML Score for ID ${id}:`, riskScore);
    } catch (apiError) {
      console.error("ML API Error Message:", apiError.message);
      riskScore = "ML Service Unavailable";
    }

    res.json({
      customer: customer,
      riskScore: typeof riskScore === 'number' ? riskScore : 0 // Ensure consistent type or handled
    });
  });
};

exports.getAllCustomers = (req, res) => {
  Customer.getAllCustomers((err, results) => {
    if (err) {
      console.error("DB Error:", err);
      return res.status(500).json({ error: "Database error" });
    }
    res.json(results);
  });
};

exports.getCustomerExplanation = (req, res) => {
  const { id } = req.params;

  Customer.getCustomerById(id, async (err, result) => {
    if (err) {
      console.error("DB Error:", err);
      return res.status(500).json({ error: "Database error" });
    }

    if (result.length === 0) {
      return res.status(404).json({ msg: "ID not found in TiDB" });
    }

    const customer = result[0];

    try {
      console.log("Fetching SHAP explanation for customer:", id);

      // Data
      const mlData = {
        RevolvingUtilizationOfUnsecuredLines: Number(customer.RevolvingUtilizationOfUnsecuredLines),
        age: Number(customer.age),
        'NumberOfTime30-59DaysPastDueNotWorse': Number(customer['NumberOfTime30-59DaysPastDueNotWorse']),
        DebtRatio: Number(customer.DebtRatio),
        MonthlyIncome: Number(customer.MonthlyIncome),
        NumberOfOpenCreditLinesAndLoans: Number(customer.NumberOfOpenCreditLinesAndLoans),
        NumberOfTimes90DaysLate: Number(customer.NumberOfTimes90DaysLate),
        NumberRealEstateLoansOrLines: Number(customer.NumberRealEstateLoansOrLines),
        'NumberOfTime60-89DaysPastDueNotWorse': Number(customer['NumberOfTime60-89DaysPastDueNotWorse']),
        NumberOfDependents: Number(customer.NumberOfDependents)
      };

      console.log("Sending-ML-Explain-Data:", JSON.stringify(mlData));

      // Explain
      const mlResponse = await axios.post("http://localhost:8000/explain", mlData);

      res.json({
        explanation: mlResponse.data
      });
    } catch (apiError) {
      console.error("ML API Explanation Error Message:", apiError.message);
      if (apiError.response) {
        console.error("ML API Error Status:", apiError.response.status);
        console.error("ML API Error Data:", JSON.stringify(apiError.response.data));
      }
      res.status(500).json({ error: "ML Explanation Service Unavailable" });
    }
  });
};
