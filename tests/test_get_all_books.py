import pytest

from .util import add_new_book_for_testing
from services.library_service import (
    add_book_to_catalog,
    get_all_books
)

def test_get_all_books():
    """Test retrieving all books from the catalog."""
    books = get_all_books()
    
    assert isinstance(books, list)
    for book in books:
        assert 'id' in book
        assert 'title' in book
        assert 'author' in book
        assert 'isbn' in book
        assert 'total_copies' in book
        assert 'available_copies' in book

def test_correct_number_of_books_after_adding():
    """After adding a book, get_all_books should have increased count"""
    
    books_before = get_all_books()
    success, _, _ = add_new_book_for_testing(books_before)
    if success == False:
        pytest.skip("Failed to add a new book for testing.")
    books_after = get_all_books()
    assert len(books_after) - len(books_before) == 1

def test_field_types():
    """Check that each field has the correct type."""
    books = get_all_books()
    for book in books:
        assert isinstance(book['id'], int)
        assert isinstance(book['title'], str)
        assert isinstance(book['author'], str)
        assert isinstance(book['isbn'], str)
        assert isinstance(book['total_copies'], int)
        assert isinstance(book['available_copies'], int)

def test_add_invalid_book_not_increase_catalog_size():
    """Adding an invalid book, i.e. a book with negative total copies, should not increase catalog size."""
    books_before = get_all_books()
    try:
        add_book_to_catalog("Invalid Book", "Author X", "9999999999999", -5)
    except Exception:
        pass
    books_after = get_all_books()
    assert len(books_after) == len(books_before)
