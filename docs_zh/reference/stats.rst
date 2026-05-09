统计
====

本页列出回测记录、统计摘要和常用绩效指标。指标类名保持英文，便于和代码、
notebook 示例以及输出列名对应。

.. autoclass:: hftbacktest.stats.Stats()
    :members:
    :member-order: bysource

.. autoclass:: hftbacktest.stats.LinearAssetRecord
    :inherited-members:
    :member-order: bysource

.. autoclass:: hftbacktest.stats.InverseAssetRecord
    :inherited-members:
    :member-order: bysource

指标
----

.. autoclass:: hftbacktest.stats.Metric

.. autoclass:: hftbacktest.stats.Ret

.. autoclass:: hftbacktest.stats.AnnualRet

.. autoclass:: hftbacktest.stats.SR

.. autoclass:: hftbacktest.stats.Sortino

.. autoclass:: hftbacktest.stats.MaxDrawdown

.. autoclass:: hftbacktest.stats.ReturnOverMDD

.. autoclass:: hftbacktest.stats.ReturnOverTrade

.. autoclass:: hftbacktest.stats.NumberOfTrades

.. autoclass:: hftbacktest.stats.DailyNumberOfTrades

.. autoclass:: hftbacktest.stats.TradingVolume

.. autoclass:: hftbacktest.stats.DailyTradingVolume

.. autoclass:: hftbacktest.stats.TradingValue

.. autoclass:: hftbacktest.stats.DailyTradingValue

.. autoclass:: hftbacktest.stats.MaxPositionValue

.. autoclass:: hftbacktest.stats.MeanPositionValue

.. autoclass:: hftbacktest.stats.MedianPositionValue

.. autoclass:: hftbacktest.stats.MaxLeverage
