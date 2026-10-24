import yfinance as yf

tickers = yf.Tickers('msft aapl goog')

# access each ticker using (example)
msft_info = tickers.tickers['MSFT'].info
tickers.tickers['AAPL'].history(period="1mo")
goog_actions = tickers.tickers['GOOG'].actions

# websocket
tickers.live()
