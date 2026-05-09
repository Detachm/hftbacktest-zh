============
迁移到 v2
============

迁移概览
--------

从版本 1 迁移到版本 2 引入了一些重要变化。如果不修改代码直接沿用旧写法，可能会出错。强烈建议阅读更新后的教程。本文用于帮助你避开迁移过程中的常见问题。

检查成功：使用 ``elapse() == 0``
----------------------------------

在版本 1 中，``elapse`` 函数成功时返回 ``True``，失败时返回 ``False``。策略循环通常会用 ``while elapse(duration)`` 检查时间推进是否成功。

在版本 2 中，``elapse`` 返回的是状态码而不是布尔值：``0`` 表示成功，其他值表示错误。因此，代码应改为检查返回值是否等于 ``0``。

例如：``while elapse(duration) == 0``。如果代码保持不变，返回值 ``0`` 会被当作 ``False``，从而导致逻辑失败。

其他会推进时间的方法，例如 ``submit_buy_order`` 或 ``submit_sell_order``，也和 ``elapse`` 类似返回状态码，而不是布尔值。应检查它们的返回值是否等于 ``0`` 来确认成功，而不是检查是否为 ``True``。

数据格式变化
------------

输入 HftBacktest 的数据格式发生了较大变化。强烈建议从原始数据重新处理，以保留全部信息。如果没有原始数据，也可以使用从 v1 到 v2 的 :mod:`data conversion utility <hftbacktest.data.utils.migration2>`。

主要变化如下：

* SOA 到 AOS：格式从列式数组 (SOA) 变为结构化数组 (AOS)。

* 移除 ``side`` 列：版本 2 中，买卖方向由 ``ev`` 字段中的标志表示，即 :const:`BUY_EVENT <hftbacktest.types.BUY_EVENT>` 和 :const:`SELL_EVENT <hftbacktest.types.SELL_EVENT>`。

* 时间戳处理：版本 1 中，数据工具会通过把某个时间戳替换为 ``-1`` 来修正事件顺序，表示该事件在交易所侧或本地侧无效。版本 2 中，事件在交易所侧或本地侧是否有效，由 ``ev`` 字段中的 :const:`EXCH_EVENT <hftbacktest.types.EXCH_EVENT>` 和 :const:`LOCAL_EVENT <hftbacktest.types.LOCAL_EVENT>` 标志决定。

* 时间戳单位：虽然没有强制要求，但时间戳单位已从微秒改为纳秒。

此外，实盘订单延迟数据的格式也从 SOA 改为 AOS。
