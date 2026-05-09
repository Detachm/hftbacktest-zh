===========
HftBacktest
===========

高频交易回测工具
================

.. note::

   这是 hftbacktest 文档的中文翻译起点。英文原文仍以官方文档为准：
   https://hftbacktest.readthedocs.io/

HftBacktest 是一个用于开发高频交易和做市策略的回测框架。它重点模拟行情延迟、订单延迟，以及限价单在订单队列中的位置，从而在完整订单簿和逐笔成交数据的基础上，提供更接近真实市场回放的回测结果。

核心功能
========

* 可以在 `Numba <https://numba.pydata.org/>`_ JIT 函数中运行 Python 策略逻辑。
* 支持完整的逐 tick 仿真，可以使用自定义时间间隔，也可以基于行情接收和订单回报事件推进。
* 支持基于 Level-2 Market-By-Price 和 Level-3 Market-By-Order 数据重建完整订单簿。
* 回测中可以考虑行情延迟和订单延迟，既可以使用内置模型，也可以自定义延迟模型。
* 订单成交模拟会考虑订单队列位置，既可以使用内置队列模型，也可以自定义模型。
* 支持多资产、多交易所模型的回测。
* 支持使用同一套算法代码快速原型化并部署实盘交易机器人，目前实盘部分主要面向 Binance Futures 和 Bybit，且仅限 Rust。

为什么准确回测很重要
====================

交易是高度竞争的领域，很多策略只有很小的优势，但这些小优势仍然可能产生显著影响。因此，回测必须尽量准确地模拟真实交易条件。它不应该过度保守，以至于掩盖真实存在的微小优势；也不应该过度乐观，通过不现实的假设放大收益。至少，你需要清楚地知道回测和实盘之间有哪些差异，以及这些差异大概有多大。

在最开始，这还不是过拟合问题。讨论过拟合之前，首先需要确认回测是否真的能反映真实执行情况。举例来说，如果你在 2025 年 1 月运行了一个实盘策略，那么同一时期的回测结果应该能和实盘结果较为接近。只有在确认回测能够复现实盘表现之后，后续的研究、优化和过拟合控制才有坚实基础。

准确回测是基础。如果基础不可靠，后面的分析无论保守还是激进，都会变得不可靠。

快速开始
========

安装
----

hftbacktest 支持 Python 3.10+。可以用 ``pip`` 安装：

.. code-block:: console

   pip install hftbacktest

也可以从 GitHub 克隆最新开发版本：

.. code-block:: console

   git clone https://github.com/nkaz001/hftbacktest

数据来源与格式
--------------

请参考官方英文文档中的 `Data <https://hftbacktest.readthedocs.io/en/latest/data.html>`_ 和 `Data Preparation <https://hftbacktest.readthedocs.io/en/latest/tutorials/Data%20Preparation.html>`_。

支持者也托管了一些示例数据，可以在这里找到：`reach.stratosphere.capital/data/usdm <https://reach.stratosphere.capital/data/usdm/>`_。

一个简短示例
------------

下面的代码片段展示了 hftbacktest 中做市策略回测的大致形态。代码保持英文变量名和 API 名称，方便与官方文档和源码对应。

.. code-block:: python

    @njit
    def market_making_algo(hbt):
        asset_no = 0
        tick_size = hbt.depth(asset_no).tick_size
        lot_size = hbt.depth(asset_no).lot_size

        # in nanoseconds
        while hbt.elapse(10_000_000) == 0:
            hbt.clear_inactive_orders(asset_no)

            forecast = 0
            volatility = 0
            position = hbt.position(asset_no)
            risk = volatility * position

            depth = hbt.depth(asset_no)
            mid_price = (depth.best_bid + depth.best_ask) / 2.0
            reservation_price = mid_price + forecast - risk

            # 后续逻辑通常会基于 reservation_price、风险限制和当前挂单状态，
            # 生成新的 bid / ask 订单并等待订单回报。

翻译范围
========

当前中文版先以“能读、能构建、便于持续同步”为目标推进。代码块、API、类名、函数名、参数名、配置键和外部链接一般保留英文；解释性正文、章节标题和注释性说明翻译为中文。

推荐优先阅读和翻译的顺序：

* 首页与快速开始
* 数据格式与数据准备
* 订单成交模型
* 延迟模型
* JIT 编译开销
* 回测与实盘差异排查
* 教程 notebooks
* API Reference

.. toctree::
   :maxdepth: 2
   :caption: 用户指南

   data
   order_fill
   latency_models
   migration2
   jit_compilation_overhead
   debugging_backtesting_and_live_discrepancies
   market_maker_program

.. toctree::
   :maxdepth: 1
   :caption: 教程

   tutorials/Data Preparation
   tutorials/Getting Started
   tutorials/Working with Market Depth and Trades
   tutorials/Integrating Custom Data
   tutorials/Impact of Order Latency
   tutorials/Order Latency Data
   tutorials/Fusing Depth Data
   tutorials/Market Making with Alpha - Order Book Imbalance
   tutorials/Market Making with Alpha - Basis
   tutorials/Market Making with Alpha - APT
   tutorials/Queue-Based Market Making in Large Tick Size Assets
   tutorials/GLFT Market Making Model and Grid Trading
   tutorials/High-Frequency Grid Trading
   tutorials/High-Frequency Grid Trading - Comparison Across Other Exchanges
   tutorials/High-Frequency Grid Trading - Simplified from GLFT
   tutorials/Making Multiple Markets - Introduction
   tutorials/Making Multiple Markets
   tutorials/Probability Queue Models
   tutorials/Level-3 Backtesting
   tutorials/Accelerated Backtesting
   tutorials/Pricing Framework
   tutorials/examples

.. toctree::
   :maxdepth: 2
   :caption: API Reference

   Initialization <reference/initialization>
   Backtester <reference/backtester>
   Constants <reference/constants>
   Statistics <reference/stats>
   Data Validation <reference/data_validation>
   Data Utilities <reference/data_utilities>
   Index <genindex>

.. toctree::
   :maxdepth: 2
   :caption: 项目维护

   glossary
   translation_plan
   deploy_readthedocs
