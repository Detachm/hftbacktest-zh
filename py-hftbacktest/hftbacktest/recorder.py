from typing import Any

import numpy as np
from numba import uint64, from_dtype
from numba.experimental import jitclass

from .types import record_dtype


@jitclass
class Recorder_:
    records: from_dtype(record_dtype)[:, :]
    i: uint64

    def __init__(self, num_assets: uint64, record_size: uint64):
        self.records = np.empty((record_size, num_assets), record_dtype)
        self.i = 0

    def record(self, hbt) -> None:
        timestamp = hbt.current_timestamp
        for asset_no in range(hbt.num_assets):
            depth = hbt.depth(asset_no)
            mid_price = (depth.best_bid + depth.best_ask) / 2.0
            state_values = hbt.state_values(asset_no)
            self.records[self.i, asset_no].timestamp = timestamp
            self.records[self.i, asset_no].price = mid_price
            self.records[self.i, asset_no].position = state_values.position
            self.records[self.i, asset_no].balance = state_values.balance
            self.records[self.i, asset_no].fee = state_values.fee
            self.records[self.i, asset_no].num_trades = state_values.num_trades
            self.records[self.i, asset_no].trading_volume = state_values.trading_volume
            self.records[self.i, asset_no].trading_value = state_values.trading_value

        self.i += 1
        if self.i == len(self.records):
            raise IndexError


class Recorder:
    """
    记录时间序列状态信息，用于计算权益曲线和绩效指标。

    Args:
        num_assets: 资产总数。
        record_size: 最多保存的记录数量。
    """

    def __init__(self, num_assets: uint64, record_size: uint64):
        self._recorder = Recorder_(num_assets, record_size)

    @property
    def recorder(self):
        """
        返回可在 Numba 代码中使用的 recorder 实例。

        可以在执行过程中用该实例记录状态，例如：
        ``recorder.record(hbt)``
        """
        return self._recorder

    def to_npz(self, file: str) -> None:
        """
        将记录保存到文件。

        Args:
            file: 输出文件路径。
        """
        data = self._recorder.records[:self._recorder.i]
        kwargs = {str(asset_no): data[:, asset_no] for asset_no in range(data.shape[1])}
        np.savez_compressed(file, **kwargs)

    def get(self, asset_no: int) -> np.ndarray[Any, record_dtype]:
        """
        获取指定资产编号的记录。

        Args:
            asset_no: 资产编号。

        Returns:
            与该资产编号对应的记录。
        """
        return self._recorder.records[:self._recorder.i, asset_no]
