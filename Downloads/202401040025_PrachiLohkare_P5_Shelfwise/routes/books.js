const express = require('express');
const fs = require('fs');
const path = require('path');
const { body, param, validationResult } = require('express-validator');
const router = express.Router();
const dataFile = path.join(__dirname, '..', 'data', 'books.json');

function readBooks() { return JSON.parse(fs.readFileSync(dataFile, 'utf8')); }
function writeBooks(books) { fs.writeFileSync(dataFile, JSON.stringify(books, null, 2) + '\n'); }
function makeId(books) {
  const largest = books.reduce((max, book) => Math.max(max, Number(book.id.split('-')[1]) || 1000), 1000);
  return `BK-${largest + 1}`;
}
function formErrors(req) {
  return validationResult(req).array().map((item) => item.msg);
}
const bookRules = [
  body('title').trim().isLength({ min: 2, max: 100 }).withMessage('Title must be between 2 and 100 characters.'),
  body('author').trim().isLength({ min: 2, max: 80 }).withMessage('Author must be between 2 and 80 characters.'),
  body('category').isIn(['Fiction', 'Technology', 'Design', 'Personal Growth', 'Science', 'History', 'Other']).withMessage('Choose a category from the list.'),
  body('isbn').trim().matches(/^[0-9Xx-]{10,17}$/).withMessage('Enter a valid ISBN (10–17 digits/characters, hyphens allowed).'),
  body('copies').isInt({ min: 1, max: 500 }).withMessage('Total copies must be between 1 and 500.'),
  body('available').isInt({ min: 0, max: 500 }).withMessage('Available copies must be 0–500.')
    .custom((value, { req }) => Number(value) <= Number(req.body.copies)).withMessage('Available copies cannot exceed total copies.'),
  body('shelf').trim().matches(/^[A-Za-z]-\d{2}$/).withMessage('Shelf must look like T-04 or F-02.')
];

router.get('/', (req, res, next) => {
  try {
    const books = readBooks();
    const q = (req.query.q || '').trim().toLowerCase();
    const category = req.query.category || 'All categories';
    const filtered = books.filter((book) => {
      const matchesText = !q || [book.title, book.author, book.isbn, book.id].some((value) => value.toLowerCase().includes(q));
      const matchesCategory = category === 'All categories' || book.category === category;
      return matchesText && matchesCategory;
    });
    res.render('books/index', {
      title: 'Library inventory', books: filtered, allBooks: books, q, category,
      categories: ['All categories', 'Fiction', 'Technology', 'Design', 'Personal Growth', 'Science', 'History', 'Other'],
      currentPath: '/books', notice: req.query.notice || '', errors: []
    });
  } catch (error) { next(error); }
});

router.get('/new', (req, res) => res.render('books/form', {
  title: 'Add a book', heading: 'Add a book', submitLabel: 'Add to inventory',
  book: { title: '', author: '', category: 'Fiction', isbn: '', copies: 1, available: 1, shelf: 'F-01' },
  errors: [], currentPath: '/books', isEdit: false
}));

router.post('/', bookRules, (req, res, next) => {
  const errors = formErrors(req);
  const book = { ...req.body, copies: Number(req.body.copies), available: Number(req.body.available) };
  if (errors.length) return res.status(422).render('books/form', {
    title: 'Add a book', heading: 'Add a book', submitLabel: 'Add to inventory', book, errors,
    currentPath: '/books', isEdit: false
  });
  try {
    const books = readBooks();
    if (books.some((item) => item.isbn.replace(/-/g, '') === book.isbn.replace(/-/g, ''))) {
      return res.status(422).render('books/form', { title: 'Add a book', heading: 'Add a book', submitLabel: 'Add to inventory', book, errors: ['A book with this ISBN already exists.'], currentPath: '/books', isEdit: false });
    }
    books.unshift({ id: makeId(books), ...book, addedAt: new Date().toISOString().slice(0, 10) });
    writeBooks(books);
    res.redirect('/books?notice=Book%20added%20to%20inventory');
  } catch (error) { next(error); }
});

router.get('/:id', param('id').matches(/^BK-\d{4,}$/).withMessage('Invalid book ID.'), (req, res, next) => {
  const errors = formErrors(req);
  if (errors.length) return res.status(400).render('error', { title: 'Invalid book ID', status: 400, message: errors[0], currentPath: '/books' });
  try {
    const book = readBooks().find((item) => item.id === req.params.id);
    if (!book) return res.status(404).render('error', { title: 'Book not found', status: 404, message: 'This book is not in the inventory.', currentPath: '/books' });
    res.render('books/detail', { title: book.title, book, currentPath: '/books' });
  } catch (error) { next(error); }
});

router.get('/:id/edit', param('id').matches(/^BK-\d{4,}$/).withMessage('Invalid book ID.'), (req, res, next) => {
  if (formErrors(req).length) return res.status(400).render('error', { title: 'Invalid book ID', status: 400, message: 'The book ID format is invalid.', currentPath: '/books' });
  try {
    const book = readBooks().find((item) => item.id === req.params.id);
    if (!book) return res.status(404).render('error', { title: 'Book not found', status: 404, message: 'This book is not in the inventory.', currentPath: '/books' });
    res.render('books/form', { title: 'Edit book', heading: 'Edit book', submitLabel: 'Save changes', book, errors: [], currentPath: '/books', isEdit: true });
  } catch (error) { next(error); }
});

router.post('/:id/edit', param('id').matches(/^BK-\d{4,}$/).withMessage('Invalid book ID.'), bookRules, (req, res, next) => {
  const errors = formErrors(req);
  const book = { ...req.body, id: req.params.id, copies: Number(req.body.copies), available: Number(req.body.available) };
  if (errors.length) return res.status(422).render('books/form', { title: 'Edit book', heading: 'Edit book', submitLabel: 'Save changes', book, errors, currentPath: '/books', isEdit: true });
  try {
    const books = readBooks();
    const index = books.findIndex((item) => item.id === req.params.id);
    if (index === -1) return res.status(404).render('error', { title: 'Book not found', status: 404, message: 'This book is not in the inventory.', currentPath: '/books' });
    const duplicate = books.some((item) => item.id !== req.params.id && item.isbn.replace(/-/g, '') === book.isbn.replace(/-/g, ''));
    if (duplicate) return res.status(422).render('books/form', { title: 'Edit book', heading: 'Edit book', submitLabel: 'Save changes', book, errors: ['Another book already uses this ISBN.'], currentPath: '/books', isEdit: true });
    books[index] = { ...books[index], ...book };
    writeBooks(books);
    res.redirect(`/books/${req.params.id}?notice=Changes%20saved`);
  } catch (error) { next(error); }
});

router.post('/:id/delete', param('id').matches(/^BK-\d{4,}$/).withMessage('Invalid book ID.'), (req, res, next) => {
  if (formErrors(req).length) return res.status(400).render('error', { title: 'Invalid book ID', status: 400, message: 'The book ID format is invalid.', currentPath: '/books' });
  try {
    const books = readBooks();
    const remaining = books.filter((book) => book.id !== req.params.id);
    if (remaining.length === books.length) return res.status(404).render('error', { title: 'Book not found', status: 404, message: 'This book is not in the inventory.', currentPath: '/books' });
    writeBooks(remaining);
    res.redirect('/books?notice=Book%20removed%20from%20inventory');
  } catch (error) { next(error); }
});

module.exports = router;
