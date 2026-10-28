const express = require('express');
const path = require('path');
const fs = require('fs');
const requestLogger = require('./middleware/requestLogger');
const errorHandler = require('./middleware/errorHandler');
const booksRouter = require('./routes/books');

const app = express();
const PORT = process.env.PORT || 3000;
const dataDir = path.join(__dirname, 'data');
if (!fs.existsSync(dataDir)) fs.mkdirSync(dataDir, { recursive: true });
if (!fs.existsSync(path.join(dataDir, 'books.json'))) fs.writeFileSync(path.join(dataDir, 'books.json'), '[]\n');

app.set('view engine', 'ejs');
app.set('views', path.join(__dirname, 'views'));
app.use(express.urlencoded({ extended: false, limit: '20kb' }));
app.use(express.json({ limit: '20kb' }));
app.use(express.static(path.join(__dirname, 'public')));
app.use(requestLogger);
app.use((req, res, next) => {
  res.locals.appName = 'Shelfwise';
  res.locals.currentPath = req.path;
  next();
});

app.get('/', (req, res) => res.redirect('/books'));
app.get('/health', (req, res) => res.status(200).json({ status: 'ok', app: 'Shelfwise', timestamp: new Date().toISOString() }));
app.use('/books', booksRouter);
app.use((req, res, next) => {
  const error = new Error('The requested page could not be found.');
  error.status = 404;
  next(error);
});
app.use(errorHandler);

if (require.main === module) {
  app.listen(PORT, () => console.log(`Shelfwise is running on port ${PORT}`));
}
module.exports = app;
