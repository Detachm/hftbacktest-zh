from typing import List

import numpy as np
from numpy.typing import NDArray

from ... import BacktestAsset, HashMapMarketDepthBacktest


def create_last_snapshot(
        data: List[str],
        tick_size: float,
        lot_size: float,
        initial_snapshot: str | None = None,
        output_snapshot_filename: str | None = None
) -> NDArray:
    r"""
    为指定数据创建最后一刻市场深度快照，可作为后续数据的初始快照。

    Args:
         data: 用于生成最后市场深度快照的数据。
         tick_size: 给定资产的最小价格变动单位。
         lot_size: 给定资产的最小订单数量。
         initial_snapshot: 初始市场深度快照。
         output_snapshot_filename: 如果提供，则把快照数据以 ``npz`` 格式保存到指定文件。

    Returns:
        与 HftBacktest 兼容的最后市场深度快照。
    """
    # Just to reconstruct order book from the given snapshot to the end of the given data.
    asset = (
        BacktestAsset()
            .data(data)
            .tick_size(tick_size)
            .lot_size(lot_size)
    )
    if initial_snapshot is not None:
        asset.initial_snapshot(initial_snapshot)

    hbt = HashMapMarketDepthBacktest([asset])

    # Go to the end of the data.
    if hbt._goto_end() not in [0, 1]:
        raise RuntimeError

    depth = hbt.depth(0)
    snapshot = depth.snapshot()
    snapshot_copied = snapshot.copy()
    depth.snapshot_free(snapshot)

    if output_snapshot_filename is not None:
        np.savez_compressed(output_snapshot_filename, data=snapshot_copied)

    return snapshot_copied
