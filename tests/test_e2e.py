from playwright.sync_api import Page, expect

def test_homepage_title(base_url, page: Page):
    server_url = base_url or "http://127.0.0.1:5000"
    page.goto(server_url)
    expect(page.get_by_role("heading", name="📚 Library Management System")).to_be_visible()
    
def test_add_book_to_catalog_playwright(base_url, page: Page):
    server_url = base_url or "http://127.0.0.1:5000"
    page.goto(f"{server_url}/catalog")
    page.get_by_role("link", name="➕ Add New Book").click()

    expect(page.get_by_role("heading", name="➕ Add New Book")).to_be_visible()

    page.get_by_role("textbox", name="Title *").click()
    page.get_by_role("textbox", name="Title *").fill("Playwright Book")
    page.get_by_role("textbox", name="Author *").click()
    page.get_by_role("textbox", name="Author *").fill("Playwright Author")
    page.get_by_role("textbox", name="ISBN *").click()
    page.get_by_role("textbox", name="ISBN *").fill("1234567891111")
    page.get_by_role("spinbutton", name="Total Copies *").click()
    page.get_by_role("spinbutton", name="Total Copies *").fill("4")
    page.get_by_role("button", name="Add Book to Catalog").click()

    expect(page.get_by_text("Book \"Playwright Book\" has been successfully added to the catalog.")).to_be_visible()
    expect(page.get_by_role("cell", name="Playwright Book")).to_be_visible()
    expect(page.get_by_role("cell", name="Playwright Author")).to_be_visible()
    expect(page.get_by_role("cell", name="1234567891111")).to_be_visible()
    expect(page.get_by_role("cell", name="/4 Available")).to_be_visible()

def test_borrow_and_return_book_playwright(base_url, page: Page):
    server_url = base_url or "http://127.0.0.1:5000"
    page.goto(f"{server_url}/catalog")
    page.get_by_role("row", name="4 Test Book 1 Test Author 1").get_by_placeholder("Patron ID (6 digits)").click()
    page.get_by_role("row", name="4 Test Book 1 Test Author 1").get_by_placeholder("Patron ID (6 digits)").fill("999999")
    page.get_by_role("cell", name="999999 Borrow").get_by_role("button").click()

    expect(page.get_by_text("Successfully borrowed \"Test Book 1\"")).to_be_visible()

    page.get_by_role("link", name="↩️ Return Book").click()
    page.get_by_role("textbox", name="Patron ID *").click()
    page.get_by_role("textbox", name="Patron ID *").fill("999999")
    page.get_by_role("spinbutton", name="Book ID *").click()
    page.get_by_role("spinbutton", name="Book ID *").fill("4")
    page.get_by_role("button", name="Process Return").click()

    expect(page.get_by_text("Successfully returned \"Test Book 1\"")).to_be_visible()