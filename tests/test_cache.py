"""
Tests for cache

To run all tests in suite from commandline:
   python -m unittest tests.cache

Specific test class:
   python -m unittest tests.cache.TestCache

"""
from tests.context import yfinance as yf

import unittest
import tempfile
import os
import sqlite3


class TestCache(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.tempCacheDir = tempfile.TemporaryDirectory()
        yf.set_tz_cache_location(cls.tempCacheDir.name)

    @classmethod
    def tearDownClass(cls):
        yf.cache._TzDBManager.close_db()
        cls.tempCacheDir.cleanup()

    def test_storeTzNoRaise(self):
        # storing TZ to cache should never raise exception
        tkr = 'AMZN'
        tz1 = "America/New_York"
        tz2 = "London/Europe"
        cache = yf.cache.get_tz_cache()
        cache.store(tkr, tz1)
        cache.store(tkr, tz2)

    def test_setTzCacheLocation(self):
        self.assertEqual(yf.cache._TzDBManager.get_location(), self.tempCacheDir.name)

        tkr = 'AMZN'
        tz1 = "America/New_York"
        cache = yf.cache.get_tz_cache()
        cache.store(tkr, tz1)

        self.assertTrue(os.path.exists(os.path.join(self.tempCacheDir.name, "tkr-tz.db")))


class TestCacheMigration(unittest.TestCase):
    def test_old_cache_schema_upgrade(self):
        tmp_dir = tempfile.TemporaryDirectory()
        try:
            # Create legacy cache DB without updated_at column
            db_path = os.path.join(tmp_dir.name, "tkr-tz.db")
            conn = sqlite3.connect(db_path)
            conn.execute("CREATE TABLE _tz_kv (key TEXT PRIMARY KEY, value TEXT)")
            conn.execute(
                "INSERT INTO _tz_kv (key, value) VALUES (?, ?)",
                ("AAPL", "America/New_York"),
            )
            conn.commit()
            conn.close()

            # Point cache to legacy DB and force reinitialisation
            yf.set_tz_cache_location(tmp_dir.name)
            yf.cache._TzCacheManager._tz_cache = None
            cache = yf.cache.get_tz_cache()

            # Lookup should succeed and return the existing value
            self.assertEqual(cache.lookup("AAPL"), "America/New_York")

            # Storing a value should still succeed and be retrievable
            cache.store("AAPL", "America/New_York")
            self.assertEqual(cache.lookup("AAPL"), "America/New_York")
        finally:
            yf.cache._TzDBManager.close_db()
            tmp_dir.cleanup()


if __name__ == '__main__':
    unittest.main()
