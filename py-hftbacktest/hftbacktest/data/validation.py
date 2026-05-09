import sys

import numpy as np
from numba import njit
from numpy.typing import NDArray

from ..types import (
    EXCH_EVENT,
    LOCAL_EVENT,
    event_dtype,
    EVENT_ARRAY
)


@njit
def correct_local_timestamp(data: EVENT_ARRAY, base_latency: float) -> EVENT_ARRAY:
    """
    如果行情延迟为负，则按最大负延迟值原地调整本地时间戳：

    .. code-block::

        feed_latency = local_timestamp - exch_timestamp
        adjusted_local_timestamp = local_timestamp + min(feed_latency, 0) + base_latency

    Args:
        data: 待修正的数据。
        base_latency: 由于交易所和本地机器系统时间可能不一致，延迟测量可能不准确，
                      从而出现负延迟。转换过程会自动修正正延迟，但仍可能产生零延迟。
                      通过添加 ``base_latency`` 可以得到更现实的数值。单位应与 feed
                      数据时间戳单位一致。

    Returns:
        时间戳已修正的数据。
    """

    latency = sys.maxsize
    for row_num in range(len(data)):
        exch_timestamp = data[row_num].exch_ts
        local_timestamp = data[row_num].local_ts

        latency = min(latency, local_timestamp - exch_timestamp)

    if latency < 0:
        local_timestamp_offset = -latency + base_latency
        print('local_timestamp is ahead of exch_timestamp by', -latency)
        for row_num in range(len(data)):
            data[row_num].local_ts += local_timestamp_offset

    return data


@njit
def correct_event_order(
        data: EVENT_ARRAY,
        sorted_exch_index: NDArray,
        sorted_local_index: NDArray,
) -> EVENT_ARRAY:
    """
    通过把每一行拆成独立事件，修正顺序反转的交易所时间戳。随后通过复制事件，
    分别按交易所时间戳和本地时间戳排序。详情见
    `data <https://hftbacktest.readthedocs.io/en/latest/data.html>`_。

    Args:
        data: 待修正的数据。
        sorted_exch_index: 按交易所时间戳排序后的数据索引。
        sorted_local_index: 按本地时间戳排序后的数据索引。

    Returns:
        事件顺序已修正的数据。
    """
    sorted_final = np.zeros(data.shape[0] * 2, event_dtype)

    out_rn = 0
    exch_rn = 0
    local_rn = 0
    while True:
        sorted_exch = data[sorted_exch_index[exch_rn]]
        sorted_local = data[sorted_local_index[local_rn]]
        if (
                exch_rn < len(data)
                and local_rn < len(data)
                and sorted_exch.exch_ts == sorted_local.exch_ts
                and sorted_exch.local_ts == sorted_local.local_ts
        ):
            assert sorted_exch.ev == sorted_local.ev
            assert (sorted_exch.px == sorted_local.px) or (np.isnan(sorted_exch.px) and np.isnan(sorted_local.px))
            assert sorted_exch.qty == sorted_local.qty

            sorted_final[out_rn] = sorted_exch
            sorted_final[out_rn].ev = sorted_final[out_rn].ev | EXCH_EVENT | LOCAL_EVENT

            out_rn += 1
            exch_rn += 1
            local_rn += 1
        elif ((
                exch_rn < len(data)
                and local_rn < len(data)
                and sorted_exch.exch_ts == sorted_local.exch_ts
                and sorted_exch.local_ts < sorted_local.local_ts
        ) or (
                exch_rn < len(data)
                and sorted_exch.exch_ts < sorted_local.exch_ts
        )):
            # exchange
            sorted_final[out_rn] = sorted_exch
            sorted_final[out_rn].ev = sorted_final[out_rn].ev | EXCH_EVENT

            out_rn += 1
            exch_rn += 1
        elif ((
                exch_rn < len(data)
                and local_rn < len(data)
                and sorted_exch.exch_ts == sorted_local.exch_ts
                and sorted_exch.local_ts > sorted_local.local_ts
        ) or (
                local_rn < len(data)
        )):
            # local
            sorted_final[out_rn] = sorted_local
            sorted_final[out_rn].ev = sorted_final[out_rn].ev | LOCAL_EVENT

            out_rn += 1
            local_rn += 1
        elif exch_rn < len(data):
            # exchange
            sorted_final[out_rn] = sorted_exch
            sorted_final[out_rn].ev = sorted_final[out_rn].ev | EXCH_EVENT

            out_rn += 1
            exch_rn += 1
        else:
            assert exch_rn == len(data)
            assert local_rn == len(data)
            break
    return sorted_final[:out_rn]


def validate_event_order(data: EVENT_ARRAY) -> None:
    """
    校验事件顺序是否正确。如果数据中存在错误事件顺序，会抛出 :class:`ValueError`。

    Args:
        data: 待校验的数据。
    """
    exch_ev = data['ev'] & EXCH_EVENT == EXCH_EVENT
    local_ev = data['ev'] & LOCAL_EVENT == LOCAL_EVENT
    if np.sum(np.diff(data['exch_ts'][exch_ev]) < 0) > 0:
        raise ValueError('exchange events are out of order.')
    if np.sum(np.diff(data['local_ts'][local_ev]) < 0) > 0:
        raise ValueError('local events are out of order.')
