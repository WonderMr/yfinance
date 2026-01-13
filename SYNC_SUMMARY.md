# Upstream Sync Summary

**Date**: 2026-01-13  
**Branch**: `upstream-sync`  
**Base commit**: `ea4dc2d` (common ancestor with ranaroussi/yfinance)  
**Commits synced**: 13 commits from upstream

## Successfully Integrated Changes

### Phase 1: Critical Bug Fixes ✅
- **b0cae4d**: Block curl_cffi version 0.14 (resolves major compatibility issues)
- **146a2a3**: Fix typo in industry column names
- **0b0b60e**: Add Swiss exchange to screener
- **bc67252**: Add industry field to EquityQuery
- **906d6f1**: Update screener querying logic and sector/industry mapping

### Phase 2: New Modules ✅
- **4f38ecf**: Redesign YfConfig with ConfigMgr class (network.proxy, network.retries, debug.hide_exceptions, debug.logging)
- **428919b**: Add new `yfinance/calendars.py` module
  - Earnings calendar
  - Economic events calendar
  - IPO info calendar
  - Splits calendar
  - Calendar query builder

### Phase 3: Multi/Tickers Updates ✅
- **fcb951b**: Changed default `period=None` in Tickers.history() and Tickers.download()

### Phase 4: Documentation Fixes ✅
- **ead4ed7, bc40e84**: Fix duplicate market reference in docs
- **5c7b41d**: Fix broken contributing link in PyPI docs
- **03ec05d**: Fix broken LICENSE.txt link in PyPI docs

### Phase 5: Module Exports ✅
- **e92386b**: Export `config` in `yfinance.__all__`

## Changes NOT Applied (Local Code Heavily Refactored)

The following upstream fixes target code sections that don't exist in our fork due to extensive local refactoring:

- **5d9f732**: Fix price-div-repair dropping NaN rows (history.py refactored)
- **bdb2fec**: Price repair nan guard (history.py refactored)
- **bd32769**: Bugfix for merging intraday with divs/splits (utils.safe_merge_dfs doesn't exist)
- **ebdfbb7**: Remove unnecessary exception raises in history() (history.py refactored)
- **7fba9cf**: Fix 30m interval alignment for NSE markets (history.py refactored)
- **4259760**: Fix internal parsing of epochs (utils._parse_user_dt doesn't exist)
- **441ae8d, 5a6efdf**: Add Ticker.get_earnings_dates() methods (base.py conflicts)
- **ec5f1c2**: Retry mechanism (already present in ConfigMgr)

## Testing Results

✅ **Import test**: All modules import successfully  
✅ **Utils tests**: Passed  
✅ **Screener tests**: Passed (3/3)  
✅ **Calendar tests**: Passed (5/5)  
⚠️ **Ticker tests**: Some failures unrelated to sync (IBM symbol issues)

## Files Modified

- `setup.py`: Added curl_cffi version constraint + kept pydantic
- `yfinance/__init__.py`: Added config export
- `yfinance/tickers.py`: Changed period default to None
- `yfinance/config.py`: NEW - ConfigMgr implementation
- `yfinance/calendars.py`: NEW - Calendar queries
- `yfinance/const.py`: Screener updates
- `yfinance/domain/industry.py`: Column name fix
- `yfinance/screener/`: Updated query logic
- `doc/`: Documentation fixes
- `tests/test_calendars.py`: NEW

## Next Steps

1. Review the `upstream-sync` branch
2. Merge into `main` when satisfied: `git merge upstream-sync`
3. Consider manually porting get_earnings_dates() methods if needed
4. Monitor for any issues from the refactored code paths
