初始化
======

本页列出创建回测资产和回测器的核心入口。通常先用
``BacktestAsset`` 配置数据、资产类型、延迟模型、队列模型、交易所模型、手续费模型、
``tick_size`` 和 ``lot_size``，再用 ``HashMapMarketDepthBacktest`` 或
``ROIVectorMarketDepthBacktest`` 构造回测器。

.. autoclass:: hftbacktest.BacktestAsset
   :members:
   :inherited-members:
   :member-order: bysource

.. autofunction:: hftbacktest.HashMapMarketDepthBacktest

.. autofunction:: hftbacktest.ROIVectorMarketDepthBacktest
