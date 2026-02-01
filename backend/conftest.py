"""
Pytest configuration. Ensures TESTING=1 when running tests so auth is not validated
(middleware and get_current_user_id use TESTING_USER_ID when token missing).
Set TESTING=0 in env to enforce auth during tests.
"""
import os

os.environ.setdefault("TESTING", "true")
