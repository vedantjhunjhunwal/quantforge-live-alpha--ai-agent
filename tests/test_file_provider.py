import pandas as pd
from quantforge.providers.file_provider import FileMarketDataProvider


def test_file_provider_loads_real_user_data(tmp_path):
    path = tmp_path / "m.csv"
    pd.DataFrame({
        "timestamp": ["2024-01-01", "2024-01-02"],
        "symbol": ["AAA", "AAA"],
        "open": [1, 2],
        "high": [1, 2],
        "low": [1, 2],
        "close": [1, 2],
        "volume": [100, 200],
    }).to_csv(path, index=False)
    df = FileMarketDataProvider(str(path), "csv").fetch()
    assert len(df) == 2
