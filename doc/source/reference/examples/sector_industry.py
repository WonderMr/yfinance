import yfinance as yf

tech = yf.Sector('technology')
software = yf.Industry('software-infrastructure')

# Common information
key = tech.key
name = tech.name
symbol = tech.symbol
ticker = tech.ticker
overview = tech.overview
top_companies = tech.top_companies
research_reports = tech.research_reports

# Sector information
top_etfs = tech.top_etfs
top_mutual_funds = tech.top_mutual_funds
industries = tech.industries

# Industry information
sector_key = software.sector_key
sector_name = software.sector_name
top_performing_companies = software.top_performing_companies
top_growth_companies = software.top_growth_companies

