from robocorp.tasks import task
from robocorp import browser
from RPA.HTTP import HTTP
from RPA.Tables import Tables
from RPA.PDF import PDF
from RPA.Archive import Archive

# https://robocorp.com/docs-robot-framework/libraries/rpa-framework/rpa-tables
# https://robocorp.com/docs/courses/build-a-robot-python/create-order-process
@task
def order_robots_from_RobotSpareBin():
    browser.configure (
        slowmo=100,
    )
    """"
    The robot uses the .csv file to complete all the orders on the file.
    The robot gets the file by itself, no human input allowed.
    a PDF file of each HTML receipt should be saved. 
    a screenshot of each ordered robot should be saved.
    the screenshot should be embedded into the PDF receipt.
    a ZIP is to be created of the PDF receipts, one ZIP for all of the PDF files.
    The robot should complete the orders even if there are technical failures with the website.
    The robot should be available in public github repo, being possible to get up and running without manual setup.
    """
    open_robot_order_website()
    download_csv_file()
    handle_table()
    archive_receipts()
    
def open_robot_order_website():
    """"open the browser"""
    browser.goto("https://robotsparebinindustries.com/#/robot-order")

def download_csv_file():
    """"download the csv file"""
    http = HTTP()
    http.download(url="https://robotsparebinindustries.com/orders.csv", overwrite=True)
    
def csv_to_table():
    """create a table object from the csv"""
    table = Tables().read_table_from_csv(path="orders.csv")
    return table

def handle_table():
    """use the table to fille the form ()"""
    """submit all the data while at it"""
    table = csv_to_table()
    for i in table:
        close_annoying_modal()
        fill_the_form(i)
        submit_order(i)
        embed_screenshot_to_receipt(i['Order number'])
        
def close_annoying_modal():
    """press the button with label  'OK' """
    page = browser.page()
    page.click("button:text('OK')")

def fill_the_form(order_row : dict):
    """fill all the fields"""
    page = browser.page()
    page.select_option(selector='#head',value=order_row['Head'])
    page.check(selector=f"input[value='{order_row['Body']}']")
    page.fill(f"input[placeholder='Enter the part number for the legs']", order_row['Legs'])
    page.fill("#address",f"{order_row['Address']}")
    print(f"filled Head = {order_row['Head']} Body = {order_row['Body']} Legs = {order_row['Legs']} Address= {order_row['Address']}")

def submit_order(order_row):
    """submit order. if any alerts exist, try again and check for errors again."""
    """get ready for another order"""
    page = browser.page()
    screenshot_robot(order_row)
    page.click("#order")
    error = page.query_selector(".alert-danger")
    while (error):
        page.click("#order")
        error = page.query_selector(".alert-danger")
    store_receipt_As_pdf(order_row)
    page.click("#order-another")

def store_receipt_As_pdf(order_row : dict):
    page = browser.page()
    html = page.locator("#receipt").inner_html()

    pdf = PDF()
    pdf.html_to_pdf( html, f"output/receipts/receipt {order_row['Order number']}.pdf")

def screenshot_robot(order_row : dict):
    page = browser.page()
    page.click("#preview")
    page.query_selector("#robot-preview-image").screenshot(path=f"output/receipts/screenshots/screenshot{order_row['Order number']}.png")
    
def embed_screenshot_to_receipt( ordernumber : int):
    """add the screenshot to the pdf as a watermark"""
    """as to not to add an extra page and lots of empty space"""
    pdf = PDF()
    screenshot = f"output/receipts/screenshots/screenshot{ordernumber}.png"
    pdf_file = f"output/receipts/receipt {ordernumber}.pdf"

    pdf.add_watermark_image_to_pdf(
        image_path=screenshot,
        source_path=pdf_file ,
        output_path=f"output/picturedPdf/receipt{ordernumber}.pdf"
    )

def archive_receipts():
    archive = Archive()
    archive.archive_folder_with_zip(folder="output/picturedPdf/",archive_name="output/archived receipts.zip")
    print("zipattu")

# tähän jäin 15.3
# https://robocorp.com/docs/courses/build-a-robot-python/final-steps