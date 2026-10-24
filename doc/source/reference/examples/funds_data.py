import yfinance as yf

spy = yf.Ticker('SPY')
data = spy.funds_data

# show fund description
description = data.description

# show operational information
fund_overview = data.fund_overview
fund_operations = data.fund_operations

# show holdings related information
asset_classes = data.asset_classes
top_holdings = data.top_holdings
equity_holdings = data.equity_holdings
bond_holdings = data.bond_holdings
bond_ratings = data.bond_ratings
sector_weightings = data.sector_weightings
