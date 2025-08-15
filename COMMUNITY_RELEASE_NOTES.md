# Community Release Notes

## Overview
This release includes code quality improvements and internationalization updates for the yfinance library.

## Changes Made

### 1. Code Internationalization
- **File**: `yfinance/multi.py`
- **Change**: Translated Russian comments to English
- **Impact**: Improves code accessibility for international contributors

### 2. Code Formatting
- **Files**: `yfinance/multi.py`, `yfinance/scrapers/history.py`, `yfinance/utils.py`
- **Changes**:
  - Applied Black formatting for consistent code style
  - Applied isort for proper import ordering
  - Unified string quotes throughout the codebase
- **Impact**: Better code readability and maintainability

### 3. Code Cleanup
- **File**: `yfinance/utils.py`
- **Change**: Removed unused `canonical_names` set from `_df_stats()` function
- **Impact**: Cleaner, more maintainable code

## Security Review
✅ **No private or sensitive data found**:
- No API keys, tokens, or credentials
- No internal/private URLs
- Only uses public Yahoo Finance APIs
- All changes are cosmetic (formatting and comments)

## Testing
- All changes are non-functional (formatting and comments only)
- Public API remains unchanged
- No breaking changes introduced

## Compatibility
- Fully backward compatible
- No changes to public interfaces
- No new dependencies added

## License
The project maintains its Apache 2.0 License and includes appropriate disclaimers about Yahoo Finance usage.

## Ready for Community
This code is ready for community release with:
- Clean, well-formatted code
- English-only comments
- No private/proprietary information
- Improved maintainability