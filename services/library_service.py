"""
Library Service Module - Business Logic Functions
Contains all the core business logic for the Library Management System
"""

from datetime import datetime, timedelta
from typing import Dict, List, Optional, Tuple
from database import (
    get_book_by_id, get_book_by_isbn, get_patron_borrow_count,
    insert_book, insert_borrow_record, update_book_availability,
    update_borrow_record_return_date, get_all_books, get_patron_borrowed_books, get_patron_borrowing_history
)
from services.payment_service import PaymentGateway

def add_book_to_catalog(title: str, author: str, isbn: str, total_copies: int) -> Tuple[bool, str]:
    """
    Add a new book to the catalog.
    Implements R1: Book Catalog Management
    
    Args:
        title: Book title (max 200 chars)
        author: Book author (max 100 chars)
        isbn: 13-digit ISBN
        total_copies: Number of copies (positive integer)
        
    Returns:
        tuple: (success: bool, message: str)
    """
    # Input validation
    if not title or not title.strip():
        return False, "Title is required."
    
    if len(title.strip()) > 200:
        return False, "Title must be less than 200 characters."
    
    if not author or not author.strip():
        return False, "Author is required."
    
    if len(author.strip()) > 100:
        return False, "Author must be less than 100 characters."
    
    if len(isbn) != 13:
        return False, "ISBN must be exactly 13 digits."
    
    if not isinstance(total_copies, int) or total_copies <= 0:
        return False, "Total copies must be a positive integer."
    
    # Check for duplicate ISBN
    existing = get_book_by_isbn(isbn)
    if existing:
        return False, "A book with this ISBN already exists."
    
    # Insert new book
    success = insert_book(title.strip(), author.strip(), isbn, total_copies, total_copies)
    if success:
        return True, f'Book "{title.strip()}" has been successfully added to the catalog.'
    else:
        return False, "Database error occurred while adding the book."

def borrow_book_by_patron(patron_id: str, book_id: int) -> Tuple[bool, str]:
    """
    Allow a patron to borrow a book.
    Implements R3 as per requirements  
    
    Args:
        patron_id: 6-digit library card ID
        book_id: ID of the book to borrow
        
    Returns:
        tuple: (success: bool, message: str)
    """
    # Validate patron ID
    if not patron_id or not patron_id.isdigit() or len(patron_id) != 6:
        return False, "Invalid patron ID. Must be exactly 6 digits."
    
    # Check if book exists and is available
    book = get_book_by_id(book_id)
    if not book:
        return False, "Book not found."
    
    if book['available_copies'] <= 0:
        return False, "This book is currently not available."
    
    # Check patron's current borrowed books count
    current_borrowed = get_patron_borrow_count(patron_id)
    if current_borrowed >= 5:
        return False, "You have reached the maximum borrowing limit of 5 books."

    # Check if book is already borrowed by this patron
    borrowed_books = get_patron_borrowed_books(patron_id)
    for book in borrowed_books:
        if book['book_id'] == book_id:
            return False, "This book is already borrowed by you."
    
    # Create borrow record
    borrow_date = datetime.now()
    due_date = borrow_date + timedelta(days=14)
    
    # Insert borrow record and update availability
    borrow_success = insert_borrow_record(patron_id, book_id, borrow_date, due_date)
    if not borrow_success:
        return False, "Database error occurred while creating borrow record."
    
    availability_success = update_book_availability(book_id, -1)
    if not availability_success:
        return False, "Database error occurred while updating book availability."
    
    return True, f'Successfully borrowed "{book["title"]}". Due date: {due_date.strftime("%Y-%m-%d")}.'

def return_book_by_patron(patron_id: str, book_id: int) -> Tuple[bool, str]:
    """
    Process book return by a patron.
    Implements R4 as per requirements

    Args:
        patron_id: 6-digit library card ID
        book_id: ID of the book to return
        
    Returns:
        tuple: (success: bool, message: str)
    """
    # Validate patron ID
    if not patron_id or not patron_id.isdigit() or len(patron_id) != 6:
        return False, "Invalid patron ID. Must be exactly 6 digits."

    # Check if book exists and is borrowed by this patron
    book = get_book_by_id(book_id)
    if not book:
        return False, "Book not found."

    # Check if book is borrowed by this patron
    borrowed_books = get_patron_borrowed_books(patron_id)
    borrow_record = None
    for book in borrowed_books:
        if book['book_id'] == book_id:
            borrow_record = book
            break
    if not borrow_record:
        return False, "Book was not borrowed by this patron."

    # Update return date and book availability
    return_date = datetime.now()
    return_success = update_borrow_record_return_date(patron_id, book_id, return_date)
    if not return_success:
        return False, "Database error occurred while updating return date."
    
    availability_success = update_book_availability(book_id, 1)
    if not availability_success:
        return False, "Database error occurred while updating book availability."

    return True, f'Successfully returned "{book["title"]}". Return date: {return_date.strftime("%Y-%m-%d")}.'

def calculate_late_fee_for_book(patron_id: str, book_id: int) -> Dict:
    """
    Calculate late fees for a specific book.
    
    Implements R5 as per requirements

    Args:
        patron_id: 6-digit library card ID
        book_id: ID of the book to calculate late fee for
        
    Returns:
        dict: {'fee_amount': float, 'days_overdue': int, 'status': str}
            {'fee_amount': 0.0, 'days_overdue': None, 'status': str} if not found
    """
    # Validate patron ID
    if not patron_id or not patron_id.isdigit() or len(patron_id) != 6:
        return {'fee_amount': 0.0, 'days_overdue': None, 'status': "Invalid patron ID. Must be exactly 6 digits."}

    # Check if book exists
    book = get_book_by_id(book_id)
    if not book:
        return {'fee_amount': 0.0, 'days_overdue': None, 'status': "Book not found."}

    # Check if book is borrowed by this patron
    borrowed_books = get_patron_borrowed_books(patron_id)
    borrow_record = None
    for book in borrowed_books:
        if book['book_id'] == book_id:
            borrow_record = book
            break
    if not borrow_record:
        return {'fee_amount': 0.0, 'days_overdue': None, 'status': "Borrow record not found."}

    # Extract dates from borrow_record
    due_date = borrow_record.get("due_date")

    days_overdue = (datetime.today() - due_date).days
    late_fee = 0.0

    # Calculate late fee
    if days_overdue <= 0:
        days_overdue = 0
        status = "Not overdue"
    elif days_overdue >= 7:
        # $0.50/day for first 7 days, then $1.00/day after, max $15.00
        late_fee = 7 * 0.5 + (days_overdue - 7) * 1.0
        late_fee = min(late_fee, 15.0)
        status = "Overdue"

    return {'fee_amount': late_fee, 'days_overdue': days_overdue, 'status': status}

def search_books_in_catalog(search_term: str, search_type: str) -> List[Dict]:
    """
    Search for books in the catalog.
    
    Implements R6 as per requirements

    Args:
        search_term: search term
        search_type: search type
        
    Returns:
        list: list of books
    """
    # Validate search type
    if search_type.lower() not in ['title', 'author', 'isbn']:
        return []

    search_type = search_type.lower()
    search_term = search_term.lower()

    # Search for books
    books = get_all_books()
    result = []
    if search_type == 'isbn':
        for book in books:
            if search_term == book['isbn']:
                result.append(book)
        return result
    for book in books:
        if search_term in book[search_type].lower():
            result.append(book)
    return result

def get_patron_status_report(patron_id: str) -> Dict:
    """
    Get status report for a patron.
    
    Implements R7 as per requirements

    Args:
        patron_id: 6-digit library card ID
        
    Returns:
        dict: 
            Dictionary representing the patron status report:
                - 'patron_id' (str): Patron's 6-digit library card ID
                - 'currently_borrowed_books' (list of dict): List of currently borrowed books with fields:
                    - 'book_id' (int)
                    - 'title' (str)
                    - 'borrow_date' (str)
                    - 'due_date' (str)
                    - 'return_date' (str or None)
                - 'total_late_fees_owed' (float): Total amount of late fees currently owed by the patron
                - 'borrowing_history' (list of dict): Complete borrowing history records (same fields as above)
            Returns None for invalid patron ID input (must be exactly 6 digits).
    """
    # Validate patron ID
    if not patron_id or not patron_id.isdigit() or len(patron_id) != 6:
        return None
    
    # Get patron's currently borrowed books
    currently_borrowed_books = get_patron_borrowed_books(patron_id) # also contains borrow history

    # Get patron's late fees
    late_fees = 0.0
    for book in currently_borrowed_books:
        result = calculate_late_fee_for_book(patron_id, book['book_id'])
        late_fee = result['fee_amount']
        status = result['status']
        if status == "Overdue":
            late_fees += late_fee
    
    # Get patron's borrowing history
    borrowing_history = get_patron_borrowing_history(patron_id)

    if not currently_borrowed_books or not borrowing_history:
        return None

    return {
        'patron_id': patron_id,
        'currently_borrowed_books': currently_borrowed_books,
        'total_late_fees_owed': late_fees,
        'borrowing_history': borrowing_history
    }

def pay_late_fees(patron_id: str, book_id: int, payment_gateway: PaymentGateway = None) -> Tuple[bool, str, Optional[str]]:
    """
    Process payment for late fees using external payment gateway.
    
    NEW FEATURE FOR ASSIGNMENT 3: Demonstrates need for mocking/stubbing
    This function depends on an external payment service that should be mocked in tests.
    
    Args:
        patron_id: 6-digit library card ID
        book_id: ID of the book with late fees
        payment_gateway: Payment gateway instance (injectable for testing)
        
    Returns:
        tuple: (success: bool, message: str, transaction_id: Optional[str])
        
    Example for you to mock:
        # In tests, mock the payment gateway:
        mock_gateway = Mock(spec=PaymentGateway)
        mock_gateway.process_payment.return_value = (True, "txn_123", "Success")
        success, msg, txn = pay_late_fees("123456", 1, mock_gateway)
    """
    # Validate patron ID
    if not patron_id or not patron_id.isdigit() or len(patron_id) != 6:
        return False, "Invalid patron ID. Must be exactly 6 digits.", None
    
    # Calculate late fee first
    fee_info = calculate_late_fee_for_book(patron_id, book_id)
    
    # Check if there's a fee to pay
    if not fee_info or 'fee_amount' not in fee_info:
        return False, "Unable to calculate late fees.", None
    
    fee_amount = fee_info.get('fee_amount', 0.0)
    if fee_amount <= 0:
        return False, "No late fees to pay for this book.", None
    
    # Get book details for payment description
    book = get_book_by_id(book_id)
    if not book:
        return False, "Book not found.", None
    
    # Use provided gateway or create new one
    if payment_gateway is None:
        payment_gateway = PaymentGateway()
    
    # Process payment through external gateway
    # THIS IS WHAT YOU SHOULD MOCK IN THEIR TESTS!
    try:
        success, transaction_id, message = payment_gateway.process_payment(
            patron_id=patron_id,
            amount=fee_amount,
            description=f"Late fees for '{book['title']}'"
        )
        
        if success:
            return True, f"Payment successful! {message}", transaction_id
        else:
            return False, f"Payment failed: {message}", None
            
    except Exception as e:
        # Handle payment gateway errors
        return False, f"Payment processing error: {str(e)}", None


def refund_late_fee_payment(transaction_id: str, amount: float, payment_gateway: PaymentGateway = None) -> Tuple[bool, str]:
    """
    Refund a late fee payment (e.g., if book was returned on time but fees were charged in error).
    
    NEW FEATURE FOR ASSIGNMENT 3: Another function requiring mocking
    
    Args:
        transaction_id: Original transaction ID to refund
        amount: Amount to refund
        payment_gateway: Payment gateway instance (injectable for testing)
        
    Returns:
        tuple: (success: bool, message: str)
    """
    # Validate inputs
    if not transaction_id or not transaction_id.startswith("txn_"):
        return False, "Invalid transaction ID."
    
    if amount <= 0:
        return False, "Refund amount must be greater than 0."
    
    if amount > 15.00:  # Maximum late fee per book
        return False, "Refund amount exceeds maximum late fee."
    
    # Use provided gateway or create new one
    if payment_gateway is None:
        payment_gateway = PaymentGateway()
    
    # Process refund through external gateway
    # THIS IS WHAT YOU SHOULD MOCK IN YOUR TESTS!
    try:
        success, message = payment_gateway.refund_payment(transaction_id, amount)
        
        if success:
            return True, message
        else:
            return False, f"Refund failed: {message}"
            
    except Exception as e:
        return False, f"Refund processing error: {str(e)}"