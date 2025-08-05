|
const express = require('express');
const app = express();
const port = 3000;

app.get('/oauth', (req, res) => {
res.send('OAuth endpoint');
});

app.listen(port, () => {
console.log(`App listening at http://localhost:${port}`);
});