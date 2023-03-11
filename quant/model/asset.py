class Asset():
    def __init__(self, account_id="", account_type=0, cash=-1, frozen_cash=-1, market_value=-1, total_asset=-1):
        self.account_id = account_id
        self.account_name = ""
        self.account_type = account_type
        self.cash = cash
        self.frozen_cash = frozen_cash
        self.market_value = market_value
        self.total_asset = total_asset
        self.initial_capital = -1
        self.fpnl=0