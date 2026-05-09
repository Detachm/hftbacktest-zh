from typing import Any

import numpy as np
from numba import float64, int64, uint8, from_dtype, uint64
from numba.experimental import jitclass

from .types import order_dtype

UNSUPPORTED = 255

BUY = 1
"""
在市场深度事件中表示 bid 侧；在成交事件中表示成交发起方为买方。
"""

SELL = -1
"""
在市场深度事件中表示 ask 侧；在成交事件中表示成交发起方为卖方。
"""

#: NONE
NONE = 0

#: NEW
NEW = 1

#: EXPIRED
EXPIRED = 2

#: FILLED
FILLED = 3

#: CANCELED
CANCELED = 4

#: PARTIALLY_FILLED
PARTIALLY_FILLED = 5

#: REJECTED
REJECTED = 6

#: Good 'till cancel
GTC = 0

#: Post only
GTX = 1

#: Fill or kill
FOK = 2

#: Immediate or cancel
IOC = 3

#: LIMIT
LIMIT = 0

#: MARKET
MARKET = 1


class Order:
    arr: from_dtype(order_dtype)[:]

    def __init__(self, arr: np.ndarray[Any, order_dtype]):
        self.arr = arr

    @property
    def price(self) -> float64:
        """
        返回订单价格。
        """
        return self.arr[0].price_tick * self.arr[0].tick_size

    @property
    def exec_price(self) -> float64:
        """
        返回成交价格。仅当 :obj:`status` 为 :const:`FILLED` 或 :const:`PARTIALLY_FILLED` 时有效。
        """
        return self.arr[0].exec_price_tick * self.arr[0].tick_size

    @property
    def cancellable(self) -> bool:
        """
        返回订单是否可撤。只有活跃订单才能撤销，即 :obj:`status` 应为 :const:`NEW`
        或 :const:`PARTIALLY_FILLED`。理论上，撤单不一定要求该订单没有正在处理的请求；
        但为了简化实现，HftBacktest 当前要求订单没有正在处理的请求时才允许撤销。
        """
        return (self.arr[0].status == NEW or self.arr[0].status == PARTIALLY_FILLED) and self.arr[0].req == NONE

    @property
    def qty(self) -> float64:
        """
        返回订单数量。
        """
        return self.arr[0].qty

    @property
    def leaves_qty(self) -> float64:
        """
        返回订单部分成交后的剩余活跃数量。在回测中，仅对支持部分成交的交易所模型有效，
        例如 `PartialFillExchange`。
        """
        return self.arr[0].leaves_qty

    @property
    def price_tick(self) -> int64:
        """
        返回以 tick 表示的订单价格。
        """
        return self.arr[0].price_tick

    @property
    def tick_size(self) -> float64:
        """
        返回 tick size。
        """
        return self.arr[0].price_tick

    @property
    def exch_timestamp(self) -> int64:
        """
        返回订单被交易所处理时的时间戳。
        """
        return self.arr[0].exch_timestamp

    @property
    def local_timestamp(self) -> int64:
        """
        返回本地发出订单请求时的时间戳。
        """
        return self.arr[0].local_timestamp

    @property
    def exec_price_tick(self) -> int64:
        """
        返回以 tick 表示的成交价格。仅当 :obj:`status` 为 :const:`FILLED` 或
        :const:`PARTIALLY_FILLED` 时有效。
        """
        return self.arr[0].exec_price_tick

    @property
    def exec_qty(self) -> float64:
        """
        返回成交数量。仅当 :obj:`status` 为 :const:`FILLED` 或 :const:`PARTIALLY_FILLED` 时有效。
        """
        return self.arr[0].exec_qty

    @property
    def order_id(self) -> uint64:
        """
        返回订单 ID。
        """
        return self.arr[0].order_id

    @property
    def order_type(self) -> uint8:
        """
        返回订单类型。可能为以下值之一，但具体取值会随交易所模型而变化。

            * :const:`MARKET`
            * :const:`LIMIT`
        """
        return self.arr[0].order_type

    @property
    def req(self) -> uint8:
        """
        返回当前正在处理的请求类型。可能为以下值之一，但具体取值会随交易所模型而变化。

            * :const:`NONE` 表示没有正在处理的请求。
            * :const:`NEW` 表示提交新订单。
            * :const:`CANCELED` 表示撤销订单。
        """
        return self.arr[0].req

    @property
    def status(self) -> uint8:
        """
        返回订单状态。可能为以下值之一，但具体取值会随交易所模型而变化。

            * :const:`NONE`
            * :const:`NEW`
            * :const:`EXPIRED`
            * :const:`FILLED`
            * :const:`CANCELED`
            * :const:`PARTIALLY_FILLED`
        """
        return self.arr[0].status

    @property
    def side(self) -> uint8:
        """
        返回订单方向。

            * :const:`BUY`
            * :const:`SELL`
        """
        return self.arr[0].side

    @property
    def time_in_force(self) -> uint8:
        """
        返回订单的 Time-In-Force。可能为以下值之一，但具体取值会随交易所模型而变化。

            * :const:`GTC`
            * :const:`GTX`
            * :const:`FOK`
            * :const:`IOC`
        """
        return self.arr[0].time_in_force


Order_ = jitclass(Order)
