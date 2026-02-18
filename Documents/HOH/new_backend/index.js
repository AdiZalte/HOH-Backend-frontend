const express = require("express");
const mysql = require("mysql2");
const cors = require("cors");

const app = express();
app.use(cors());
app.use(express.json());

// 🔹 TiDB Connection
const db = mysql.createConnection({
  host: "gateway01.ap-southeast-1.prod.aws.tidbcloud.com",
  user: "35aX1bhXkL1teZU.root",
  password: "orwwy1SfYdiHfHwJ",
  database: "Customer_Bank_Details",
  port: 4000,
  ssl: { rejectUnauthorized: true }
});

// 🔹 Test Connection
db.connect(err => {
  if (err) {
    console.log("❌ DB Connection Failed:", err);
  } else {
    console.log("✅ Connected to TiDB");
  }
});

// 🔹 API Route
app.get("/user/:id", (req, res) => {
  const id = req.params.id;

  const sql = "SELECT * FROM credit_risk WHERE id = ?";
  
  db.query(sql, [id], (err, result) => {
    if (err) {
      console.log(err);
      return res.status(500).json(err);
    }

    if (result.length === 0) {
      return res.status(404).json({ message: "User not found" });
    }

    res.json(result[0]);
  });
});

app.listen(5000, () => {
  console.log("🚀 Server running on port 5000");
});
