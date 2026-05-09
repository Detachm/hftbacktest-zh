import inspect
from abc import ABC, abstractmethod
from typing import Any, List, Type, Mapping, Literal

import numpy as np
import polars as pl
from numpy.typing import NDArray

from .metrics import (
    Metric,
    SR,
    Sortino,
    Ret,
    MaxDrawdown,
    DailyTradingValue,
    ReturnOverMDD,
    ReturnOverTrade,
    MaxPositionValue, DailyNumberOfTrades
)
from .utils import resample, monthly, daily, hourly


def compute_metrics(
        df: pl.DataFrame,
        metrics: List[Metric | Type[Metric]],
        kwargs: Mapping[str, Any]
) -> Mapping[str, Any]:
    context = {
        'start': df['timestamp'][0],
        'end': df['timestamp'][-1],
    }

    for metric in metrics:
        if isinstance(metric, type):
            sig = inspect.signature(metric.__init__)
            valid_kwargs = {k: v for k, v in kwargs.items() if k in sig.parameters}
            metric = metric(**valid_kwargs)

        ret = metric.compute(df, context)

        for key, value in ret.items():
            context[key] = value

    return context


class Stats:
    """
    **示例**

    .. code-block:: python

        import numpy as np
        from hftbacktest.stats import LinearAssetRecord

        asset0_record = np.load('backtest_result.npz')['0']
        stats = (
            LinearAssetRecord(asset0_record)
                .resample('10s')
                .monthly()
                .stats(book_size=100000)
        )
        stats.summary()
        stats.plot()

    """

    def __init__(self, entire: pl.DataFrame, splits: List[Mapping[str, Any]], kwargs: Mapping[str, Any]):
        self.entire = entire
        self.splits = splits
        self.kwargs = kwargs

    def summary(self, pretty: bool = False):
        """
        显示统计摘要。

        Args:
            pretty: 以更易读的格式返回统计结果。
        """
        df = pl.DataFrame(self.splits)
        return df

    def plot(self, price_as_ret: bool = False, backend: Literal['matplotlib', 'holoviews'] = 'matplotlib'):
        """
        绘制权益曲线、position 时间序列以及价格图。

        Args:
            price_as_ret: 如果设为 `True`，价格图按累计收益绘制；否则按原始价格绘制。
            backend: 指定用于绘图的库。默认值为 'matplotlib'。
        """
        if backend == 'matplotlib':
            return self.plot_matplotlib(price_as_ret)
        elif backend == 'holoviews':
            return self.plot_holoviews(price_as_ret)
        else:
            raise ValueError(f'{backend} is unsupported')

    def plot_holoviews(self, price_as_ret: bool = False):
        import holoviews as hv

        entire_df = self.entire
        kwargs = self.kwargs

        equity = entire_df['equity_wo_fee'] - entire_df['fee']
        equity_wo_fee = entire_df['equity_wo_fee']

        book_size = kwargs.get('book_size')
        if book_size is not None:
            if price_as_ret:
                equity_plt = hv.Overlay([
                    hv.Curve(
                        (entire_df['timestamp'], equity / book_size * 100),
                        label='Equity',
                        vdims=['Cumulative Returns (%)']
                    ),
                    hv.Curve(
                        (entire_df['timestamp'], equity_wo_fee / book_size * 100),
                        label='Equity w/o fee',
                        vdims=['Cumulative Returns (%)']
                    ),
                    hv.Curve(
                        (entire_df['timestamp'], (entire_df['price'] / entire_df['price'][0] - 1.0) * 100),
                        label='Price',
                        vdims=['Cumulative Returns (%)']
                    ).opts(alpha=0.2, color='black')
                ])
            else:
                equity_plt = hv.Overlay([
                    hv.Curve(
                        (entire_df['timestamp'], equity / book_size * 100),
                        label='Equity',
                        vdims=['Cumulative Returns (%)']
                    ),
                    hv.Curve(
                        (entire_df['timestamp'], equity_wo_fee / book_size * 100),
                        label='Equity w/o fee',
                        vdims=['Cumulative Returns (%)']
                    )
                ]) * hv.Curve(
                    (entire_df['timestamp'], entire_df['price']),
                    label='Price',
                    vdims=['Price']
                ).opts(xlabel='timestamp', alpha=0.2, color='black')
        else:
            equity_plt = hv.Overlay([
                hv.Curve(
                    (entire_df['timestamp'], equity),
                    label='Equity',
                    vdims=['Equity']
                ),
                hv.Curve(
                    (entire_df['timestamp'], equity_wo_fee),
                    label='Equity w/o fee',
                    vdims=['Equity']
                )
            ]) * hv.Curve(
                (entire_df['timestamp'], entire_df['price']),
                label='Price',
                vdims=['Price']
            ).opts(xlabel='timestamp', alpha=0.2, color='black')

        px_plt = hv.Curve(
            (entire_df['timestamp'], entire_df['price']),
            label='Price',
            vdims=['Price']
        ).opts(xlabel='timestamp', alpha=0.2, color='black')
        pos_plt = hv.Curve(
            (entire_df['timestamp'], entire_df['position']),
            label='Position',
            vdims=['Position (Qty)']
        )

        plt1 = equity_plt.opts(yformatter='$%.2f')
        plt1.opts(multi_y=True, width=1000, height=400, legend_position='right', show_grid=True)

        plt2 = pos_plt.opts(yformatter='$%d') * px_plt
        plt2.opts(multi_y=True, width=1000, height=400, legend_position='right', show_grid=True)

        return (plt1.relabel('Equity') + plt2.relabel('Position')).cols(1)

    def plot_matplotlib(self, price_as_ret: bool = False):
        from matplotlib import pyplot as plt

        fig, (ax1, ax2) = plt.subplots(2, 1, sharex=True)
        fig.subplots_adjust(hspace=0)
        fig.set_size_inches(10, 6)

        entire_df = self.entire
        kwargs = self.kwargs

        equity = entire_df['equity_wo_fee'] - entire_df['fee']
        equity_wo_fee = entire_df['equity_wo_fee']

        book_size = kwargs.get('book_size')
        if book_size is not None:
            if price_as_ret:
                ax1.plot(entire_df['timestamp'], equity / book_size * 100)
                ax1.plot(entire_df['timestamp'], equity_wo_fee / book_size * 100)
                ax1.plot(entire_df['timestamp'], (entire_df['price'] / entire_df['price'][0] - 1.0) * 100, 'black', alpha=0.2)

                ax1.set_ylabel('Cumulative Returns (%)')
                ax1.legend(['Equity', 'Equity w/o fee', 'Price'])
            else:
                ax1.plot(entire_df['timestamp'], equity / book_size * 100)
                ax1.plot(entire_df['timestamp'], equity_wo_fee / book_size * 100)
                ax1_ = ax1.twinx()
                ax1_.plot(entire_df['timestamp'], entire_df['price'], 'black', alpha=0.2)

                ax1.set_ylabel('Cumulative Returns (%)')
                ax1_.set_ylabel('Price')
                ax1.legend(['Equity', 'Equity w/o fee'])
                ax1_.legend(['Price'])
        else:
            ax1.plot(entire_df['timestamp'], equity)
            ax1.plot(entire_df['timestamp'], equity_wo_fee)
            ax1_ = ax1.twinx()
            ax1_.plot(entire_df['timestamp'], entire_df['price'], 'black', alpha=0.2)

            ax1.set_ylabel('Equity')
            ax1_.set_ylabel('Price')
            ax1.legend(['Equity', 'Equity w/o fee', 'Price'])
            ax1_.legend(['Price'])

        ax1.grid()

        ax2.plot(entire_df['timestamp'], entire_df['position'], label='Position')

        ax2_ = ax2.twinx()
        ax2_.plot(entire_df['timestamp'], entire_df['price'], 'black', alpha=0.2, label='Price')

        handles, labels = [], []
        for ax in (ax2, ax2_):
            h, l = ax.get_legend_handles_labels()
            handles.extend(h)
            labels.extend(l)

        ax2.legend(handles, labels, loc='best')

        ax2.set_ylabel('Position (Qty)')
        ax2_.set_ylabel('Price')
        ax2.grid()

        #display(plt.gcf())
        plt.close()

        return fig

class Record(ABC):
    DEFAULT_METRICS = (
        SR,
        Sortino,
        Ret,
        MaxDrawdown,
        DailyNumberOfTrades,
        DailyTradingValue,
        ReturnOverMDD,
        ReturnOverTrade,
        MaxPositionValue
    )

    def __init__(self, data: NDArray | pl.DataFrame):
        self._contract_size = 1.0
        self._time_unit = 'ns'
        self._frequency = '10s'
        self._partition = None

        if isinstance(data, np.ndarray):
            self.df = pl.DataFrame(data)
        elif isinstance(data, pl.DataFrame):
            self.df = data
        else:
            raise ValueError

    def contract_size(self, contract_size: float) -> 'Self':
        """
        设置合约乘数。默认值为 `1.0`。

        Args:
            contract_size: 资产的合约乘数。
        """
        self._contract_size = contract_size
        return self

    def time_unit(self, time_unit: str) -> 'Self':
        """
        设置把记录中的时间戳转换为 datetime 时使用的时间单位。默认值为 `ns`。

        Args:
            time_unit: epoch time 以来时间步的时间单位。内部使用 `Polars`，详情请参考
                       `polars.from_epoch <https://docs.pola.rs/api/python/stable/reference/expressions/api/polars.from_epoch.html>`_
        """
        self._time_unit = time_unit
        return self

    def resample(self, frequency: str) -> 'Self':
        """
        设置记录降采样的重采样频率。这会影响与采样间隔相关的指标计算。
        同时，它也会减少计算指标和绘图所需时间。默认值为 `10s`。

        Args:
            frequency: 窗口间隔。内部使用 `Polars`，详情请参考
                       `polars.DataFrame.group_by_dynamic <https://docs.pola.rs/api/python/stable/reference/dataframe/api/polars.DataFrame.group_by_dynamic.html>`_
        """
        self._frequency = frequency
        return self

    def monthly(self) -> 'Self':
        """
        生成月度统计。
        """
        self._partition = 'monthly'
        return self

    def daily(self) -> 'Self':
        """
        生成日度统计。
        """
        self._partition = 'daily'
        return self

    @abstractmethod
    def prepare(self):
        raise NotImplementedError

    def stats(
            self,
            metrics: List[Metric | Type[Metric]] | None = None,
            **kwargs: Any
    ) -> Stats:
        """
        **示例**

        .. code-block:: python

            stats = record.stats([SR('SR365', trading_days_per_year=365), AnnualRet(trading_days_per_year=365)]


        Args:
            metrics: 对该记录计算的指标列表。每个指标都应是从 `Metric` 类派生的类。
                     如果传入的是类类型而不是实例，会使用提供的 ``kwargs`` 构造该类实例。

                     默认值为以下指标列表：
                     :class:`SR <metrics.SR>`,
                     :class:`Sortino <metrics.Sortino>`,
                     :class:`Ret <metrics.Ret>`,
                     :class:`MaxDrawdown <metrics.MaxDrawdown>`,
                     :class:`DailyNumberOfTrades <metrics.DailyNumberOfTrades>`,
                     :class:`DailyTradingValue <metrics.DailyTradingValue>`,
                     :class:`ReturnOverMDD <metrics.ReturnOverMDD>`,
                     :class:`ReturnOverTrade <metrics.rTrade>`, and
                     :class:`MaxPositionValue <metrics.MaxPositionValue>`.
            kwargs: 用于构造 `Metric` 实例的关键字参数。

        Returns:
            该记录在指定指标上的统计结果。
        """
        if metrics is None:
            metrics = Record.DEFAULT_METRICS

        if not isinstance(self.df['timestamp'].dtype, pl.Datetime):
            self.df = self.df.with_columns(
                pl.from_epoch('timestamp', time_unit=self._time_unit)
            )

        if 'num_trades_' not in self.df:
            if 'num_trades' not in self.df:
                # This may not reflect the exact value since information could be lost between recording intervals.
                num_trades = self.df['position'].diff().fill_null(0).abs()
                num_trades = num_trades.set(num_trades > 0, 1)
                self.df = self.df.with_columns(
                    num_trades.alias('num_trades_')
                )
            else:
                self.df = self.df.with_columns(
                    pl.col('num_trades').diff().fill_null(0).alias('num_trades_')
                )

        if 'trading_volume_' not in self.df:
            if 'trading_volume' not in self.df:
                # This may not reflect the exact value since information could be lost between recording intervals.
                self.df = self.df.with_columns(
                    pl.col('position').diff().fill_null(0).abs().alias('trading_volume_')
                )
            else:
                self.df = self.df.with_columns(
                    pl.col('trading_volume').diff().fill_null(0).alias('trading_volume_')
                )

        # Prepares the asset type-specific data by computing it from the state records.
        self.prepare()

        if self._frequency is not None:
            # The DataFrame should be sorted by timestamp, even though it won't be resampled.
            self.df = self.df.set_sorted('timestamp')
            self.df = resample(self.df, self._frequency)

        if self._partition == 'monthly':
            splits = monthly(self.df)
        elif self._partition == 'daily':
            splits = daily(self.df)
        elif self._partition == 'hourly':
            splits = hourly(self.df)
        else:
            splits = []

        stats = [compute_metrics(df, metrics, kwargs) for df in splits]
        # For the entire period.
        stats.append(compute_metrics(self.df, metrics, kwargs))

        return Stats(self.df, stats, kwargs)


class LinearAssetRecord(Record):
    def prepare(self):
        if 'equity_wo_fee' not in self.df:
            self.df = self.df.with_columns(
                (
                    pl.col('balance') + pl.col('position') * pl.col('price') * self._contract_size
                ).alias('equity_wo_fee')
            )

        if 'trading_value_' not in self.df:
            if 'trading_value' not in self.df:
                # This may not reflect the exact value since information could be lost between recording intervals.
                self.df = self.df.with_columns(
                    (
                        pl.col('position').diff().fill_null(0) * pl.col('price') * self._contract_size
                    ).alias('trading_value_')
                )
            else:
                self.df = self.df.with_columns(
                    pl.col('trading_value').diff().fill_null(0).alias('trading_value_')
                )


class InverseAssetRecord(Record):
    def prepare(self):
        if 'equity_wo_fee' not in self.df:
            self.df = self.df.with_columns(
                (
                    -pl.col('balance') - pl.col('position') / pl.col('price') * self._contract_size
                ).alias('equity_wo_fee')
            )

        if 'trading_value_' not in self.df:
            if 'trading_value' not in self.df:
                # This may not reflect the exact value since information could be lost between recording intervals.
                self.df = self.df.with_columns(
                    (
                        (pl.col('position').diff().fill_null(0) / pl.col('price')) * self._contract_size
                    ).alias('trading_value_')
                )
            else:
                self.df = self.df.with_columns(
                    pl.col('trading_value').diff().fill_null(0).alias('trading_value_')
                )
