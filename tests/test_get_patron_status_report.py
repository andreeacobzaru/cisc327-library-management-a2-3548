import pytest
from datetime import datetime, timedelta
from library_service import (
    get_patron_status_report,
    borrow_book_by_patron
)
from .util import (
    mock_insert_borrow_record,
)

def test_get_patron_status_report_valid():
    """Test getting patron status report with valid patron ID."""
    report = get_patron_status_report("123456")
    
    assert isinstance(report, dict)
    assert 'patron_id' in report
    assert 'currently_borrowed_books' in report
    assert 'total_late_fees_owed' in report
    assert 'borrowing_history' in report

def test_get_patron_status_report_invalid_patron_id():
    """Test getting patron status report with invalid patron ID."""
    report = get_patron_status_report("abc123")  # Invalid patron ID
    
    assert report is None

def test_get_patron_status_report_contains_borrowed_books():
    """Test that the report contains correct borrowed books information."""
    # First, ensure the patron has borrowed a book
    borrow_success, _ = borrow_book_by_patron("654321", 1)  # Assuming book ID 1 exists and has available copies
    assert borrow_success == True
    
    report = get_patron_status_report("654321")
    
    assert isinstance(report, dict)
    assert 'currently_borrowed_books' in report
    assert len(report['currently_borrowed_books']) > 0
    for book in report['currently_borrowed_books']:
        assert 'book_id' in book
        assert 'title' in book
        assert 'author' in book
        assert 'borrow_date' in book
        assert 'due_date' in book
        assert 'is_overdue' in book

def test_get_patron_status_report_contains_late_fees():
    """Test that the report includes late fees for overdue books."""
    mock_borrow_date = (datetime.today() - timedelta(days=29))
    success, patron_id, book_id = mock_insert_borrow_record(book=None, patron_id=None, borrow_date=mock_borrow_date, due_date=None)
    if not success:
        pytest.skip("Failed to insert mock borrow record.")
    report = get_patron_status_report(patron_id)
    
    assert isinstance(report, dict)
    assert 'currently_borrowed_books' in report
    assert len(report['currently_borrowed_books']) > 0
    assert 'total_late_fees_owed' in report
    assert isinstance(report['total_late_fees_owed'], (int, float))
    assert report['total_late_fees_owed'] > 0.0

def test_get_patron_status_report_borrowing_history():
    """Test that the report includes borrowing history."""
    report = get_patron_status_report("123456")
    
    assert isinstance(report, dict)
    assert 'borrowing_history' in report
    assert isinstance(report['borrowing_history'], list)
    for record in report['borrowing_history']:
        assert 'book_id' in record
        assert 'title' in record
        assert 'author' in record
        assert 'borrow_date' in record
        assert 'due_date' in record
        assert 'return_date' in record