============
JIT 编译开销
============

HftBacktest 使用 Numba 的能力，并依赖 Numba JIT 编译后的类。因此，导入 HftBacktest 时需要进行 JIT 编译，可能耗时数秒。为了获得更好的回测性能，策略函数本身也需要 JIT 编译，这同样需要编译时间。

如果回测覆盖多天数据，这点开销通常不明显，但仍可能影响使用体验。为了减少开销，可以考虑使用 Numba 的 ``cache`` 功能。示例如下。

.. code-block:: python

    from numba import njit
    # May take a few seconds
    from hftbacktest import BacktestAsset, HashMapMarketDepthBacktest

    # Enables caching feature
    @njit(cache=True)
    def algo(arguments, hbt):
        # your algo implementation.

    asset = (
        BacktestAsset()
            .linear_asset(1.0)
            .data([
                'data/ethusdt_20221003.npz',
                'data/ethusdt_20221004.npz',
                'data/ethusdt_20221005.npz',
                'data/ethusdt_20221006.npz',
                'data/ethusdt_20221007.npz'
            ])
            .initial_snapshot('data/ethusdt_20221002_eod.npz')
            .no_partial_fill_exchange()
            .intp_order_latency([
                'data/latency_20221003.npz',
                'data/latency_20221004.npz',
                'data/latency_20221005.npz',
                'data/latency_20221006.npz',
                'data/latency_20221007.npz'
            ])
            .power_prob_queue_model3(3.0)
            .tick_size(0.01)
            .lot_size(0.001)
            .trading_value_fee_model(0.0002, 0.0007)
    )

    hbt = HashMapMarketDepthBacktest([asset])
    algo(arguments, hbt)
