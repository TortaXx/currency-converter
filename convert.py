import requests
from bs4 import BeautifulSoup
import json
from config import *



def get_live_rates(page):
    soup = BeautifulSoup(page.content, "html.parser")
    forex_table = soup.find("table", class_="forextable").find("tbody")
    table_rows = forex_table.find_all("tr")
    exchange_rates = dict()

    for row in table_rows:
        symbol, rate = get_currency_info(row)
        exchange_rates[symbol] = float(rate)
    return exchange_rates


def get_past_rates(filename):
    try:
        with open(filename, "r") as file:
            exchange_rates = json.load(file)
            return exchange_rates
    except IOError:
        return None


def get_currency_info(table_row):  # returns full currency name, symbol and conversion rate
    symbol = table_row.find("td", class_="currency").text
    rate = table_row.find("td", class_="spot number").find("span", class_="rate").text
    return (symbol, rate)


def get_rates(url):
    page = requests.get(url)
    if page.status_code != 200:
        return get_past_rates()
    live_data = get_live_rates(page)
    with open(DATA_FILE, "w") as file: 
        json.dump(live_data, file, indent=4)  # Save data to use later without internet connection
    return live_data


def convert(rates, from_currency, to_currency, amount):
    if from_currency != "EUR":
        amount /= rates[from_currency]
        from_currency = "EUR"
    return amount * rates.get(to_currency, 1) # 1 in case to_currency is EUR
