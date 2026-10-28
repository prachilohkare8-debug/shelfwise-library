const fs = require('fs');
const path = require('path');
const logPath = path.join(__dirname, '..', 'data', 'requests.log');

module.exports = function requestLogger(req, res, next) {
  const started = Date.now();
  res.on('finish', () => {
    const line = `${new Date().toISOString()} ${req.method} ${req.originalUrl} ${res.statusCode} ${Date.now() - started}ms\n`;
    fs.appendFile(logPath, line, (error) => {
      if (error) console.error('Could not write request log:', error.message);
    });
  });
  next();
};
