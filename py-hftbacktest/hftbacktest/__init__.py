from typing import List, Any

import numpy as np
from numpy.typing import NDArray

from ._hftbacktest import (
    BacktestAsset as BacktestAsset_,
    build_hashmap_backtest,
    build_roivec_backtest,
    LiveInstrument
)
from .binding import (
    HashMapMarketDepthBacktest_,
    HashMapMarketDepthBacktest as HashMapMarketDepthBacktest_TypeHint,
    ROIVectorMarketDepthBacktest_,
    ROIVectorMarketDepthBacktest as ROIVectorMarketDepthBacktest_TypeHint,

    event_dtype
)
from .order import (
    BUY,
    SELL,
    NONE,
    NEW,
    EXPIRED,
    FILLED,
    CANCELED,
    GTC,
    GTX,
    LIMIT,
    MARKET,
)
from .recorder import Recorder
from .types import (
    ALL_ASSETS,
    EVENT_ARRAY,
    DEPTH_EVENT,
    TRADE_EVENT,
    DEPTH_CLEAR_EVENT,
    DEPTH_SNAPSHOT_EVENT,
    DEPTH_BBO_EVENT,
    ADD_ORDER_EVENT,
    CANCEL_ORDER_EVENT,
    MODIFY_ORDER_EVENT,
    FILL_EVENT,
    EXCH_EVENT,
    LOCAL_EVENT,
    BUY_EVENT,
    SELL_EVENT
)
try:
    from ._hftbacktest import (
        build_hashmap_livebot,
        build_roivec_livebot
    )
    from .binding import (
        HashMapMarketDepthLiveBot_,
        HashMapMarketDepthLiveBot as HashMapMarketDepthLiveBot_TypeHint,
        ROIVectorMarketDepthLiveBot_,
        ROIVectorMarketDepthLiveBot as ROIVectorMarketDepthLiveBot_TypeHint,
    )
    LIVE_FEATURE = True
except:
    LIVE_FEATURE = False

__all__ = (
    'BacktestAsset',
    'HashMapMarketDepthBacktest',
    'ROIVectorMarketDepthBacktest',

    'LiveInstrument',
    'HashMapMarketDepthLiveBot',
    'ROIVectorMarketDepthLiveBot',

    'ALL_ASSETS',

    # Event flags
    'DEPTH_EVENT',
    'TRADE_EVENT',
    'DEPTH_CLEAR_EVENT',
    'DEPTH_SNAPSHOT_EVENT',
    'DEPTH_BBO_EVENT',
    'ADD_ORDER_EVENT',
    'CANCEL_ORDER_EVENT',
    'MODIFY_ORDER_EVENT',
    'FILL_EVENT',
    'EXCH_EVENT',
    'LOCAL_EVENT',
    'EXCH_EVENT',
    'LOCAL_EVENT',
    'BUY_EVENT',
    'SELL_EVENT',

    # Side
    'BUY',
    'SELL',

    # Order status
    'NONE',
    'NEW',
    'EXPIRED',
    'FILLED',
    'CANCELED',

    # Time-In-Force
    'GTC',
    'GTX',

    'LIMIT',
    'MARKET',
    
    'Recorder'
)

__version__ = '2.4.4'


class BacktestAsset(BacktestAsset_):
    def add_data(self, data: EVENT_ARRAY):
        self._add_data_ndarray(data.ctypes.data, len(data))
        return self

    def data(self, data: str | List[str] | EVENT_ARRAY | List[EVENT_ARRAY]):
        """
        设置行情 feed 数据。

        Args:
            data: `.npz` 格式行情数据文件路径列表，或包含行情 feed 数据的 NumPy 数组列表。
        """
        if isinstance(data, str):
            self.add_file(data)
        elif isinstance(data, np.ndarray):
            self.add_data(data)
        elif isinstance(data, list):
            for item in data:
                if isinstance(item, str):
                    self.add_file(item)
                elif isinstance(item, np.ndarray):
                    self.add_data(item)
                else:
                    raise ValueError
        else:
            raise ValueError
        return self

    def intp_order_latency(self, data: str | NDArray | List[str], latency_offset: int = 0):
        """
        使用 `IntpOrderLatency <https://docs.rs/hftbacktest/latest/hftbacktest/backtest/models/struct.IntpOrderLatency.html>`_
        作为订单延迟模型。

        请参考订单延迟数据格式。历史延迟数据的单位应与行情数据时间戳单位一致。
        HftBacktest 通常使用纳秒。

        Args:
            data: `npz` 格式历史订单延迟数据文件路径列表，或历史订单延迟数据 NumPy 数组。
            latency_offset: 延迟偏移量，用于按指定数值调整订单进入延迟和订单回报延迟。
                            在跨交易所回测中尤其有用，例如行情数据采集地点与策略实际运行地点不同。
        """
        if isinstance(data, str):
            super().intp_order_latency([data], latency_offset)
        elif isinstance(data, np.ndarray):
            self._intp_order_latency_ndarray(data.ctypes.data, len(data), latency_offset)
        elif isinstance(data, list):
            super().intp_order_latency(data, latency_offset)
        else:
            raise ValueError
        return self

    def initial_snapshot(self, data: str | np.ndarray[Any, event_dtype]):
        """
        设置初始订单簿快照。

        Args:
            data: 初始快照文件路径，或初始快照的 NumPy 数组。
        """
        if isinstance(data, str):
            super().initial_snapshot(data)
        elif isinstance(data, np.ndarray):
            self._initial_snapshot_ndarray(data.ctypes.data, len(data))
        else:
            raise ValueError
        return self


def HashMapMarketDepthBacktest(
        assets: List[BacktestAsset]
) -> HashMapMarketDepthBacktest_TypeHint:
    """
    构造 `HashMapMarketDepthBacktest` 实例。

    Args:
        assets: 使用 :class:`BacktestAsset` 构造的回测资产列表。

    Returns:
        已 JIT 化的 `HashMapMarketDepthBacktest`，可在 ``njit`` 函数中使用。
    """
    ptr = build_hashmap_backtest(assets)
    return HashMapMarketDepthBacktest_(ptr)


def ROIVectorMarketDepthBacktest(
        assets: List[BacktestAsset]
) -> ROIVectorMarketDepthBacktest_TypeHint:
    """
    构造 `ROIVectorMarketDepthBacktest` 实例。

    Args:
        assets: 使用 :class:`BacktestAsset` 构造的回测资产列表。

    Returns:
        已 JIT 化的 `ROIVectorMarketDepthBacktest`，可在 ``njit`` 函数中使用。
    """
    ptr = build_roivec_backtest(assets)
    return ROIVectorMarketDepthBacktest_(ptr)


if LIVE_FEATURE:
    def ROIVectorMarketDepthLiveBot(
            assets: List[LiveInstrument]
    ) -> ROIVectorMarketDepthLiveBot_TypeHint:
        """
        Constructs an instance of `ROIVectorMarketDepthLiveBot`.

        Args:
            assets: A list of live instruments constructed using :class:`LiveInstrument`.

        Returns:
            A jit`ed `ROIVectorMarketDepthLiveBot` that can be used in an ``njit`` function.
        """
        ptr = build_roivec_livebot(assets)
        return ROIVectorMarketDepthLiveBot_(ptr)
