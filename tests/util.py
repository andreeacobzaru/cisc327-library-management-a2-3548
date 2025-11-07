from datetime import datetime, timedelta
from services.library_service import (
    add_book_to_catalog,
    get_patron_borrow_count,
    borrow_book_by_patron,
    get_all_books,
    get_book_by_isbn
)
from database import insert_borrow_record, setup_database_for_testing

def add_new_book_for_testing(all_books, title=None, author=None, available_copies=5):
    """Helper function to add a new book with a unique ISBN for testing."""
    book_isbns = [book['isbn'] for book in all_books]
    isbn = "0000000000000"
    while isbn in book_isbns:
        isbn = str(int(isbn) + 1).zfill(13)
    if title is None:
        title = f"Test Book {int(isbn)}"
    if author is None:
        author = f"Test Author {int(isbn)}"
    success, message = add_book_to_catalog(title, author, isbn, available_copies)
    return success, message, isbn

def get_book_with_available_copies(all_books, min_available_copies=1, id_disallow_list=[]):
    """Helper function to get a book ID with available copies."""
    for book in all_books:
        if book['available_copies'] >= min_available_copies and book['id'] not in id_disallow_list:
            return book
    return None

def generate_patron_id_under_borrow_limit(borrow_limit=5):
    """Helper function to generate a patron ID that has borrowed less than borrow_limit books."""
    patron_id = "000001"
    while get_patron_borrow_count(patron_id) >= borrow_limit:
        patron_id = str(int(patron_id) + 1).zfill(6)  # Increment patron ID to find one under limit
    return patron_id

def mock_borrow_book(all_books, book=None, patron_id=None):
    """Helper function to mock borrowing a book for testing return functionality."""
    if patron_id is None:
        patron_id = generate_patron_id_under_borrow_limit()
    if book is None:
        success, _, isbn = add_new_book_for_testing(all_books)
        if not success:
            return False
        book = get_book_by_isbn(isbn)
    book_id = book['id']
    success, _ = borrow_book_by_patron(patron_id, book_id)
    return success, patron_id, book_id

def get_nonexistent_book_id(all_books):
    """Helper function to get a book ID that does not exist in the catalog."""
    existing_ids = [book['id'] for book in all_books]
    if not existing_ids:
        return 1  # If no books exist, return 1 as a non-existent ID
    non_existent_id = existing_ids[-1] + 1
    while non_existent_id in existing_ids:
        non_existent_id += 1
    return non_existent_id

def mock_insert_borrow_record(book=None, patron_id=None, borrow_date=None, due_date=None):
    """Helper function to directly insert a borrow record into the database for testing."""
    if book is None:
        all_books = get_all_books()
        success, _, _ = add_new_book_for_testing(all_books)
        if not success:
            return False
        all_books = get_all_books()
        book = get_book_with_available_copies(all_books)
    book_id = book['id']
    if patron_id is None:
        patron_id = generate_patron_id_under_borrow_limit()
    if borrow_date is None:
        borrow_date = datetime.today()
    if due_date is None:
        due_date = (borrow_date + timedelta(days=14))
    insert_borrow_record(patron_id, book_id, borrow_date, due_date)
    return True, patron_id, book_id

def setup_pretest_database():
    """
    Pre-test setup function to clear the database and prepopulate with test books.

    Returns:
        bool: True if setup was successful, False otherwise
    """
    setup_database_for_testing()
    return True
