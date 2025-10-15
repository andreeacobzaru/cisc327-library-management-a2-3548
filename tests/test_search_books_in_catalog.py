import pytest

from library_service import (
    get_all_books,
    search_books_in_catalog
)
from .util import (
    add_new_book_for_testing
)

def test_search_books_by_title_success():
    """Test searching books by title."""
    searched_books = search_books_in_catalog("Test Book", "title")
    all_books = get_all_books()
    mock_searched_books = [book for book in all_books if "test book" in book['title'].lower()]
    
    assert isinstance(searched_books, list)
    for book in searched_books:
        assert "test book" in book['title'].lower()
    assert sorted(searched_books, key=lambda book: book["id"]) == sorted(mock_searched_books, key=lambda book: book["id"])

def test_search_books_by_author_success():
    """Test searching books by author."""
    searched_books = search_books_in_catalog("Test Author", "author")
    all_books = get_all_books()
    mock_searched_books = [book for book in all_books if "test author" in book['author'].lower()]
    
    assert isinstance(searched_books, list)
    for book in searched_books:
        assert "test author" in book['author'].lower()
    assert sorted(searched_books, key=lambda book: book["id"]) == sorted(mock_searched_books, key=lambda book: book["id"])

def test_search_books_by_isbn_success():
    """Test searching books by ISBN."""
    success, _, isbn = add_new_book_for_testing(get_all_books())
    if not success:
        pytest.skip("Failed to add a new book for testing.")
    
    searched_books = search_books_in_catalog(isbn, "isbn")
    all_books = get_all_books()
    mock_searched_books = [book for book in all_books if isbn == book['isbn']]
    
    assert isinstance(searched_books, list)
    for book in searched_books:
        assert isbn == book['isbn']
    assert sorted(searched_books, key=lambda book: book["id"]) == sorted(mock_searched_books, key=lambda book: book["id"])

def test_search_books_no_results():
    """Test searching books with no matching results."""
    books = search_books_in_catalog("NonExistentBookTitle", "title") # could be flaky
    
    assert isinstance(books, list)
    assert len(books) == 0
