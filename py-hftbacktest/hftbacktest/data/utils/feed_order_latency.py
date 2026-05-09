from typing import Any

import numpy as np
import polars as pl
from numba import njit

from hftbacktest import LOCAL_EVENT, EXCH_EVENT, EVENT_ARRAY

order_latency_dtype = np.dtype(
    [
        ('req_ts', 'i8'),
        ('exch_ts', 'i8'),
        ('resp_ts', 'i8'),
        ('_padding', 'i8')
    ],
    align=True
)


@njit
def generate_order_latency_nb(
        data: EVENT_ARRAY,
        order_latency: np.ndarray[Any, order_latency_dtype],
        mul_entry: float,
        offset_entry: float,
        mul_resp: float,
        offset_resp: float
):
    for i in range(len(data)):
        exch_ts = data[i].exch_ts
        local_ts = data[i].local_ts
        feed_latency = local_ts - exch_ts
        order_entry_latency = mul_entry * feed_latency + offset_entry
        order_resp_latency = mul_resp * feed_latency + offset_resp

        req_ts = local_ts
        order_exch_ts = req_ts + order_entry_latency
        resp_ts = order_exch_ts + order_resp_latency

        order_latency[i].req_ts = req_ts
        order_latency[i].exch_ts = order_exch_ts
        order_latency[i].resp_ts = resp_ts


def generate_order_latency(
        feed_file: str,
        output_file: str | None = None,
        mul_entry: float = 1,
        offset_entry: float = 0,
        mul_resp: float = 1,
        offset_resp: float = 0,
        resampling_ns: int = 1_000_000_000
) -> np.ndarray[Any, order_latency_dtype]:
    """
    基于行情 feed latency 生成合成订单延迟数据。

    订单延迟模型如下：
        - Order entry latency    = mul_entry * feed_latency + offset_entry
        - Order response latency = mul_resp  * feed_latency + offset_resp

    Args:
        feed_file: 市场 feed 文件路径。
        output_file: 如果提供，则把生成的订单延迟数据保存到该文件。
        mul_entry: 用于根据 feed latency 计算 entry latency 的乘数。
        offset_entry: 加到 entry latency 上的常数偏移。
        mul_resp: 用于根据 feed latency 计算 response latency 的乘数。
        offset_resp: 加到 response latency 上的常数偏移。
        resampling_ns: 重采样间隔，单位为纳秒。合成订单延迟数据会按该间隔对 feed
                       latency 数据重采样后生成。默认值：1_000_000_000 ns（1 s）。

    Returns:
        生成的订单延迟数据。
    """
    data = np.load(feed_file)['data']
    df = pl.DataFrame(data)

    df = df.filter(
        (pl.col('ev') & EXCH_EVENT == EXCH_EVENT) & (pl.col('ev') & LOCAL_EVENT == LOCAL_EVENT)
    ).with_columns(
        pl.col('local_ts').alias('ts')
    ).group_by_dynamic(
        'ts', every=f'{resampling_ns}i'
    ).agg(
        pl.col('exch_ts').last(),
        pl.col('local_ts').last()
    ).drop('ts')

    data = df.to_numpy(structured=True)

    order_latency = np.zeros(
        len(data),
        dtype=order_latency_dtype
    )
    generate_order_latency_nb(data, order_latency, mul_entry, offset_entry, mul_resp, offset_resp)

    if output_file is not None:
        np.savez_compressed(output_file, data=order_latency)

    return order_latency
