中文版 Roadmap
==============

目标
----

中文版的第一目标是方便中文读者系统阅读 hftbacktest 文档；第二目标是在质量稳定后，作为社区贡献反馈给官方项目。当前策略是先在 ``docs_zh/`` 中维护独立中文文档，英文原文不改动。

总体原则
--------

* 中文文档独立维护在 ``docs_zh/``，避免影响官方英文文档。
* 代码块、API 名称、参数名、类名、函数名、配置项和命令保持英文。
* 解释性正文、章节标题、提示语、图注和叙述性注释翻译为中文。
* 翻译优先保证技术准确性和可读性，不追求文学化表达。
* 遇到不确定的译法，先记录到 ``glossary.rst``，再统一替换。
* 每完成一个页面，都跑一次 Sphinx 构建，避免链接和语法问题积累。
* 每个阶段结束后，保留一份清晰状态表，方便后续同步 upstream。

目录策略
--------

第一阶段采用“独立中文站点”方案：

* ``docs_zh/index.rst`` 作为中文首页。
* ``docs_zh/glossary.rst`` 维护术语表。
* ``docs_zh/translation_plan.rst`` 维护 roadmap 和状态。
* 用户指南页面按英文文档同名复制到 ``docs_zh/``。
* API Reference 按英文文档同名复制到 ``docs_zh/reference/``。
* 教程 notebook 后续复制到 ``docs_zh/tutorials/`` 或从 ``examples/`` 同步生成。

如果后续要贡献给官方，再视维护者偏好调整为 Sphinx gettext、``docs/zh_CN/`` 或独立仓库链接。

阶段 0：基础设施
----------------

目标：让中文文档能独立构建、能持续维护。

状态：已开始。

交付物：

* ``docs_zh/conf.py``：中文 Sphinx 配置。
* ``docs_zh/Makefile``：中文构建入口。
* ``docs_zh/index.rst``：中文首页初版。
* ``docs_zh/glossary.rst``：术语表初版。
* ``docs_zh/translation_plan.rst``：本 roadmap。

验收标准：

* 可以运行 ``sphinx-build -M html docs_zh docs_zh/_build``。
* 构建结果可以打开 ``docs_zh/_build/html/index.html`` 阅读。
* 首页、术语表、roadmap 在左侧导航中可见。

阶段 1：核心用户指南
--------------------

目标：先翻译理解 hftbacktest 必需的核心概念，让自己能顺畅阅读和使用。

优先级顺序：

1. ``docs/data.rst`` -> ``docs_zh/data.rst``
2. ``docs/order_fill.rst`` -> ``docs_zh/order_fill.rst``
3. ``docs/latency_models.rst`` -> ``docs_zh/latency_models.rst``
4. ``docs/migration2.rst`` -> ``docs_zh/migration2.rst``

原因：

* ``data.rst`` 是最大页面，也是理解输入数据格式的基础。
* ``order_fill.rst`` 和 ``latency_models.rst`` 是 hftbacktest 相对普通回测框架最核心的差异。
* ``migration2.rst`` 有助于理解当前版本和历史版本的数据格式变化。

验收标准：

* 每个页面接入中文首页的 User Guide toctree。
* 每个页面中的英文段落已翻译，代码和 API 名称保持原样。
* 图示、表格、交叉引用和外链能正常渲染。
* 阶段结束后跑一次完整构建，无 error。

阶段 2：补齐用户指南
--------------------

目标：补齐剩余 `.rst` 用户指南，让中文站点覆盖官方 User Guide。

页面清单：

* ``docs/jit_compilation_overhead.rst`` -> ``docs_zh/jit_compilation_overhead.rst``
* ``docs/debugging_backtesting_and_live_discrepancies.rst`` -> ``docs_zh/debugging_backtesting_and_live_discrepancies.rst``
* ``docs/market_maker_program.rst`` -> ``docs_zh/market_maker_program.rst``
* ``docs/tutorials/examples.rst`` -> ``docs_zh/tutorials/examples.rst``

验收标准：

* 中文 User Guide 与英文 User Guide 页面数量一致。
* 页面标题、正文、提示说明已中文化。
* 外部交易所、API、项目名保留官方英文名称。

阶段 3：教程 Notebook
-------------------------

目标：翻译教程 notebook 的说明文字，保留代码可运行性。

来源页面：

* ``examples/Data Preparation.ipynb``
* ``examples/Getting Started.ipynb``
* ``examples/Working with Market Depth and Trades.ipynb``
* ``examples/Integrating Custom Data.ipynb``
* ``examples/Making Multiple Markets - Introduction.ipynb``
* ``examples/High-Frequency Grid Trading.ipynb``
* ``examples/High-Frequency Grid Trading - Comparison Across Other Exchanges.ipynb``
* ``examples/High-Frequency Grid Trading - Simplified from GLFT.ipynb``
* ``examples/Impact of Order Latency.ipynb``
* ``examples/Order Latency Data.ipynb``
* ``examples/GLFT Market Making Model and Grid Trading.ipynb``
* ``examples/Making Multiple Markets.ipynb``
* ``examples/Probability Queue Models.ipynb``
* ``examples/Risk Mitigation through Price Protection in Extreme Market Conditions.ipynb``
* ``examples/Level-3 Backtesting.ipynb``
* ``examples/Market Making with Alpha - Order Book Imbalance.ipynb``
* ``examples/Market Making with Alpha - Basis.ipynb``
* ``examples/Market Making with Alpha - APT.ipynb``
* ``examples/Queue-Based Market Making in Large Tick Size Assets.ipynb``
* ``examples/Fusing Depth Data.ipynb``
* ``examples/Accelerated Backtesting.ipynb``
* ``examples/Pricing Framework.ipynb``

处理策略：

* 复制 notebook 到 ``docs_zh/tutorials/``。
* 只翻译 markdown cell。
* 代码 cell 保持原样，除非原英文注释严重影响理解。
* notebook 输出可以保留，避免翻译过程引入执行环境依赖。
* 文件名第一版保留英文，减少 toctree、图片和链接问题。

验收标准：

* 中文教程能在 Sphinx 中渲染。
* markdown 说明基本中文化。
* 代码 cell 未被无意修改。
* 每批 notebook 构建成功。

建议批次：

1. 入门批：Data Preparation、Getting Started、Working with Market Depth and Trades。
2. 数据与延迟批：Integrating Custom Data、Impact of Order Latency、Order Latency Data、Fusing Depth Data。
3. 做市核心批：Market Making with Alpha 系列、Queue-Based Market Making、GLFT。
4. 网格与多市场批：High-Frequency Grid Trading 系列、Making Multiple Markets 系列。
5. 高级批：Accelerated Backtesting、Pricing Framework、Level-3 Backtesting、Risk Mitigation。

阶段 4：API Reference
-------------------------

目标：让 API Reference 在中文站点中完整可访问。

页面清单：

* ``docs/reference/initialization.rst``
* ``docs/reference/backtester.rst``
* ``docs/reference/constants.rst``
* ``docs/reference/stats.rst``
* ``docs/reference/data_validation.rst``
* ``docs/reference/data_utilities.rst``
* ``docs/reference/hftbacktest.data.utils.binancefutures.rst``
* ``docs/reference/hftbacktest.data.utils.binancehistmktdata.rst``
* ``docs/reference/hftbacktest.data.utils.databento.rst``
* ``docs/reference/hftbacktest.data.utils.difforderbooksnapshot.rst``
* ``docs/reference/hftbacktest.data.utils.migration2.rst``
* ``docs/reference/hftbacktest.data.utils.snapshot.rst``
* ``docs/reference/hftbacktest.data.utils.tardis.rst``

处理策略：

* API 对象名和 ``.. autoclass::``、``.. automodule::``、``.. autofunction::`` 指令保持原样。
* 翻译页面标题、章节标题、简短说明。
* 如果 API 文档正文来自 docstring，第一版不强行翻译源码 docstring。

验收标准：

* 中文 API Reference toctree 与英文版本基本一致。
* autodoc 页面能构建成功。
* 不因为翻译破坏 Sphinx 指令。

阶段 5：质量校对
----------------

目标：让中文版从“可读”提升到“可信”。

校对清单：

* 术语表统一：检查同一术语是否有多个译法。
* 技术准确性：重点校对数据格式、延迟模型、队列模型、成交模型。
* 链接检查：检查内部链接、外部链接和图片引用。
* 代码保护：确认代码块、API 名称和 notebook code cell 没有误翻。
* 可读性：长句拆分，减少直译腔。
* 版本标记：说明中文版对应的 upstream commit 或版本。

验收标准：

* 完整构建无 error。
* 关键页面至少二次校对。
* 术语表覆盖主要高频交易和回测概念。
* 首页明确说明“英文官方文档为准”。

阶段 6：社区贡献
----------------

目标：把中文版以合适方式反馈给 hftbacktest 社区。

推荐路径：

1. 在自己的 fork 或独立仓库中发布中文文档。
2. 在 README 或 GitHub Pages / ReadTheDocs 上提供在线访问地址。
3. 开一个官方 issue，说明中文文档目标、当前完成范围、维护方式。
4. 询问维护者偏好：

   * 是否愿意在官方 README 中增加中文文档链接。
   * 是否接受 ``docs_zh/`` 目录。
   * 是否更偏好 Sphinx gettext / ``docs/locale/zh_CN``。
   * 是否希望中文文档独立维护，官方只保留链接。

5. 根据维护者反馈再开小 PR，不一次性提交巨大翻译。

状态表
------

.. list-table::
   :header-rows: 1
   :widths: 34 14 18 34

   * - 页面或任务
     - 阶段
     - 状态
     - 备注
   * - ``docs_zh`` 构建骨架
     - 0
     - 已完成
     - 已能独立构建。
   * - ``index.rst``
     - 0 / 1
     - 进行中
     - 首页已有初版，完整示例后续补齐。
   * - ``glossary.rst``
     - 0 / 5
     - 进行中
     - 后续随翻译持续补充。
   * - ``data.rst``
     - 1
     - 已完成
     - 第一版已翻译并接入中文目录。
   * - ``order_fill.rst``
     - 1
     - 已完成
     - 第一版已翻译并接入中文目录。
   * - ``latency_models.rst``
     - 1
     - 已完成
     - 第一版已翻译并接入中文目录。
   * - ``migration2.rst``
     - 1
     - 已完成
     - 第一版已翻译并接入中文目录。
   * - 剩余用户指南
     - 2
     - 已完成
     - JIT、实盘差异排查、做市商计划已完成第一版。
   * - 教程 notebooks
     - 3
     - 进行中
     - 示例索引已翻译；notebook 正文未开始。
   * - API Reference
     - 4
     - 已完成
     - RST 壳页面已中文化，autodoc 指令保持不变。
   * - 全站校对
     - 5
     - 未开始
     - 术语、链接、构建、版本标记。
   * - 社区反馈
     - 6
     - 未开始
     - 完成核心页面后再开 issue。

常用命令
--------

构建中文版：

.. code-block:: console

   uv run --with sphinx --with sphinx-rtd-theme --with nbsphinx --with ipython --with jupyter --with sphinxcontrib-jquery sphinx-build -M html docs_zh docs_zh/_build

打开本地页面：

.. code-block:: console

   docs_zh/_build/html/index.html

后续维护建议
------------

每完成一批翻译，建议单独提交一次 commit。commit 粒度可以按页面或阶段划分，例如：

* ``docs_zh: translate data guide``
* ``docs_zh: translate order fill and latency models``
* ``docs_zh: add translated getting started tutorial``
* ``docs_zh: sync glossary terms``

这样后续无论自己维护、开 PR，还是回滚某批翻译，都会更清楚。
