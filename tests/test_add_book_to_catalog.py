import pytest
from services.library_service import (
    add_book_to_catalog
)

def test_add_book_valid_input():
    """Test adding a book with valid input."""
    success, message = add_book_to_catalog("Test Book", "Test Author", "0123456789124", 5)
    
    assert success == True
    assert "successfully added" in message.lower()

def test_add_book_invalid_isbn_not_thirteen_chars():
    """Test adding a book with ISBN length not equal to thirteen chars."""
    success, message = add_book_to_catalog("Test Book", "Test Author", "123456789", 5)
    
    assert success == False
    assert "13 digits" in message

def test_add_book_duplicate_isbn():
    """Test adding a book with a duplicate ISBN."""
    fake_isbn = "0123456789125"
    add_book_to_catalog("Original Book", "Original Author", fake_isbn, 3)
    success, message = add_book_to_catalog("Duplicate Book", "Duplicate Author", fake_isbn, 2)
    
    assert success == False
    assert "already exists" in message.lower()

def test_add_book_empty_title():
    """Test adding a book with an empty title."""
    success, message = add_book_to_catalog("", "Test Author", "1234567890123", 5)
    
    assert success == False
    assert "title is required" in message.lower()

def test_add_book_title_too_long():
    """Test adding a book with a title that is too long."""
    long_title = "a" * 201
    success, message = add_book_to_catalog(long_title, "Test Author", "1234567890123", 5)
    
    assert success == False
    assert "less than 200 characters" in message.lower()

def test_add_book_empty_author():
    """Test adding a book with an empty author."""
    success, message = add_book_to_catalog("Test Book", "", "1234567890123", 5)
    
    assert success == False
    assert "author is required" in message.lower()

def test_add_book_author_too_long():
    """Test adding a book with an author name that is too long."""
    long_author = "a" * 101
    success, message = add_book_to_catalog("Test Book", long_author, "1234567890123", 5)
    
    assert success == False
    assert "less than 100 characters" in message.lower()

def test_add_book_negative_total_copies():
    """Test adding a book with negative total copies."""
    success, message = add_book_to_catalog("Test Book", "Test Author", "1234567890123", -1)
    
    assert success == False
    assert "positive integer" in message.lower()

def test_add_book_zero_total_copies():
    """Test adding a book with zero total copies."""
    success, message = add_book_to_catalog("Test Book", "Test Author", "1234567890123", 0)
    
    assert success == False
    assert "positive integer" in message.lower()