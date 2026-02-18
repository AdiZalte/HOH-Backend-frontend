const db = require("../config/db");

exports.getCustomerById = (id, callback) => {
  const sql = "SELECT id, RevolvingUtilizationOfUnsecuredLines, age, `NumberOfTime30-59DaysPastDueNotWorse`, DebtRatio, MonthlyIncome, NumberOfOpenCreditLinesAndLoans, NumberOfTimes90DaysLate, NumberRealEstateLoansOrLines, `NumberOfTime60-89DaysPastDueNotWorse`, NumberOfDependents FROM credit_risk WHERE id = ?";
  db.query(sql, [id], (err, results) => {
    callback(err, results);
  });
};

exports.getAllCustomers = (callback) => {
  const sql = "SELECT id, RevolvingUtilizationOfUnsecuredLines, age, `NumberOfTime30-59DaysPastDueNotWorse`, DebtRatio, MonthlyIncome, NumberOfOpenCreditLinesAndLoans, NumberOfTimes90DaysLate, NumberRealEstateLoansOrLines, `NumberOfTime60-89DaysPastDueNotWorse`, NumberOfDependents FROM credit_risk LIMIT 10";
  db.query(sql, (err, results) => {
    callback(err, results);
  });
};
