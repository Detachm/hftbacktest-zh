import warnings
from abc import ABC, abstractmethod
from typing import Mapping, Dict, Any

import polars as pl
import numpy as np
from .utils import get_total_days, get_num_samples_per_day


class Metric(ABC):
    """
    用于计算策略绩效指标的基类。继承该基类实现自定义指标后，可以在 :class:`Stats`
    中计算该指标，并在 summary 中展示。
    """
    @abstractmethod
    def compute(self, df: pl.DataFrame, context: Dict[str, Any]) -> Mapping[str, Any]:
        """
        Args:
            df: 包含策略状态记录的 Polars :class:`DataFrame <pl.DataFrame>`。
            context: 已计算指标或其他值组成的字典。

        Returns:
            字典，键为指标名称，值为计算得到的指标值。
        """
        raise NotImplementedError


class Ret(Metric):
    """
    收益。

    Parameters:
        name: 指标名称。默认值为 `Return`。
        book_size: 如果设置 book size 或资金分配额，则该指标会除以 book size，
                   表示为 book size 的百分比；否则使用原始单位。
    """

    def __init__(self, name: str = None, book_size: float | None = None):
        self.name = name if name is not None else 'Return'
        self.book_size = book_size

    def compute(self, df: pl.DataFrame, context: Dict[str, Any]) -> Mapping[str, Any]:
        equity = (df['equity_wo_fee'] - df['fee']).drop_nans()
        pnl = equity[-1] - equity[0]

        if self.book_size is not None:
            pnl /= self.book_size

        return {self.name: pnl}


class AnnualRet(Ret):
    """
    年化收益。

    Parameters:
        name: 指标名称。默认值为 `AnnualReturn`。
        book_size: 如果设置 book size 或资金分配额，则该指标会除以 book size，
                   表示为 book size 的百分比；否则使用原始单位。
        trading_days_per_year: 用于年化的每年交易日数量。Trad-Fi 通常使用 252，
                               因此默认值为 252。对于 24/7 运行的加密货币市场，也可以使用 365。
    """

    def __init__(self, name: str = None, book_size: float | None = None, trading_days_per_year: float = 252):
        super().__init__(
            name if name is not None else 'AnnualReturn',
            book_size
        )
        self.trading_days_per_year = trading_days_per_year

    def compute(self, df: pl.DataFrame, context: Dict[str, Any]) -> Mapping[str, Any]:
        pnl = super().compute(df, context)[self.name]
        pnl = pnl / get_total_days(df['timestamp']) * self.trading_days_per_year
        return {self.name: pnl}


class SR(Metric):
    """
    不考虑 benchmark 的 Sharpe Ratio。

    Parameters:
        name: 指标名称。默认值为 `SR`。
        trading_days_per_year: 用于年化的每年交易日数量。Trad-Fi 通常使用 252，
                               因此默认值为 252。对于 24/7 运行的加密货币市场，也可以使用 365。
                               另外，计算日度 Sharpe Ratio 时还会乘以
                               `sqrt(每日样本数)`，因此结果会受采样间隔影响。
    """

    def __init__(self, name: str = None, trading_days_per_year: float = 252):
        self.name = name if name is not None else 'SR'
        self.trading_days_per_year = trading_days_per_year

    def compute(self, df: pl.DataFrame, context: Dict[str, Any]) -> Mapping[str, Any]:
        equity = df['equity_wo_fee'] - df['fee']

        pnl = equity.diff()
        c = get_num_samples_per_day(df['timestamp']) * self.trading_days_per_year

        with np.errstate(divide='ignore'):
            return {self.name: np.divide(pnl.drop_nans().mean(), pnl.drop_nans().std()) * np.sqrt(c)}


class Sortino(Metric):
    """
    不考虑 benchmark 的 Sortino Ratio。

    Parameters:
        name: 指标名称。默认值为 `Sortino`。
        trading_days_per_year: 用于年化的每年交易日数量。Trad-Fi 通常使用 252，
                               因此默认值为 252。对于 24/7 运行的加密货币市场，也可以使用 365。
                               另外，计算日度指标时还会乘以 `sqrt(每日样本数)`，
                               因此结果会受采样间隔影响。
    """

    def __init__(self, name=None, trading_days_per_year: float = 252):
        self.name = name if name is not None else 'Sortino'
        self.trading_days_per_year = trading_days_per_year

    def compute(self, df: pl.DataFrame, context: Dict[str, Any]) -> Mapping[str, Any]:
        equity = df['equity_wo_fee'] - df['fee']

        pnl = equity.diff()
        c = get_num_samples_per_day(df['timestamp']) * self.trading_days_per_year

        dr = np.sqrt((np.minimum(0, pnl) ** 2).drop_nans().mean())
        with np.errstate(divide='ignore'):
            return {self.name: np.divide(pnl.drop_nans().mean(), dr) * np.sqrt(c)}


class ReturnOverMDD(Metric):
    """
    收益与最大回撤之比。

    Parameters:
        name: 指标名称。默认值为 `ReturnOverMDD`。
    """

    def __init__(self, name: str = None):
        self.name = (
            name if name is not None else 'ReturnOverMDD'
        )

    def compute(self, df: pl.DataFrame, context: Dict[str, Any]) -> Mapping[str, Any]:
        ret = Ret().compute(df, context)['Return']
        mdd = MaxDrawdown().compute(df, context)['MaxDrawdown']
        return {self.name: np.divide(ret, mdd)}


class ReturnOverTrade(Metric):
    """
    收益与成交额之比，表示单位成交额产生的利润，例如 `$profit / $trading_value`。

    Parameters:
        name: 指标名称。默认值为 `ReturnOverTrade`。
    """

    def __init__(self, name: str = None):
        self.name = name if name is not None else 'ReturnOverTrade'

    def compute(self, df: pl.DataFrame, context: Dict[str, Any]) -> Mapping[str, Any]:
        ret = Ret().compute(df, context)['Return']
        trade_volume = TradingValue().compute(df, context)['TradingValue']
        return {self.name: np.divide(ret, trade_volume)}


class MaxDrawdown(Metric):
    """
    最大回撤。

    Parameters:
        name: 指标名称。默认值为 `MaxDrawdown`。
        book_size: 如果设置 book size 或资金分配额，则该指标会除以 book size，
                   表示为 book size 的百分比；否则使用原始单位。
    """

    def __init__(self, name: str = None, book_size: float | None = None):
        self.name = name if name is not None else 'MaxDrawdown'
        self.book_size = book_size

    def compute(self, df: pl.DataFrame, context: Dict[str, Any]) -> Mapping[str, Any]:
        equity = df['equity_wo_fee'] - df['fee']

        max_equity = equity.cum_max()
        dd = equity - max_equity

        if self.book_size is not None:
            dd /= self.book_size

        return {self.name: abs(dd.min())}


class NumberOfTrades(Metric):
    """
    计算总成交次数。

    Parameters:
        name: 指标名称。默认值为 `NumberOfTrades`。
    """

    def __init__(self, name: str = None):
        self.name = name if name is not None else 'NumberOfTrades'

    def compute(self, df: pl.DataFrame, context: Dict[str, Any]) -> Mapping[str, Any]:
        num_trades = df['num_trades_'].sum()
        return {self.name: num_trades}


class DailyNumberOfTrades(NumberOfTrades):
    """
    计算日均成交次数。
    
    Parameters:
        name: 指标名称。默认值为 `DailyNumberOfTrades`。
    """

    def __init__(self, name: str = None):
        super().__init__(name if name is not None else 'DailyNumberOfTrades')

    def compute(self, df: pl.DataFrame, context: Dict[str, Any]) -> Mapping[str, Any]:
        num_trades = super().compute(df, context)[self.name]
        num_trades /= get_total_days(df['timestamp'])
        return {self.name: num_trades}


class TradingVolume(Metric):
    """
    计算总成交量，即成交的股票或合约数量。

    Parameters:
        name: 指标名称。默认值为 `TradingVolume`。
    """

    def __init__(self, name: str = None):
        self.name = name if name is not None else 'TradingVolume'

    def compute(self, df: pl.DataFrame, context: Dict[str, Any]) -> Mapping[str, Any]:
        trading_volume = df['trading_volume_'].sum()
        return {self.name: trading_volume}


class DailyTradingVolume(TradingVolume):
    """
    计算日均成交量，即每日成交的股票或合约数量。

    Parameters:
        name: 指标名称。默认值为 `DailyTradingVolume`。
    """

    def __init__(self, name: str = None):
        super().__init__(name if name is not None else 'DailyTradingVolume')

    def compute(self, df: pl.DataFrame, context: Dict[str, Any]) -> Mapping[str, Any]:
        trading_volume = super().compute(df, context)[self.name]
        trading_volume /= get_total_days(df['timestamp'])
        return {self.name: trading_volume}


class TradingValue(Metric):
    """
    计算总成交额；如果提供 book size，也可表示为成交额除以 book size 得到的 turnover。

    Parameters:
        name: 指标名称。默认值为 `TradingValue`；如果提供 book_size，则默认值为 `Turnover`。
        book_size: 如果设置 book size 或资金分配额，则该指标会除以 book size，
                   表示为 book size 的百分比；否则使用原始单位。
    """

    def __init__(self, name: str = None, book_size: float | None = None):
        self.name = (
            name if name is not None else ('TradingValue' if book_size is None else 'Turnover')
        )
        self.book_size = book_size

    def compute(self, df: pl.DataFrame, context: Dict[str, Any]) -> Mapping[str, Any]:
        trading_value = df['trading_value_'].sum()
        if self.book_size is not None:
            trading_value /= self.book_size
        return {self.name: trading_value}


class DailyTradingValue(TradingValue):
    """
    计算日均成交额；如果提供 book size，也可表示为日均成交额除以 book size 得到的日均 turnover。

    Parameters:
        name: 指标名称。默认值为 `DailyTradingValue`；如果提供 book_size，则默认值为 `DailyTurnover`。
        book_size: 如果设置 book size 或资金分配额，则该指标会除以 book size，
                   表示为 book size 的百分比；否则使用原始单位。
    """

    def __init__(self, name: str = None, book_size: float | None = None):
        super().__init__(
            name if name is not None else ('DailyTradingValue' if book_size is None else 'DailyTurnover'),
            book_size
        )

    def compute(self, df: pl.DataFrame, context: Dict[str, Any]) -> Mapping[str, Any]:
        trading_value = super().compute(df, context)[self.name]
        trading_value /= get_total_days(df['timestamp'])
        return {self.name: trading_value}


class MaxPositionValue(Metric):
    """
    计算最大未平仓 position value。

    Parameters:
        name: 指标名称。默认值为 `MaxPositionValue`。
    """

    def __init__(self, name: str = None):
        self.name = name if name is not None else 'MaxPositionValue'

    def compute(self, df: pl.DataFrame, context: Dict[str, Any]) -> Mapping[str, Any]:
        return {self.name: (df['position'].abs() * df['price']).max()}


class MeanPositionValue(Metric):
    """
    计算平均未平仓 position value。

    Parameters:
        name: 指标名称。默认值为 `MeanPositionValue`。
    """

    def __init__(self, name: str = None):
        self.name = name if name is not None else 'MeanPositionValue'

    def compute(self, df: pl.DataFrame, context: Dict[str, Any]) -> Mapping[str, Any]:
        return {self.name: (df['position'].abs() * df['price']).mean()}


class MedianPositionValue(Metric):
    """
    计算未平仓 position value 的中位数。

    Parameters:
        name: 指标名称。默认值为 `MedianPositionValue`。
    """

    def __init__(self, name: str = None):
        self.name = name if name is not None else 'MedianPositionValue'

    def compute(self, df: pl.DataFrame, context: Dict[str, Any]) -> Mapping[str, Any]:
        return {self.name: (df['position'].abs() * df['price']).median()}


class MaxLeverage(Metric):
    """
    计算最大杠杆，定义为最大未平仓 position value 除以资金。

    Parameters:
        name: 指标名称。默认值为 `MaxLeverage`。
        book_size: 资金分配额。
    """

    def __init__(self, name: str = None, book_size: float = 0.0):
        if book_size <= 0.0:
            warnings.warn('book_size should be positive.', UserWarning)
        self.name = name if name is not None else 'MaxLeverage'
        self.capital = book_size

    def compute(self, df: pl.DataFrame, context: Dict[str, Any]) -> Mapping[str, Any]:
        return {self.name: (df['position'].abs() * df['price']).max() / self.capital}
