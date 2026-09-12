import pandas as pd


class SimpleBacktest:
    """
    Backtesting simplu bazat pe semnale BUY/SELL/EXIT.
    """

    def __init__(self, df: pd.DataFrame, signals: pd.DataFrame, initial_capital: float = 10000):
        self.df = df.set_index("timestamp")
        self.signals = signals.set_index("timestamp")
        self.initial_capital = initial_capital

    def run(self) -> pd.DataFrame:
        capital = self.initial_capital
        position = 0  # 0 = flat, 1 = long, -1 = short
        entry = None
        entry_ts = None
        trades = []

        for ts, row in self.df.iterrows():
            if ts in self.signals.index:
                sig = self.signals.loc[ts]
                if sig["signal"] == "BUY" and position <= 0:
                    if position == -1:
                        # închide short
                        exit_price = row["close"]
                        pnl = (entry - exit_price)
                        capital += pnl
                        trades.append({
                            "entry_time": entry_ts,
                            "exit_time": ts,
                            "entry_price": entry,
                            "exit_price": exit_price,
                            "pnl": pnl,
                            "type": "SHORT",
                        })
                    position = 1
                    entry = row["close"]
                    entry_ts = ts

                elif sig["signal"] == "SELL" and position >= 0:
                    if position == 1:
                        # închide long
                        exit_price = row["close"]
                        pnl = (exit_price - entry)
                        capital += pnl
                        trades.append({
                            "entry_time": entry_ts,
                            "exit_time": ts,
                            "entry_price": entry,
                            "exit_price": exit_price,
                            "pnl": pnl,
                            "type": "LONG",
                        })
                    position = -1
                    entry = row["close"]
                    entry_ts = ts

                elif sig["signal"] == "EXIT" and position != 0:
                    exit_price = row["close"]
                    pnl = (exit_price - entry) * position
                    capital += pnl
                    trades.append({
                        "entry_time": entry_ts,
                        "exit_time": ts,
                        "entry_price": entry,
                        "exit_price": exit_price,
                        "pnl": pnl,
                        "type": "LONG" if position > 0 else "SHORT",
                    })
                    position = 0
                    entry = None
                    entry_ts = None

        # închide poziția rămasă la final
        if position != 0 and entry is not None:
            exit_price = self.df.iloc[-1]["close"]
            pnl = (exit_price - entry) * position
            capital += pnl
            trades.append({
                "entry_time": entry_ts,
                "exit_time": self.df.index[-1],
                "entry_price": entry,
                "exit_price": exit_price,
                "pnl": pnl,
                "type": "LONG" if position > 0 else "SHORT",
            })

        return pd.DataFrame(trades)
