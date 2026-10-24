import yfinance as yf

dat = yf.Ticker("MSFT")

# get historical market data
dat.history(period='1mo')

# options
calls = dat.option_chain(dat.options[0]).calls

# get financials
balance_sheet = dat.balance_sheet
quarterly_income_stmt = dat.quarterly_income_stmt

# dates
calendar = dat.calendar

# general info
info = dat.info

# analysis
analyst_price_targets = dat.analyst_price_targets

# websocket
dat.live()
