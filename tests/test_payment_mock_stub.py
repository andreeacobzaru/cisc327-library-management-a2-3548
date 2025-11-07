import pytest
from services.library_service import pay_late_fees, refund_late_fee_payment
from services.payment_service import PaymentGateway
from unittest.mock import Mock

def test_pay_late_fees_invalid_patron_id(mocker):
    '''Test paying late fees with an invalid patron ID.'''
    mock_calc_fee = mocker.patch(
        "services.library_service.calculate_late_fee_for_book", 
        return_value={'fee_amount': 0.0, 'days_overdue': None, 'status': ""}
    )

    mock_get_book = mocker.patch(
        "services.library_service.get_book_by_id",
        return_value=None
    )

    mock_payment_gateway = Mock(spec=PaymentGateway)

    success, message, transaction_id = pay_late_fees(patron_id="abcdef", book_id=999, payment_gateway=mock_payment_gateway)
    assert success == False
    assert "invalid patron id" in message.lower()
    assert transaction_id is None

    mock_payment_gateway.process_payment.assert_not_called()

def test_pay_late_fees_no_late_fees(mocker):
    '''Test paying late fees when there are no late fees for the patron.'''
    mock_calc_fee = mocker.patch(
        "services.library_service.calculate_late_fee_for_book", 
        return_value={'fee_amount': 0.0, 'days_overdue': None, 'status': ""}
    )

    mock_get_book = mocker.patch(
        "services.library_service.get_book_by_id",
        return_value=None
    )
    mock_payment_gateway = Mock(spec=PaymentGateway)

    success, message, transaction_id = pay_late_fees(patron_id="123456", book_id=999, payment_gateway=mock_payment_gateway)
    assert success == False
    assert "no late fees" in message.lower()
    assert transaction_id is None

    mock_payment_gateway.process_payment.assert_not_called()

def test_pay_late_fees_invalid_book_id(mocker):
    '''Test paying late fees with an invalid book ID.'''

    mock_calc_fee = mocker.patch(
        "services.library_service.calculate_late_fee_for_book", 
        return_value={'fee_amount': 5.0, 'days_overdue': 3, 'status': 'overdue'}
    )

    mock_get_book = mocker.patch(
        "services.library_service.get_book_by_id",
        return_value=None
    )
    mock_payment_gateway = Mock(spec=PaymentGateway)
    success, message, transaction_id = pay_late_fees(patron_id="123456", book_id=999, payment_gateway=mock_payment_gateway)
    
    assert success == False
    assert "book not found" in message.lower()
    assert transaction_id is None

    mock_payment_gateway.process_payment.assert_not_called()

def test_pay_late_fees_valid_payment(mocker):
    mock_calc_fee = mocker.patch(
        "services.library_service.calculate_late_fee_for_book", 
        return_value={'fee_amount': 5.0, 'days_overdue': 3, 'status': 'overdue'}
    )

    mock_get_book = mocker.patch(
        "services.library_service.get_book_by_id",
        return_value={"author":"Test Author","available_copies":2,"id":999,"isbn":"1234567890123","title":"Test Book","total_copies":3}
    )

    book_id = mock_get_book.return_value['id']
    book_title = mock_get_book.return_value['title']
    fee_amount = mock_calc_fee.return_value['fee_amount']
    
    mock_payment_gateway = Mock(spec=PaymentGateway)
    fake_patron_id = "123456"

    mock_payment_gateway.process_payment.return_value = (True, f"txn_{fake_patron_id}_1234567890", f"Payment successful! Payment of ${fee_amount:.2f} processed successfully")
    success, message, transaction_id = pay_late_fees(patron_id=fake_patron_id, book_id=book_id, payment_gateway=mock_payment_gateway)
    
    assert success == True
    assert "payment of $5.00 processed successfully" in message.lower()
    assert transaction_id is not None
    
    mock_payment_gateway.process_payment.assert_called_once()
    mock_payment_gateway.process_payment.assert_called_with(
        amount=5.00, 
        patron_id=fake_patron_id,
        description=f"Late fees for '{book_title}'"
    )

def test_pay_late_fees_payment_gateway_error_failure(mocker):
    '''Test paying late fees when the payment gateway fails.'''

    mock_calc_fee = mocker.patch(
        "services.library_service.calculate_late_fee_for_book", 
        return_value={'fee_amount': 5.0, 'days_overdue': 3, 'status': 'overdue'}
    )

    mock_get_book = mocker.patch(
        "services.library_service.get_book_by_id",
        return_value={"author":"Test Author","available_copies":2,"id":999,"isbn":"1234567890123","title":"Test Book","total_copies":3}
    )

    book_id = mock_get_book.return_value['id']
    book_title = mock_get_book.return_value['title']
    
    mock_payment_gateway = Mock(spec=PaymentGateway)
    fake_patron_id = "123456"

    mock_payment_gateway.process_payment.return_value = (False, "", "Payment declined: amount exceeds limit")
    success, message, transaction_id = pay_late_fees(patron_id=fake_patron_id, book_id=book_id, payment_gateway=mock_payment_gateway)
    
    assert success == False
    assert "payment failed" in message.lower()
    assert transaction_id is None
    
    mock_payment_gateway.process_payment.assert_called_once()
    mock_payment_gateway.process_payment.assert_called_with(
        amount=5.00, 
        patron_id=fake_patron_id,
        description=f"Late fees for '{book_title}'"
    )

def test_pay_late_fees_payment_exception_error(mocker):
    '''Test paying late fees when the payment gateway raises an exception.'''

    mock_calc_fee = mocker.patch(
        "services.library_service.calculate_late_fee_for_book", 
        return_value={'fee_amount': 5.0, 'days_overdue': 3, 'status': 'overdue'}
    )

    mock_get_book = mocker.patch(
        "services.library_service.get_book_by_id",
        return_value={"author":"Test Author","available_copies":2,"id":999,"isbn":"1234567890123","title":"Test Book","total_copies":3}
    )

    book_id = mock_get_book.return_value['id']
    book_title = mock_get_book.return_value['title']

    mock_payment_gateway = Mock(spec=PaymentGateway)
    fake_patron_id = "123456"

    mock_payment_gateway.process_payment.side_effect = Exception("network error")
    success, message, transaction_id = pay_late_fees(patron_id=fake_patron_id, book_id=book_id, payment_gateway=mock_payment_gateway)

    assert success == False
    assert "payment processing error" in message.lower()
    assert transaction_id is None

    mock_payment_gateway.process_payment.assert_called_once()
    mock_payment_gateway.process_payment.assert_called_with(
        amount=5.00, 
        patron_id=fake_patron_id,
        description=f"Late fees for '{book_title}'"
    )


##### REFUNDS #####

def test_refund_late_fee_payment_invalid_transaction_id(mocker):
    '''Test refunding late fee payment with an invalid transaction ID.'''

    fake_transaction_id = "invalid_txn_123"
    fake_refund_amount = 5.0
    mock_payment_gateway = Mock(spec=PaymentGateway)

    success, message = refund_late_fee_payment(
        transaction_id=fake_transaction_id,
        amount=fake_refund_amount,
        payment_gateway=mock_payment_gateway
    )

    assert success == False
    assert "invalid transaction id" in message.lower()

    mock_payment_gateway.refund_payment.assert_not_called()

def test_refund_late_fee_payment_negative_refund_amount():
    '''Test refunding late fee payment with a negative refund amount.'''
    fake_transaction_id = "txn_123456_1617181920"
    fake_refund_amount = -10.0
    mock_payment_gateway = Mock(spec=PaymentGateway)

    success, message = refund_late_fee_payment(
        transaction_id=fake_transaction_id,
        amount=fake_refund_amount,
        payment_gateway=mock_payment_gateway
    )

    assert success == False
    assert "must be greater than 0" in message.lower()

    mock_payment_gateway.refund_payment.assert_not_called()

def test_refund_late_fee_payment_zero_refund_amount():
    '''Test refunding late fee payment with a negative refund amount.'''
    fake_transaction_id = "txn_123456_1617181920"
    fake_refund_amount = 0.0
    mock_payment_gateway = Mock(spec=PaymentGateway)

    success, message = refund_late_fee_payment(
        transaction_id=fake_transaction_id,
        amount=fake_refund_amount,
        payment_gateway=mock_payment_gateway
    )

    assert success == False
    assert "must be greater than 0" in message.lower()

    mock_payment_gateway.refund_payment.assert_not_called()

def test_refund_late_fee_payment_exceeds_maximum_late_fee():
    '''Test refunding late fee payment that exceeds maximum late fee amount.'''
    fake_transaction_id = "txn_123456_1617181920"
    fake_refund_amount = 16.00
    mock_payment_gateway = Mock(spec=PaymentGateway)

    success, message = refund_late_fee_payment(
        transaction_id=fake_transaction_id,
        amount=fake_refund_amount,
        payment_gateway=mock_payment_gateway
    )

    assert success == False
    assert "exceeds maximum late fee" in message.lower()

    mock_payment_gateway.refund_payment.assert_not_called()

def test_refund_late_fee_payment_valid_refund(mocker):
    '''Test refunding late fee payment with valid inputs.'''

    fake_transaction_id = "txn_123456_1617181920"
    fake_refund_amount = 10.00
    mock_payment_gateway = Mock(spec=PaymentGateway)
    mock_payment_gateway.refund_payment.return_value = (True, f"Refund of ${fake_refund_amount:.2f} processed successfully. Refund ID: refund_{fake_transaction_id}_1617181921")

    success, message = refund_late_fee_payment(
        transaction_id=fake_transaction_id,
        amount=fake_refund_amount,
        payment_gateway=mock_payment_gateway
    )

    assert success == True
    assert f"refund of ${fake_refund_amount:.2f} processed successfully" in message.lower()

    mock_payment_gateway.refund_payment.assert_called_once()
    mock_payment_gateway.refund_payment.assert_called_with(fake_transaction_id, fake_refund_amount)

def test_refund_late_fee_payment_refund_gateway_error_failure(mocker):
    '''Test refunding late fee payment that fails.'''

    fake_transaction_id = "txn_123456_1617181920"
    fake_refund_amount = 10.00
    mock_payment_gateway = Mock(spec=PaymentGateway)
    mock_payment_gateway.refund_payment.return_value = (False, f"Refund of ${fake_refund_amount:.2f} failed.")
    # Note: all payment gateway failures are already protected by the method in library_service.py, so this failure case is slightly artificial.

    success, message = refund_late_fee_payment(
        transaction_id=fake_transaction_id,
        amount=fake_refund_amount,
        payment_gateway=mock_payment_gateway
    )

    assert success == False
    assert f"refund of ${fake_refund_amount:.2f} failed" in message.lower()

    mock_payment_gateway.refund_payment.assert_called_once()
    mock_payment_gateway.refund_payment.assert_called_with(fake_transaction_id, fake_refund_amount)
    
    pass

def test_refund_late_fee_payment_refund_exception_error(mocker):
    '''Test refunding late fee payment that encounters a processing error.'''

    fake_transaction_id = "txn_123456_1617181920"
    fake_refund_amount = 10.00
    mock_payment_gateway = Mock(spec=PaymentGateway)
    mock_payment_gateway.refund_payment.side_effect = Exception("network error")

    success, message = refund_late_fee_payment(
        transaction_id=fake_transaction_id,
        amount=fake_refund_amount,
        payment_gateway=mock_payment_gateway
    )

    assert success == False
    assert "refund processing error" in message.lower()

    mock_payment_gateway.refund_payment.assert_called_once()
    mock_payment_gateway.refund_payment.assert_called_with(fake_transaction_id, fake_refund_amount)