from datetime import timedelta

from app.timeutil import app_now, app_zone, mariadb_time_zone_offset


def test_app_timezone_is_gmt_plus_7():
    assert str(app_zone()) == "Asia/Jakarta"
    assert mariadb_time_zone_offset() == "+07:00"
    now = app_now()
    # naive local; within a few minutes of Asia/Jakarta wall clock
    aware = now.replace(tzinfo=app_zone())
    assert aware.utcoffset() == timedelta(hours=7)
