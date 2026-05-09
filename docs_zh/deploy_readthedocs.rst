发布到 Read the Docs
====================

目标地址
--------

建议 Read the Docs 项目名使用：

.. code-block:: text

   hftbacktest-zh

构建成功后，默认公开地址会是：

.. code-block:: text

   https://hftbacktest-zh.readthedocs.io/

仓库准备
--------

当前仓库已经包含中文站点所需配置：

* ``.readthedocs.yml``：Read the Docs 中文站构建配置，入口为 ``docs_zh/conf.py``。
* ``.readthedocs.en.yml``：官方英文站构建配置备份。
* ``docs_zh/``：中文文档源码。

Read the Docs 导入步骤
----------------------

1. 在 GitHub 创建公开仓库 ``hftbacktest-zh``。
2. 把当前仓库推送到该仓库。
3. 登录 https://readthedocs.org/。
4. 点击 ``Import a Project``。
5. 选择 GitHub 仓库 ``hftbacktest-zh``。
6. 项目 slug 填 ``hftbacktest-zh``。
7. 确认配置文件使用根目录的 ``.readthedocs.yml``。
8. 触发构建。

本地验证命令
------------

可以用下面的命令模拟 Read the Docs 构建：

.. code-block:: console

   uv run --with ./py-hftbacktest --with sphinx --with sphinx-rtd-theme --with nbsphinx --with ipython --with jupyter --with sphinxcontrib-jquery sphinx-build -T -b html -d /tmp/hftbacktest-zh-doctrees -D language=zh_CN docs_zh /tmp/hftbacktest-zh-html

当前本地验证结果：构建成功，无 warning。

注意事项
--------

* Read the Docs 的 ``hftbacktest-zh`` slug 如果已被占用，需要换一个名字，例如 ``hftbacktest-cn`` 或 ``hftbacktest-zh-cn``。
* 首次构建会编译 ``py-hftbacktest`` 的 Rust 扩展，耗时会比普通 Sphinx 文档更长。
* ``databento`` 是可选依赖，中文配置中已经通过 ``autodoc_mock_imports`` 处理。
