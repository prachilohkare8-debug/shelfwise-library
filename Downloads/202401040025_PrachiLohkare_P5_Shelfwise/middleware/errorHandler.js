module.exports = function errorHandler(err, req, res, next) {
  console.error(err.stack || err);
  const status = err.status || 500;
  if (req.accepts('html')) {
    return res.status(status).render('error', {
      title: status === 404 ? 'Page not found' : 'Something went wrong',
      status,
      message: status === 404 ? 'We could not find that page or book.' : (status < 500 ? err.message : 'The request could not be completed. Please try again.'),
      currentPath: req.path
    });
  }
  res.status(status).json({ error: status === 404 ? 'Not found' : 'Request failed', message: err.message });
};
