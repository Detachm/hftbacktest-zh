from typing import Any

import numpy as np
from numba import from_dtype, float64, int64
from numba.experimental import jitclass

from .types import state_values_dtype


class StateValues:
    arr: from_dtype(state_values_dtype)[:]

    def __init__(self, arr: np.ndarray[Any, state_values_dtype]):
        self.arr = arr

    @property
    def position(self) -> float64:
        """
        返回当前未平仓 position。
        """
        return self.arr[0].position

    @property
    def balance(self) -> float64:
        """
        返回现金余额。
        """
        return self.arr[0].balance

    @property
    def fee(self) -> float64:
        """
        返回累计手续费。
        """
        return self.arr[0].fee

    @property
    def num_trades(self) -> int64:
        """
        返回累计成交次数。
        """
        return self.arr[0].num_trades

    @property
    def trading_volume(self) -> float64:
        """
        返回累计成交量。
        """
        return self.arr[0].trading_volume

    @property
    def trading_value(self) -> float64:
        """
        返回累计成交额。
        """
        return self.arr[0].trading_value


StateValues_ = jitclass(StateValues)
