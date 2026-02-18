require("dotenv").config();
const express = require("express");
const cors = require("cors");
const customerRoutes = require("./src/routes/customerRoutes");

const app = express();

// Add request logging
app.use((req, res, next) => {
  console.log(`[${new Date().toISOString()}] ${req.method} ${req.url}`);
  next();
});

app.use(cors());
app.use(express.json());

app.use("/api/customer", customerRoutes);

app.get("/", (req, res) => {
  res.send("Backend is running 🚀");
});

const PORT = 5001;

app.listen(5001, '0.0.0.0', () => console.log("Backend running on 5001"));

process.on('uncaughtException', (err) => {
  console.error('Uncaught Exception:', err);
});

process.on('unhandledRejection', (reason, promise) => {
  console.error('Unhandled Rejection at:', promise, 'reason:', reason);
});
