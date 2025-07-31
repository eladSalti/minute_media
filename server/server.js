const express = require('express');
const bodyParser = require('body-parser');
const path = require('path');

const app = express();
app.use(bodyParser.json());

app.use(express.static(path.join(__dirname, '../client')));

app.post('/api/event', (req, res) => {
  console.log('📩 Event received:', req.body);
  res.status(200).send({ ok: true });
});

const PORT = process.env.PORT || 3000;
app.listen(PORT, () => {
  console.log(`📺 Server is running at http://localhost:${PORT}`);
});
