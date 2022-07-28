import requests
from bs4 import BeautifulSoup
import json
from config import *
import argparse



def get_live_rates(page):
    soup = BeautifulSoup(page.content, "html.parser")
    forex_table = soup.find("table", class_="forextable").find("tbody")
    table_rows = forex_table.find_all("tr")
    currencies = dict()

    for row in table_rows:
        symbol, rate, name = get_currency_info(row)
        currencies[symbol] = {"rate": float(rate), "name": name}
    return currencies


def get_past_rates(filename):
    try:
        with open(filename, "r") as file:
            exchange_rates = json.load(file)
            return exchange_rates
    except IOError:
        return None


def get_currency_info(table_row):  # returns symbol, full currency name and conversion rate
    symbol = table_row.find("td", class_="currency").text
    rate = table_row.find("td", class_="spot number").find("span", class_="rate").text
    name = table_row.find("td", class_="alignLeft").find("a").text
    return (symbol, rate, name)


def get_currencies(url):
    page = requests.get(url)
    if page.status_code != 200:
        return get_past_rates()
    live_data = get_live_rates(page)
    with open(DATA_FILE, "w") as file: 
        json.dump(live_data, file, indent=4)  # Save data to use later without internet connection
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
    parser = argparse.ArgumentParser()
    parser.add_argument("--list", "-l", help="Display all availible exchange rates from EUR", action="store_true")
    options, _ = parser.parse_known_args()
    currencies = get_currencies(URL)
    if options.list:
        list_all(currencies)
    else:
        parser.add_argument("amount", type=int, nargs=1, help="Amount of from_currency to convert")
        parser.add_argument("from_currency", nargs=1, help="Currency from which to convert")
        parser.add_argument("to_currency", nargs='+', help="Currencies to which convert")
        args = parser.parse_args()

        from_currency = args.from_currency[0]
        amount = args.amount[0]
        
        for currency in args.to_currency:
            print(f"{amount} {from_currency} = {round(convert(currencies, from_currency, currency, amount), 5)} {currency}")

if __name__ == "__main__":
    main()