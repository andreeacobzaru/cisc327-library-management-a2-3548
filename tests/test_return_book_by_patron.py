import pytest
from datetime import datetime, timedelta
from services.library_service import (
    return_book_by_patron,
    get_all_books,
    get_book_by_id,
    get_book_by_isbn
)
from .util import (
    mock_borrow_book,
    generate_patron_id_under_borrow_limit,
    add_new_book_for_testing,
    get_nonexistent_book_id,
)

def test_return_book_valid():
    """Test returning a book with valid patron ID and book ID."""
    success, patron_id, book_id = mock_borrow_book(get_all_books())
    if not success:
        pytest.skip("Failed to borrow a book for testing return functionality.")
    success, message = return_book_by_patron(patron_id, book_id) 
    
    assert success == True
    assert "successfully returned" in message.lower()

def test_return_book_not_borrowed():
    """Test returning a book that was not borrowed by the patron."""
    patron_id = generate_patron_id_under_borrow_limit()
    add_book_success, _, book_isbn = add_new_book_for_testing(get_all_books())
    if not add_book_success:
        pytest.skip("Failed to add a book for testing return functionality.")
    book = get_book_by_isbn(book_isbn)
    success, message = return_book_by_patron(patron_id, book['id'])
    
    assert success == False
    assert "not borrowed" in message.lower()

def test_return_book_invalid_patron_id():
    """Test returning a book with invalid patron ID."""
    success, message = return_book_by_patron("abc123", 1) # Invalid patron ID
    
    assert success == False
    assert "invalid patron id" in message.lower()

def test_return_book_nonexistent_book():
    """Test returning a book that does not exist."""
    nonexistent_book_id = get_nonexistent_book_id(get_all_books())
    success, message = return_book_by_patron("123456", nonexistent_book_id)
    assert success == False
    assert "book not found" in message.lower()

def test_return_book_and_update_availability():
    """Test that returning a book increases its available copies."""

    success, patron_id, book_id = mock_borrow_book(get_all_books())
    available_after_borrow = get_book_by_id(book_id)['available_copies']
    success, _ = return_book_by_patron(patron_id, book_id)
    assert success == True
    
    available_after = get_book_by_id(book_id)['available_copies']
    assert available_after_borrow + 1 == available_after
