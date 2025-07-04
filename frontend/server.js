const express = require('express');
const app = express();
const port = 3000;


app.use(express.static('build'));

app.get('/api/test', (req, res) => {
  res.json({ message: 'This is a test from server.js' });
});

const server = app.listen(port, () => {
  console.log(`Frontend running on http://localhost:${port}`);
});


process.on('SIGTERM', () => {
  console.log('Received SIGTERM. Performing graceful shutdown...');
  server.close(() => {
    console.log('Server closed. Exiting process.');
    process.exit(0);
  });
});