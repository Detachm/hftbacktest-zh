数据工具
========

本页汇总交易所历史数据转换、订单簿快照生成、深度数据融合等工具模块。
工具函数的输入文件格式通常依赖具体数据源，原始 JSON/CSV 字段名保持英文。

.. toctree::
   :maxdepth: 4

   hftbacktest.data.utils.binancefutures
   hftbacktest.data.utils.binancehistmktdata
   hftbacktest.data.utils.bybithistmktdata
   hftbacktest.data.utils.databento
   hftbacktest.data.utils.difforderbooksnapshot
   hftbacktest.data.utils.hyperliquid
   hftbacktest.data.utils.mexc
   hftbacktest.data.utils.migration2
   hftbacktest.data.utils.snapshot
   hftbacktest.data.utils.tardis

.. autoclass:: hftbacktest.binding.FuseMarketDepth
   :members:
   :member-order: bysource
