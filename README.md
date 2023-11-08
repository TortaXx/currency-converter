# Currency converter

CLI tool for conversion between 30 currencies.
Conversion rates are obtained from European Central Bank

## Usage

```
python convert.py -f <from-currency> -t <target-currencies> -n <amount>
```

or
```
python convert.py --from-currency <from-currency> --to-currency <target-currencies> --amount <amount>
```

#### Example Usage:
To convert 30 Philippine pesos to US dollars and Swiss francs:

`python convert.py -f PHP -t USD CHF BRL -n 30`



#### Other commands:
- `python convert.py -h` to display help
- `python convert.py -l` to list all available currencies with their conversion rates