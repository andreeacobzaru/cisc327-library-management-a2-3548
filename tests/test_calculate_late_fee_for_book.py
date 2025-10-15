import pytest
from datetime import datetime, timedelta
from library_service import (
    get_all_books,
    calculate_late_fee_for_book
)
from .util import (
    get_nonexistent_book_id,
    mock_insert_borrow_record,
)

"""
Calculates late fees for overdue books based on:
Books due 14 days after borrowing
- $0.50/day for first 7 days overdue
- $1.00/day for each additional day after 7 days
- Maximum $15.00 per book
"""
def test_calculate_late_fee_invalid_borrow_record():
    """Test calculating late fee for a non-existent borrow record."""
    book_id = get_nonexistent_book_id(get_all_books())
    result = calculate_late_fee_for_book("123456", book_id)
    assert result['status'] == "Book not found."
    assert result['fee_amount'] == None
    assert result['days_overdue'] == None

def test_calculate_late_fee_not_overdue():
    """Test calculating late fee for a book returned on time."""
    mock_borrow_date = datetime.today()
    success, patron_id, book_id = mock_insert_borrow_record(book=None, patron_id=None, borrow_date=mock_borrow_date, due_date=None)
    if not success:
        pytest.skip("Failed to insert mock borrow record.")
    result = calculate_late_fee_for_book(patron_id, book_id)
    assert result['status'] == "Not overdue"
    assert result['fee_amount'] == 0.0
    assert result['days_overdue'] == 0

def test_calculate_late_fee_with_7_days_overdue():
    """Test calculating late fee for a book returned 7 days late."""
    mock_borrow_date = (datetime.today() - timedelta(days=21))    
    success, patron_id, book_id = mock_insert_borrow_record(book=None, patron_id=None, borrow_date=mock_borrow_date, due_date=None)
    if not success:
        pytest.skip("Failed to insert mock borrow record.")
    result = calculate_late_fee_for_book(patron_id, book_id)
    assert "overdue" in result['status'].lower()
    assert result['fee_amount'] == 3.5  # 7 days * $0.50
    assert result['days_overdue'] == 7

def test_calculate_late_fee_with_15_days_overdue():
    """Test calculating late fee for a book returned 15 days late."""
    mock_borrow_date = (datetime.today() - timedelta(days=29))
    success, patron_id, book_id = mock_insert_borrow_record(book=None, patron_id=None, borrow_date=mock_borrow_date, due_date=None)
    if not success:
        pytest.skip("Failed to insert mock borrow record.")
    result = calculate_late_fee_for_book(patron_id, book_id)
    assert "overdue" in result['status'].lower()
    assert result['fee_amount'] == 11.5  # (7 days * $0.50) + (8 days * $1.00)
    assert result['days_overdue'] == 15


def test_calculate_late_fee_with_100_days_overdue():
    """Test calculating late fee for a book returned 100 days late, should cap at $15.00."""
    mock_borrow_date = (datetime.today() - timedelta(days=114))
    success, patron_id, book_id = mock_insert_borrow_record(book=None, patron_id=None, borrow_date=mock_borrow_date, due_date=None)
    if not success:
        pytest.skip("Failed to insert mock borrow record.")
    result = calculate_late_fee_for_book(patron_id, book_id)
    assert "overdue" in result['status'].lower()
    assert result['fee_amount'] == 15.0  # Capped at $15.00
    assert result['days_overdue'] == 100