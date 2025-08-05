|
// Security middleware implementation
const express = require('express');
const helmet = require('helmet');

const router = express.Router();

router.use(helmet());

module.exports = router;