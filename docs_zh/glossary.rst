术语表
======

本页用于统一中文版的核心术语。后续翻译时，优先沿用这里的译法。

.. list-table::
   :header-rows: 1
   :widths: 30 30 40

   * - 英文术语
     - 推荐中文
     - 说明
   * - backtesting
     - 回测
     - 在历史数据上模拟策略运行。
   * - market replay
     - 市场回放
     - 按历史行情顺序重放市场事件。
   * - feed latency
     - 行情延迟
     - 交易所行情从产生到本地接收之间的延迟。
   * - order latency
     - 订单延迟
     - 下单请求、撤单请求和订单回报之间的延迟。
   * - order entry latency
     - 订单进入延迟
     - 从本地发送订单请求到交易所撮合引擎处理请求之间的延迟。
   * - order response latency
     - 订单回报延迟
     - 从撮合引擎处理订单请求到本地收到订单回报之间的延迟。
   * - matching engine
     - 撮合引擎
     - 交易所用于撮合买卖订单的核心系统。
   * - queue position
     - 队列位置
     - 限价单在同一价格档位订单队列中的相对位置。
   * - order fill
     - 订单成交
     - 根据上下文也可译为“成交模拟”。
   * - exchange model
     - 交易所模型
     - 用于模拟订单在交易所中的成交行为。
   * - partial fill
     - 部分成交
     - 订单只有一部分数量成交。
   * - full execution
     - 完全成交
     - 订单全部数量成交。
   * - liquidity-taking order
     - 主动吃单
     - 主动与订单簿已有流动性成交的订单。
   * - market impact
     - 市场冲击
     - 订单自身对市场价格、深度或后续成交造成的影响。
   * - best bid / best ask
     - 最优买价 / 最优卖价
     - 当前订单簿中最好的买入和卖出报价。
   * - market depth
     - 市场深度
     - 订单簿中的买卖盘深度。
   * - order book
     - 订单簿
     - 记录买卖限价单的盘口结构。
   * - Level-2 Market-By-Price
     - L2 按价聚合盘口
     - 以价格档位为单位聚合数量。
   * - Level-3 Market-By-Order
     - L3 逐笔委托盘口
     - 以单笔委托为单位记录订单簿。
   * - market making
     - 做市
     - 同时或近似同时提供买卖报价以赚取价差。
   * - grid trading
     - 网格交易
     - 在多个价格层级挂单捕捉波动。
   * - tick-by-tick simulation
     - 逐 tick 仿真
     - 按最细粒度市场事件推进仿真。
   * - live trading
     - 实盘交易
     - 策略连接真实交易所执行。
   * - fair value
     - 公允价值
     - 策略估计的资产合理价格。
   * - reservation price
     - 保留价格
     - 做市模型中考虑 alpha 和库存风险后的目标报价中心。
   * - half spread
     - 半价差
     - 买卖价差的一半。
   * - alpha
     - alpha
     - 保留英文，指预测收益或短期信号。
   * - inventory risk
     - 库存风险
     - 持仓偏离目标时带来的价格风险。
   * - maker / taker
     - maker / taker
     - 交易所手续费角色，通常保留英文。
   * - SOA
     - SOA
     - Structure of Arrays，列式数组结构。
   * - AOS
     - AOS
     - Array of Structures，结构化数组结构。
   * - liquidity provider
     - 流动性提供者
     - 为市场提供挂单流动性的交易者或机构。
   * - rebate
     - 返佣
     - 交易所向满足条件的做市或流动性提供行为返还的费用。
