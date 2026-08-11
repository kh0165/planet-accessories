import os

import gspread

from google.oauth2.service_account import Credentials

from django.conf import settings


SCOPES = [
    "https://www.googleapis.com/auth/spreadsheets",
    "https://www.googleapis.com/auth/drive",
]


def get_google_sheet():

    credentials_path = os.path.join(
        settings.BASE_DIR,
        "credentials",
        "google-sheet.json",
    )

    credentials = Credentials.from_service_account_file(
        credentials_path,
        scopes=SCOPES,
    )

    client = gspread.authorize(credentials)

    spreadsheet = client.open(
        "planet-accessories"
    )

    worksheet = spreadsheet.sheet1

    return worksheet

def add_order_to_google_sheet(order):

    worksheet = get_google_sheet()

    products = []

    for item in order.items.all():

        products.append(
            f"{item.product.name} x {item.quantity}"
        )

    products_text = ", ".join(products)

    worksheet.append_row([
        order.id,
        order.created_at.strftime("%Y-%m-%d %H:%M"),
        order.name,
        order.phone,
        order.city,
        order.address,
        products_text,
        str(order.total),
        str(order.deposit),
        order.get_payment_status_display(),
    ])

def update_order_in_google_sheet(order):

    worksheet = get_google_sheet()

    records = worksheet.get_all_records()

    for row_number, row in enumerate(records, start=2):

        if str(row.get("Order ID")) == str(order.id):

            worksheet.update_cell(
                row_number,
                10,
                order.get_payment_status_display()
            )

            return