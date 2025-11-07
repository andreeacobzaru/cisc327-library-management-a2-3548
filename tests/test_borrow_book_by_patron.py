import pytest
import time
from services.library_service import (
    borrow_book_by_patron,
    get_all_books,
    get_patron_borrow_count,
    get_book_by_id
)
from .util import (
    get_book_with_available_copies,
    generate_patron_id_under_borrow_limit
)
from database import get_patron_borrowed_books

def test_borrow_book_valid():
    """Test borrowing a book with valid patron ID and book ID."""
    book_id = -1
    books = get_all_books()
    for book in books:
        if book['available_copies'] > 0:
            book_id = book['id']
            break
    if book_id == -1:
        pytest.skip("No books with available copies to borrow.")

    patron_id = generate_patron_id_under_borrow_limit()
    success, message = borrow_book_by_patron(patron_id, book_id) # Assuming book ID exists and has available copies
    
    assert success == True
    assert "successfully borrowed" in message.lower()

def test_borrow_book_invalid_patron_id():
    """Test borrowing a book with invalid patron ID."""
    success, message = borrow_book_by_patron("abc123", 1) # Invalid patron ID
    
    assert success == False
    assert "invalid patron id" in message.lower()

def test_borrow_book_nonexistent_book():
    """Test borrowing a book that does not exist."""
    book_id = -1
    books = get_all_books()
    book_ids = [book['id'] for book in books]
    while book_id in book_ids:
        book_id += 1
    success, message = borrow_book_by_patron("123456", book_id)
    assert success == False
    assert "book not found" in message.lower()

def test_borrow_book_no_available_copies():
    """Test borrowing a book that has no available copies."""
    books = get_all_books()
    book_id = -1
    for book in books:
        if book['available_copies'] == 0:
            book_id = book['id']
            break
    if book_id == -1:
        pytest.skip("No books with zero available copies to test.")
    success, message = borrow_book_by_patron("123456", book_id)
    assert success == False
    assert "not available" in message.lower()

def test_borrow_book_exceed_limit():
    """Test borrowing a book when patron has already borrowed maximum allowed books."""
    books = get_all_books()
    patron_id = "123456"
    borrowed_books_ids = [book["book_id"] for book in get_patron_borrowed_books(patron_id)]
    while get_patron_borrow_count(patron_id) < 5:
        # Borrow books until the limit is reached
        book = get_book_with_available_copies(books, id_disallow_list=borrowed_books_ids)
        if book == None:
            pytest.skip("Not enough books with available copies to reach borrow limit.")
        success, _ = borrow_book_by_patron(patron_id, book["id"])
        assert success == True
        borrowed_books_ids.append(book["id"])
    # Now try to borrow one more
    book = get_book_with_available_copies(books, id_disallow_list=borrowed_books_ids)
    if book == None:
            pytest.skip("Not enough books with available copies to reach borrow limit.")
    success, message = borrow_book_by_patron(patron_id, book['id']) # Trying to borrow one more
    assert success == False
    assert "maximum borrowing limit" in message.lower()

def test_borrow_book_and_update_availability():
    """Test that borrowing a book decreases its available copies."""
    all_books = get_all_books()
    patron_id = generate_patron_id_under_borrow_limit()
    borrowed_books_ids = [book["book_id"] for book in get_patron_borrowed_books(patron_id)]
    book = get_book_with_available_copies(all_books, id_disallow_list=borrowed_books_ids)
    if book == None:
        pytest.skip("Not enough books with available copies to test.")
    initial_available = book['available_copies']
    success, _ = borrow_book_by_patron(patron_id, book["id"])
    new_book = get_book_by_id(book["id"])
    assert success == True
    assert new_book['available_copies'] == initial_available - 1

def test_borrow_book_already_borrowed():
    """Test borrowing a book that is already borrowed by the patron."""
    all_books = get_all_books()
    patron_id = generate_patron_id_under_borrow_limit(borrow_limit=4)
    borrowed_books_ids = [book["book_id"] for book in get_patron_borrowed_books(patron_id)]
    book = get_book_with_available_copies(all_books, min_available_copies=2, id_disallow_list=borrowed_books_ids)
    if book == None:
        pytest.skip("Not enough books with available copies to test.")
    success, _ = borrow_book_by_patron(patron_id, book["id"])
    assert success == True
    success, message = borrow_book_by_patron(patron_id, book["id"])
    assert success == False
    assert "already borrowed" in message.lower()
