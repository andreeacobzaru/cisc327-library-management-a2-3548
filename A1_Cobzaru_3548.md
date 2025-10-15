# A1_Cobzaru_3548.md

- **Name:** Andreea Cobzaru
- **Student ID:** 20383548
- **Group Number:** 1


## Project Implementation Status

| Requirement | Function Name                                                          | Implementation Status | What is Missing                                                                                                                                                                                                                                                                                                                                                                                                                                                                         |
| :---------: | ---------------------------------------------------------------------- | :-------------------: | --------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
|     R1      | `add_book_to_catalog`<br>also, `add_book` for web interface            |       Complete        | N/A                                                                                                                                                                                                                                                                                                                                                                                                                                                                                     |
|     R2      | `get_all_books`                                                        |       Complete        | N/A                                                                                                                                                                                                                                                                                                                                                                                                                                                                                     |
|     R3      | `borrow_book_by_patron`<br>also, `borrow_book` for web interface       |       Complete        | N/A                                                                                                                                                                                                                                                                                                                                                                                                                                                                                     |
|     R4      | `return_book_by_patron`<br>also, `return_book` for web interface       |  Incomplete/Partial   | Feature is not implemented. System does not:<ul><li>Verify Book was borrowed by the patron</li><li>Update available copies and records return date</li><li>Calculate and display any late fees owed</li></ul>`return_book_by_patron` currently returns an error message to be used by the frontend.                                                                                                                                                                                     |
|     R5      | `calculate_late_fee_for_book`<br>also, `get_late_fee` for API endpoint |  Incomplete/Partial   | Feature is not implemented. System does not:<ul><li>Calculate late fees for overdue books based on specifications in requirements</li><li>Return JSON response with fee amount and days overdue</li></ul>`calculate_late_fee_for_book` does not currently return anything, but docstrings are provided.                                                                                                                                                                                 |
|     R6      | `search_books_in_catalog`<br>also, `search_books` for web interface    |  Incomplete/Partial   | Feature is not implemented. System does not provide any sort of search functionality with the following parameters:<ul><li>`q`: search term</li><li>`type`: search type</li><li>Support partial matching for title/author (case-insensitive)</li><li>Support exact matching for ISBN</li><li>Return results in same format as catalog display</li></ul>`search_books_in_catalog` currently only returns an empty list, and docstrings are not provided.                                 |
|     R7      | `get_patron_status_report`                                             |  Incomplete/Partial   | Feature is not implemented. System does not display patron status for a particular patron that includes the following:<ul><li>Currently borrowed books with due dates</li><li>Total late fees owed</li><li>Number of books currently borrowed</li><li>Borrowing history</li></ul>In addition, the system does not contain a **menu option** for showing the patron status in the main interface.<br>`get_patron_status_report` returns an empty `dict` and does not contain docstrings. |

## Summary of Test Scripts
NOTE: I also wrote a file called `util.py` to help with test setup and mocks.
### R1: Add Book To Catalog
- `test_add_book_valid_input`
    - Note that this test is **flaky** because it modifies the database, and if the book added already exists, this test will fail.
    - Tests adding a book with all valid parameters
    - Asserts `success` as "True" and that "successfully added" is contained in `message`
- `test_add_book_invalid_isbn_not_thirteen_chars`
    - Tests adding a book with an isbn that is not equal to 13 chars
    - Asserts `success` as "False" and that "13 digits" is contained in `message`
- `test_add_book_empty_title`
    - Tests adding a book with an empty title
    - Asserts `success` as "False" and that "title is required" is contained in `message`
- `test_add_book_title_too_long`
    - Tests adding a book with a title that is too long (> 200 characters)
    - Asserts `success` as "False" and that "less than 200 characters" is contained in `message`
- `test_add_book_empty_author`
    - Tests adding a book with no author
    - Asserts `success` as "False" and that "author is required" is contained in `message`
- `test_add_book_author_too_long`
    - Tests adding a book with an author name that is too long (>100 characters)
    - Asserts `success` as "False" and that "less than 100 characters" is contained in `message`
- `test_add_book_negative_total_copies`
    - Tests adding a book with negative total copies
    - Asserts `success` as "False" and that "positive integer" is contained in `message`
- `test_add_book_zero_total_copies`
    - Tests adding a book with zero total copies
    - Asserts `success` as "False" and that "positive integer" is contained in `message`
### R2: Book Catalog Display
- `test_get_all_books`
    - This test simply runs the function and asserts that every book in the list it returns contains all fields that a book is expected to have (id, title, author, isbn, total_copies, available_copies)
- `test_correct_number_of_books_after_adding`
    - This test adds a valid book to the catalog, recording the number of books in the catalog before and after.
    - Asserts that length of list returned by `get_all_books` before and after has a difference of 1
    - Note that this test uses a function I wrote in `util.py` to create a new valid book by finding a valid isbn and calling `add_new_book_to_catalog`.
- `test_field_types`
    - This test simply asserts that each field in each book returned from `get_all_books` has the correct type
        - id: int, title: str, author: str, isbn: str, total_copies: int, available_copies: int
- `test_add_invalid_book_not_increase_catalog_size`
    - This test attempts to add an invalid book to the catalog (with negative copies) and records the number of books in the catalog before and after by calling `get_all_books`.
    - Asserts that length of list returned by `get_all_books` before and after are equal.
- Besides functional tests, I can do an inspection test and see that the book catalog display webpage meets all of the requirements
    - Book ID, Title, Author, ISBN
    - Available copies / Total copies
    - Actions (Borrow button for available books)
### R3: Book Borrowing Interface
- `test_borrow_book_valid`
    - This test calls `borrow_book_by_patron` by calling the function with a valid patron id and book id to test if it executes successfully.
    - Note that this test is **flaky** because it depends on the database. If no books are available to borrow, this test will be skipped. Also, if the patron is ever removed, this test will fail.
    - Asserts that `success` is "True" and that "successfully borrowed" is contained in `message`.
- `test_borrow_book_invalid_patron_id`
    - This test calls `borrow_book_by_patron` by calling the function with an invalid patron id and valid book id to test if it executes unsuccessfully.
    - Asserts that `success` is "False" and that "invalid patron id" is contained in `message`.
- `test_borrow_book_nonexistent_book`
    - This test calls `borrow_book_by_patron` by calling the function with a valid patron id and invalid book id to test if it executes unsuccessfully.
    - Asserts that `success` is "False" and that "book not found" is contained in `message`.
- `test_borrow_book_no_available_copies`
    - This test calls `borrow_book_by_patron` by calling the function with a valid patron id and valid book id for a book with no available copies to test if it executes unsuccessfully.
    - Note that this test is **flaky** because it depends on the database, and if there are no books with zero available copies, the test will be skipped.
    - Asserts that `success` is "False" and that "not available" is contained in `message`.
- `test_borrow_book_exceed_limit`
    - This test calls `borrow_book_by_patron` by calling the function with a valid patron id and valid book id, but the patron has already borrowed maximum allowed books
    - Note that this test is **flaky** because it depends on the database, and if there are not enough books in the database to borrow to reach the limit, the test will be skipped.
    - Asserts that `success` is "False" and that "maxiumum borrowing limit" is contained in `message`.
- `test_borrow_book_and_update_availability`
    - This test calls borrow_book_by_patron on a book with available copies and a valid patron id and asserts that the number of copies decreases after this action
    - Asserts that `success` is "True" and that available copies after is one greater than available copies before.
### R4: Book Return Processing
This function is not implemented, so these tests may not run properly.
- `test_return_book_valid`
    - This test attempts to return a book that was previously borrowed by a patron.
    - Note that this test is **flaky** because it depends on the database state and the ability to borrow a book for setup. If borrowing fails, the test is skipped.
    - Asserts that `success` is "True" and that "successfully returned" is contained in `message`.
- `test_return_book_not_borrowed`
    - This test attempts to return a book that was not borrowed by the patron.
    - Asserts that `success` is "False" and that "not borrowed" is contained in `message`.
- `test_return_book_invalid_patron_id`
    - This test attempts to return a book using an invalid patron ID.
    - Asserts that `success` is "False" and that "invalid patron id" is contained in `message`.
- `test_return_book_nonexistent_book`
    - This test attempts to return a book that does not exist in the catalog.
    - Asserts that `success` is "False" and that "book not found" is contained in `message`.
- `test_return_book_and_update_availability`
    - This test borrows a book, then returns it, and checks that the number of available copies increases by one after the return.
    - Note that this test is **flaky** because it depends on the ability to borrow a book for setup. If borrowing fails, the test may be skipped.
    - Asserts that `success` is "True" and that available copies after returning is one greater than before.
### R5: Late Fee Calculation API
This function is not implemented, so these tests may not run properly.
- `test_calculate_late_fee_invalid_borrow_record`
    - This test attempts to calculate the late fee for a non-existent borrow record.
    - Asserts that `status`, `late_fee`, and `days_overdue` are all `None`.
- `test_calculate_late_fee_not_overdue`
    - This test inserts a mock borrow record for a book that is not overdue.
    - Asserts that `"overdue"` is not in `status`, and that `late_fee` is `0.0` and `days_overdue` is `0`.
    - Note that this test is **flaky** because it depends on the ability to insert a mock borrow record. If insertion fails, the test is skipped.
- `test_calculate_late_fee_with_7_days_overdue`
    - This test inserts a mock borrow record for a book that is exactly 7 days overdue.
    - Asserts that `"overdue"` is in `status`, `late_fee` is `3.5` (7 days * $0.50), and `days_overdue` is `7`.
    - Note that this test is **flaky** because it depends on the ability to insert a mock borrow record. If insertion fails, the test is skipped.
- `test_calculate_late_fee_with_15_days_overdue`
    - This test inserts a mock borrow record for a book that is 15 days overdue.
    - Asserts that `"overdue"` is in `status`, `late_fee` is `11.5` ((7 days * $0.50) + (8 days * $1.00)), and `days_overdue` is `15`.
    - Note that this test is **flaky** because it depends on the ability to insert a mock borrow record. If insertion fails, the test is skipped.
- `test_calculate_late_fee_with_100_days_overdue`
    - This test inserts a mock borrow record for a book that is 100 days overdue.
    - Asserts that `"overdue"` is in `status`, `late_fee` is capped at `15.0`, and `days_overdue` is `100`.
    - Note that this test is **flaky** because it depends on the ability to insert a mock borrow record. If insertion fails, the test is skipped.
### R6: Book Search Functionality
This function is not implemented, so these tests may not run properly.
- `test_search_books_by_title_success`
    - This test searches for books by title using a sample title.
    - Asserts that the result is a list, that each book in the result contains the search term (case-insensitive) in the title, and that the result matches a filtered list from all books.
- `test_search_books_by_author_success`
    - This test searches for books by author using a sample author.
    - Asserts that the result is a list, that each book in the result contains the search term (case-insensitive) in the author field, and that the result matches a filtered list from all books.
- `test_search_books_by_isbn_success`
    - This test adds a new book and then searches for it by its ISBN.
    - Asserts that the result is a list, that each book in the result has the exact ISBN, and that the result matches a filtered list from all books.
    - Note that this test is **flaky** because it depends on the ability to add a new book for testing. If adding fails, the test is skipped.
- `test_search_books_no_results`
    - This test searches for a book with a title that does not exist.
    - Asserts that the result is a list and that the list is empty.
    - Note that this test could be **flaky** if a book with the test title is ever added to the database.
### R7: Patron Status Report
This function is not implemented, so these tests may not run properly.
- `test_get_patron_status_report_valid`
    - This test gets a patron status report for a valid patron ID.
    - Asserts that the result is a dict and contains the keys: `patron_id`, `currently_borrowed_books`, `total_late_fees_owed`, and `borrowing_history`.
- `test_get_patron_status_report_invalid_patron_id`
    - This test gets a patron status report for an invalid patron ID.
    - Asserts that the result is `None`.
- `test_get_patron_status_report_contains_borrowed_books`
    - This test ensures the report contains correct information about currently borrowed books for a patron who has borrowed a book.
    - Asserts that the result is a dict, contains `currently_borrowed_books`, and that the list is not empty. Also checks that each borrowed book contains the keys: `book_id`, `title`, `borrow_date`, `due_date`, and `return_date`.
    - Note that this test is **flaky** because it depends on the ability to borrow a book for setup.
- `test_get_patron_status_report_contains_late_fees`
    - This test ensures the report includes late fees for overdue books.
    - Asserts that the result is a dict, contains `currently_borrowed_books` (not empty), contains `total_late_fees_owed` as a number, and that the value is greater than 0.0.
    - Note that this test is **flaky** because it depends on the ability to insert a mock borrow record.
- `test_get_patron_status_report_borrowing_history`
    - This test ensures the report includes borrowing history.
    - Asserts that the result is a dict, contains `borrowing_history` as a list, and that each record contains the keys: `book_id`, `title`, `borrow_date`, `due_date`, and `return_date`.