const express = require("express");
const router = express.Router();
const { getCustomerAndScore, getAllCustomers, getCustomerExplanation } = require("../controllers/customerController");

router.get("/", getAllCustomers);
router.get("/:id/explain", getCustomerExplanation);
router.get("/:id", getCustomerAndScore);

module.exports = router;
