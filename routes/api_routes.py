"""
API Routes - JSON API endpoints
"""

from flask import Blueprint, jsonify, request
from services.library_service import calculate_late_fee_for_book, search_books_in_catalog
from database import get_book_by_id

api_bp = Blueprint('api', __name__, url_prefix='/api')

@api_bp.route('/late_fee/<patron_id>/<int:book_id>')
def get_late_fee(patron_id, book_id):
    """
    Calculate late fee for a specific book borrowed by a patron.
    API endpoint for R5: Late Fee Calculation
    """
    result = calculate_late_fee_for_book(patron_id, book_id)
    return jsonify(result), 501 if 'not implemented' in result.get('status', '') else 200

@api_bp.route('/search')
def search_books_api():
    """
    Search for books via API endpoint.
    Alternative API interface for R5: Book Search Functionality
    """
    search_term = request.args.get('q', '').strip()
    search_type = request.args.get('type', 'title')
    
    if not search_term:
        return jsonify({'error': 'Search term is required'}), 400
    
    # Use business logic function
    books = search_books_in_catalog(search_term, search_type)
    
    return jsonify({
        'search_term': search_term,
        'search_type': search_type,
        'results': books,
        'count': len(books)
    })

@api_bp.route('/book/<int:book_id>', methods=['GET'])
def get_book_details(book_id):
    """
    Calls the database function get_book_by_id directly
    and returns the result as JSON in the browser.
    """
    
    # --- 1. CALL THE DATABASE FUNCTION HERE ---
    book_data = get_book_by_id(book_id)
    # --- --------------------------------- ---
    
    if book_data:
        # Flask's jsonify converts the Python dictionary result into a JSON response
        return jsonify({
            "status": "success",
            "data": book_data
        }), 200
    else:
        return jsonify({
            "status": "error",
            "message": f"Book with ID {book_id} not found."
        }), 404