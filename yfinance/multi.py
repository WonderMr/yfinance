#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
# yfinance - market data downloader
# https://github.com/ranaroussi/yfinance
#
# Copyright 2017-2019 Ran Aroussi
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
#

from __future__ import print_function

import logging
import os
import traceback
import warnings
from concurrent.futures import ThreadPoolExecutor, as_completed
from typing import Union

import pandas as _pd
from curl_cffi import requests

from . import Ticker, shared, utils
from .const import _SENTINEL_
from .data import YfData
from .config import YfConfig


@utils.log_indent_decorator
def download(
    tickers,
    start=None,
    end=None,
    actions=False,
    threads=True,
    ignore_tz=None,
    group_by="column",
    auto_adjust=None,
    back_adjust=False,
    repair=False,
    keepna=False,
    progress=True,
    period=None,
    interval="1d",
    prepost=False,
    proxy=_SENTINEL_,
    rounding=False,
    timeout=10,
    session=None,
    multi_level_index=True,
    _retry=True,
) -> Union[_pd.DataFrame, None]:
    """
    Download yahoo tickers
    :Parameters:
        tickers : str, list
            List of tickers to download
        period : str
            Valid periods: 1d,5d,1mo,3mo,6mo,1y,2y,5y,10y,ytd,max
            Default: 1mo
            Either Use period parameter or use start and end
        interval : str
            Valid intervals: 1m,2m,5m,15m,30m,60m,90m,1h,1d,5d,1wk,1mo,3mo
            Intraday data cannot extend last 60 days
        start: str
            Download start date string (YYYY-MM-DD) or _datetime, inclusive.
            Default is 99 years ago
            E.g. for start="2020-01-01", the first data point will be on "2020-01-01"
        end: str
            Download end date string (YYYY-MM-DD) or _datetime, exclusive.
            Default is now
            E.g. for end="2023-01-01", the last data point will be on "2022-12-31"
        group_by : str
            Group by 'ticker' or 'column' (default)
        prepost : bool
            Include Pre and Post market data in results?
            Default is False
        auto_adjust: bool
            Adjust all OHLC automatically? Default is True
        repair: bool
            Detect currency unit 100x mixups and attempt repair
            Default is False
        keepna: bool
            Keep NaN rows returned by Yahoo?
            Default is False
        actions: bool
            Download dividend + stock splits data. Default is False
        threads: bool / int
            How many threads to use for mass downloading. Default is True
        ignore_tz: bool
            When combining from different timezones, ignore that part of datetime.
            Default depends on interval. Intraday = False. Day+ = True.
        rounding: bool
            Optional. Round values to 2 decimal places?
        timeout: None or float
            If not None stops waiting for a response after given number of
            seconds. (Can also be a fraction of a second e.g. 0.01)
        session: None or Session
            Optional. Pass your own session object to be used for all requests
        multi_level_index: bool
            Optional. Always return a MultiIndex DataFrame? Default is True
    """
    logger = utils.get_yf_logger()
    session = session or requests.Session(impersonate="chrome")

    # Ensure data initialised with session.
    if proxy is not _SENTINEL_:
        warnings.warn(
            "Set proxy via new config function: yf.set_config(proxy=proxy)",
            DeprecationWarning,
            stacklevel=3,
        )
        YfData(proxy=proxy)
    YfData(session=session)

    if auto_adjust is None:
        # Warn users that default has changed to True
        warnings.warn(
            "YF.download() has changed argument auto_adjust default to True",
            FutureWarning,
            stacklevel=3,
        )
        auto_adjust = True

    YfData(session=session)
    if logger.isEnabledFor(logging.DEBUG):
        if threads:
            # With DEBUG, each thread generates a lot of log messages.
            # And with multi-threading, these messages will be interleaved, bad!
            # So disable multi-threading to make log readable.
            logger.debug("Disabling multithreading because DEBUG logging enabled")
            threads = False
        if progress:
            # Disable progress bar, interferes with display of log messages
            progress = False

    if ignore_tz is None:
        # Set default value depending on interval
        if interval[-1] in ["m", "h"]:
            # Intraday
            ignore_tz = False
        else:
            ignore_tz = True

    # create ticker list
    tickers = (
        tickers
        if isinstance(tickers, (list, set, tuple))
        else tickers.replace(",", " ").split()
    )

    # accept isin as ticker
    with shared._ISINS_LOCK:
        shared._ISINS = {}
    _tickers_ = []
    for ticker in tickers:
        if utils.is_isin(ticker):
            isin = ticker
            ticker = utils.get_ticker_by_isin(ticker)
            with shared._ISINS_LOCK:
                shared._ISINS[ticker] = isin
        _tickers_.append(ticker)

    tickers = _tickers_

    tickers = list(dict.fromkeys([ticker.upper() for ticker in tickers]))

    if progress:
        with shared._PROGRESS_BAR_LOCK:
            shared._PROGRESS_BAR = utils.ProgressBar(len(tickers), "completed")

    # reset shared structures
    with shared._DFS_LOCK:
        shared._DFS = {}
    with shared._ERRORS_LOCK:
        shared._ERRORS = {}
    with shared._TRACEBACKS_LOCK:
        shared._TRACEBACKS = {}

    # download using threads
    if threads:
        if threads is True:
            threads = min([len(tickers), (os.cpu_count() or 1) * 2])
        futures = {}
        with ThreadPoolExecutor(max_workers=threads) as executor:
            for ticker in tickers:
                futures[
                    executor.submit(
                        _download_one_threaded,
                        ticker,
                        start=start,
                        end=end,
                        auto_adjust=auto_adjust,
                        back_adjust=back_adjust,
                        repair=repair,
                        actions=actions,
                        period=period,
                        interval=interval,
                        prepost=prepost,
                        rounding=rounding,
                        keepna=keepna,
                        timeout=timeout,
                    )
                ] = ticker
            for future in as_completed(futures):
                ticker = futures[future]
                try:
                    data = future.result()
                    with shared._DFS_LOCK:
                        shared._DFS[ticker.upper()] = data
                except Exception as e:
                    with shared._DFS_LOCK:
                        shared._DFS[ticker.upper()] = utils.empty_df()
                    with shared._ERRORS_LOCK:
                        shared._ERRORS[ticker.upper()] = repr(e)
                    with shared._TRACEBACKS_LOCK:
                        shared._TRACEBACKS[ticker.upper()] = traceback.format_exc()
    # download synchronously
    else:
        for ticker in tickers:
            try:
                data = _download_one(
                    ticker,
                    period=period,
                    interval=interval,
                    start=start,
                    end=end,
                    prepost=prepost,
                    actions=actions,
                    auto_adjust=auto_adjust,
                    back_adjust=back_adjust,
                    repair=repair,
                    keepna=keepna,
                    rounding=rounding,
                    timeout=timeout,
                    _retry=_retry,
                )
                with shared._DFS_LOCK:
                    shared._DFS[ticker.upper()] = data
            except Exception as e:
                with shared._DFS_LOCK:
                    shared._DFS[ticker.upper()] = utils.empty_df()
                with shared._ERRORS_LOCK:
                    shared._ERRORS[ticker.upper()] = repr(e)
                with shared._TRACEBACKS_LOCK:
                    shared._TRACEBACKS[ticker.upper()] = traceback.format_exc()
            if progress:
                with shared._PROGRESS_BAR_LOCK:
                    shared._PROGRESS_BAR.animate()

    if progress:
        with shared._PROGRESS_BAR_LOCK:
            shared._PROGRESS_BAR.completed()

    with shared._ERRORS_LOCK:
        errors_copy = shared._ERRORS.copy()
    if errors_copy:
        # Send errors to logging module
        logger = utils.get_yf_logger()
        logger.error(
            "\n%.f Failed download%s:"
            % (len(errors_copy), "s" if len(errors_copy) > 1 else "")
        )

        # Log each distinct error once, with list of symbols affected
        errors = {}
        for ticker in errors_copy:
            err = errors_copy[ticker]
            err = err.replace(f"${ticker}: ", "")
            if err not in errors:
                errors[err] = [ticker]
            else:
                errors[err].append(ticker)
        for err in errors.keys():
            logger.error(f"{errors[err]}: " + err)

        # Log each distinct traceback once, with list of symbols affected
        with shared._TRACEBACKS_LOCK:
            tbs_copy = shared._TRACEBACKS.copy()
        tbs = {}
        for ticker in tbs_copy:
            tb = tbs_copy[ticker]
            tb = tb.replace(f"${ticker}: ", "")
            if tb not in tbs:
                tbs[tb] = [ticker]
            else:
                tbs[tb].append(ticker)
        for tb in tbs.keys():
            logger.debug(f"{tbs[tb]}: " + tb)

    if ignore_tz:
        with shared._DFS_LOCK:
            for tkr in shared._DFS.keys():
                if (shared._DFS[tkr] is not None) and (shared._DFS[tkr].shape[0] > 0):
                    shared._DFS[tkr].index = shared._DFS[tkr].index.tz_localize(None)

    try:
        # ───────────────────────────────
        # 1. Logging before concat
        # ───────────────────────────────
        with shared._DFS_LOCK:  # already hold same lock as concat
            for (
                tkr,
                df_single,
            ) in shared._DFS.items():  # iterate over all saved DataFrames
                if df_single is not None and not df_single.empty:
                    utils._df_stats("BEFORE_CONCAT", df_single, tkr)
                else:
                    utils.get_yf_logger().debug(f"{tkr}: BEFORE_CONCAT: df EMPTY")

        # ───────────────────────────────
        # 2. _pd.concat(...)
        # ───────────────────────────────
        data = _pd.concat(
            shared._DFS.values(),  # all DataFrames
            axis=1,  # concatenate by columns
            sort=True,
            keys=shared._DFS.keys(),  # top level of MultiIndex = ticker
            names=["Ticker", "Price"],
        )

        # ───────────────────────────────
        # 3. Logging after concat
        # ───────────────────────────────
        # data now has MultiIndex columns (Ticker → Price fields).
        for tkr in data.columns.levels[0]:  # top level is list of tickers
            df_slice = data[tkr]  # ticker slice ("sub-DataFrame")
            # df_slice is still a DataFrame: columns Open/High/Low/Close/...
            utils._df_stats("AFTER_CONCAT", df_slice, tkr)

    except Exception:
        _realign_dfs()
        with shared._DFS_LOCK:
            data = _pd.concat(
                shared._DFS.values(),
                axis=1,
                sort=True,
                keys=shared._DFS.keys(),
                names=["Ticker", "Price"],
            )
    data.index = _pd.to_datetime(data.index, utc=not ignore_tz)
    # switch names back to isins if applicable
    with shared._ISINS_LOCK:
        data.rename(columns=shared._ISINS, inplace=True)

    if group_by == "column":
        data.columns = data.columns.swaplevel(0, 1)
        data.sort_index(level=0, axis=1, inplace=True)

    if not multi_level_index and len(tickers) == 1:
        data = data.droplevel(0 if group_by == "ticker" else 1, axis=1).rename_axis(
            None, axis=1
        )

    return data


def _realign_dfs():
    idx_len = 0
    idx = None

    with shared._DFS_LOCK:
        for df in shared._DFS.values():
            if len(df) > idx_len:
                idx_len = len(df)
                idx = df.index

        for key in shared._DFS.keys():
            try:
                shared._DFS[key] = _pd.DataFrame(
                    index=idx, data=shared._DFS[key]
                ).drop_duplicates()
            except Exception:
                shared._DFS[key] = _pd.concat(
                    [utils.empty_df(idx), shared._DFS[key].dropna()], axis=0, sort=True
                )

            # remove duplicate index
            shared._DFS[key] = shared._DFS[key].loc[
                ~shared._DFS[key].index.duplicated(keep="last")
            ]


def _download_one(
    ticker,
    start=None,
    end=None,
    auto_adjust=False,
    back_adjust=False,
    repair=False,
    actions=False,
    period="max",
    interval="1d",
    prepost=False,
    rounding=False,
    keepna=False,
    timeout=10,
    _retry=True,
):
    data = Ticker(ticker).history(
        period=period,
        interval=interval,
        start=start,
        end=end,
        prepost=prepost,
        actions=actions,
        auto_adjust=auto_adjust,
        back_adjust=back_adjust,
        repair=repair,
        rounding=rounding,
        keepna=keepna,
        timeout=timeout,
        raise_errors=True,
        _retry=_retry,
    )

    return data


def _download_one_threaded(
    ticker,
    start=None,
    end=None,
    auto_adjust=False,
    back_adjust=False,
    repair=False,
    actions=False,
    period="max",
    interval="1d",
    prepost=False,
    rounding=False,
    keepna=False,
    timeout=10,
    _retry=True,
):
    try:
        return _download_one(
            ticker,
            start=start,
            end=end,
            auto_adjust=auto_adjust,
            back_adjust=back_adjust,
            repair=repair,
            actions=actions,
            period=period,
            interval=interval,
            prepost=prepost,
            rounding=rounding,
            keepna=keepna,
            timeout=timeout,
            _retry=_retry,
        )
    finally:
        if shared._PROGRESS_BAR is not None:
            with shared._PROGRESS_BAR_LOCK:
                shared._PROGRESS_BAR.animate()
