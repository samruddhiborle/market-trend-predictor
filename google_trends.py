from pytrends.request import TrendReq

def get_trend_score(keyword):

    try:

        pytrends = TrendReq(
            hl="en-US",
            tz=330
        )

        pytrends.build_payload(
            [keyword],
            timeframe="today 12-m"
        )

        data = pytrends.interest_over_time()

        if data.empty:
            return 50

        return int(data[keyword].mean())

    except Exception as e:

        print("Google Trends Error:", e)

        return 50