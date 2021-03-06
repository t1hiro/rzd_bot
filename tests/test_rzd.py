import datetime

import rzd


def test_live():
    tomorrow = datetime.date.today() + datetime.timedelta(days=1)
    after_tomorrow = datetime.date.today() + datetime.timedelta(days=3)
    with rzd.RzdFetcher() as fetcher:
        train_list = fetcher.trains(
            'МОСКВА',
            'САНКТ-ПЕТЕРБУРГ',
            rzd.TimeRange(
                datetime.datetime(tomorrow.year, tomorrow.month,
                                  tomorrow.day,
                                  20, 0),
                datetime.datetime(after_tomorrow.year, after_tomorrow.month,
                                  after_tomorrow.day, 4, 0),
            )
        )
    assert isinstance(train_list, list)
    assert len(train_list) != 0
    available_seats = {
        s
        for t in train_list
        for s in t.seats.keys()
    }
    assert set() != available_seats