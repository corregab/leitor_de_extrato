# Changelog

All notable changes to this project will be documented in this file.

## [Unreleased]

### Added
- Complete HTML template refactoring with clean, modern design
- Loading indicators during file processing
- File counter display when multiple files are selected
- Print-friendly CSS for results page
- Real-time search functionality in results
- Custom 404 and 500 error pages with beautiful design
- Health check endpoint (`/health`) for monitoring
- Robots.txt for better SEO
- Comprehensive security headers (HSTS, X-Frame-Options, CSP, etc.)
- File validation preventing path traversal attacks
- Maximum file count limit (10 files per upload)
- Enhanced meta tags for better SEO
- Custom CSS file with accessibility improvements
- Comprehensive README at root level
- Updated WEBAPP documentation

### Changed
- Improved mobile responsiveness across all pages
- Enhanced error handling with user-friendly messages
- Better logging for debugging in production
- Optimized render.yaml configuration
- Updated Gunicorn configuration for better performance

### Security
- Robust file validation preventing security vulnerabilities
- Safe error messages hiding sensitive information in production
- Automatic cleanup of temporary uploaded files
- File size enforcement (16 MB per file)
- Path traversal protection in filename handling

### Fixed
- Corrupted HTML templates with duplicate content
- UTF-8 encoding issues
- Duplicate CSS and JavaScript in templates

## [Previous] - Historical

### Features
- Initial Flask web application
- Support for multiple banks (Itaú, Santander, Nubank, PicPay, Mercado Pago)
- PDF extraction using pdfplumber
- Transaction filtering by name
- Multiple file upload support
- Results table with copy functionality
