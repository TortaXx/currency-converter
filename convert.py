import requests
from bs4 import BeautifulSoup
import json
from config import *
import argparse
import sys



def get_live_rates(page):
    soup = BeautifulSoup(page.content, "html.parser")
    
    try:
        forex_table = soup.find("table", class_="forextable").find("tbody")
        forex_table_rows = forex_table.find_all("tr")
    except TypeError: # if find() is called on None
        print(f"No table of currencies found on {URL}\nPage strucure has possibly changed", file=sys.stderr)
        return None

    currencies = dict()
    
    for row in forex_table_rows:
        symbol, rate, name = get_currency_info(row)
        currencies[symbol] = {"rate": float(rate), "name": name}
    return currencies


def save_current_rates(rates, filename):
    try:
        with open(DATA_FILE, "w") as file: 
            json.dump(rates, file, indent=4)  # Save data to use later without internet connection
    except IOError:
        print(f"Error opening {DATA_FILE} to save current conversion rates for later use", file=sys.stderr)


def get_past_rates(filename):
    try:
        with open(filename, "r") as file:
            exchange_rates = json.load(file)
            return exchange_rates
    except IOError:
        print(f"Error opening {DATA_FILE} while getting saved rates from the past", file=sys.stderr)
        return None


def get_currency_info(table_row):  # returns symbol, full currency name and conversion rate
    symbol = table_row.find("td", class_="currency").text
    rate = table_row.find("td", class_="spot number").find("span", class_="rate").text
    name = table_row.find("td", class_="alignLeft").find("a").text
    return (symbol, rate, name)


def get_currencies(url):
    page = requests.get(url)
    if page.status_code != 200:
        print(f"{page.content}\nUsing saved rates from the past")
        return get_past_rates()
    live_data = get_live_rates(page)
    if live_data is None:
        return None
    
    save_current_rates(live_data, DATA_FILE)
    
    return live_data


def convert(currencies, from_currency, to_currency, amount):
    if from_currency != "EUR":
        amount /= currencies[from_currency]["rate"]
    if to_currency == "EUR":
        return amount
    return amount * currencies[to_currency]["rate"] # 1 in case to_currency is EUR


def list_all(currencies):
    for currency in currencies:
        print(f"1 {currency} ({currencies[currency]['name']}) = {currencies[currency]['rate']} EUR")


def main():
    # Has to be improved
    parser = argparse.ArgumentParser()
    parser.add_argument("--list", "-l", help="Display all availible exchange rates from EUR", action="store_true")
    
    parser.add_argument("--amount", "-n", type=int, nargs=1, help="Amount of from_currency to convert")
    parser.add_argument("--from-currency", "-f", nargs=1, help="Currency from which to convert")
    parser.add_argument("--to-currency", "-t", nargs='+', help="Currencies to which convert")
    
    options, _ = parser.parse_known_args()
    currencies = get_currencies(URL)
    if currencies is None:
        sys.exit(1)
    
    if options.list:
        list_all(currencies)
        sys.exit(0)

    if not options.amount or not options.from_currency or not options.to_currency:
        print("All of `--amount`, `--from-currency` and `to-currency` need to be specified")
        sys.exit(1)

    from_currency = options.from_currency[0]
    amount = options.amount[0]
    
    for currency in options.to_currency:
        print(f"{amount} {from_currency} = {round(convert(currencies, from_currency, currency, amount), 5)} {currency}")

if __name__ == "__main__":
    main()