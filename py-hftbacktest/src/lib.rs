use std::{ffi::c_void, mem::size_of, ptr::slice_from_raw_parts_mut};

pub use backtest::*;
pub use depth::*;
pub use fuse::*;
#[cfg(feature = "live")]
use hftbacktest::live::{Instrument, LiveBotBuilder};
use hftbacktest::{
    backtest::{
        Asset,
        Backtest,
        DataSource,
        assettype::{InverseAsset, LinearAsset},
        data::{Data, DataPtr, FeedLatencyAdjustment, Reader, read_npz_file},
        models::{
            CommonFees,
            ConstantLatency,
            FlatPerTradeFeeModel,
            IntpOrderLatency,
            L3FIFOQueueModel,
            LogProbQueueFunc,
            LogProbQueueFunc2,
            OrderLatencyRow,
            PowerProbQueueFunc,
            PowerProbQueueFunc2,
            PowerProbQueueFunc3,
            ProbQueueModel,
            RiskAdverseQueueModel,
            TradingQtyFeeModel,
            TradingValueFeeModel,
        },
        order::order_bus,
        proc::{
            L3Local,
            L3NoPartialFillExchange,
            Local,
            LocalProcessor,
            NoPartialFillExchange,
            PartialFillExchange,
            Processor,
        },
        state::State,
    },
    prelude::{ApplySnapshot, Event, HashMapMarketDepth, ROIVectorMarketDepth},
};
use hftbacktest_derive::build_asset;
pub use order::*;
use pyo3::{
    PyTypeInfo,
    exceptions::{PyDeprecationWarning, PyValueError},
    ffi::c_str,
    prelude::*,
};

#[cfg(feature = "live")]
use crate::live::{HashMapMarketDepthLiveBot, ROIVectorMarketDepthLiveBot};

mod backtest;
mod depth;
mod fuse;
#[cfg(feature = "live")]
mod live;
mod order;

#[derive(Clone)]
pub enum AssetType {
    LinearAsset { contract_size: f64 },
    InverseAsset { contract_size: f64 },
}

#[derive(Clone)]
pub enum LatencyModel {
    ConstantLatency {
        entry_latency: i64,
        resp_latency: i64,
    },
    IntpOrderLatency {
        data: Vec<DataSource<OrderLatencyRow>>,
        latency_offset: i64,
    },
}

#[derive(Clone)]
pub enum QueueModel {
    RiskAdverseQueueModel {},
    PowerProbQueueModel { n: f64 },
    LogProbQueueModel {},
    LogProbQueueModel2 {},
    PowerProbQueueModel2 { n: f64 },
    PowerProbQueueModel3 { n: f64 },
    L3FIFOQueueModel {},
}

#[derive(Clone)]
pub enum ExchangeKind {
    NoPartialFillExchange {},
    PartialFillExchange {},
}

#[derive(Clone)]
pub enum FeeModel {
    TradingValueFeeModel { fees: CommonFees },
    TradingQtyFeeModel { fees: CommonFees },
    FlatPerTradeFeeModel { fees: CommonFees },
}

/// Builds a backtesting asset.
#[pyclass(subclass)]
pub struct BacktestAsset {
    data: Vec<DataSource<Event>>,
    asset_type: AssetType,
    latency_model: LatencyModel,
    queue_model: QueueModel,
    exch_kind: ExchangeKind,
    tick_size: f64,
    lot_size: f64,
    last_trades_cap: usize,
    roi_lb: f64,
    roi_ub: f64,
    initial_snapshot: Option<DataSource<Event>>,
    fee_model: FeeModel,
    latency_offset: i64,
    parallel_load: bool,
}

unsafe impl Send for BacktestAsset {}
unsafe impl Sync for BacktestAsset {}

#[pymethods]
impl BacktestAsset {
    /// 构造 `BacktestAsset` 实例。
    #[allow(clippy::new_without_default)]
    #[new]
    pub fn new() -> Self {
        Self {
            data: Vec::new(),
            latency_model: LatencyModel::ConstantLatency {
                entry_latency: 0,
                resp_latency: 0,
            },
            asset_type: AssetType::LinearAsset { contract_size: 1.0 },
            queue_model: QueueModel::LogProbQueueModel2 {},
            tick_size: 0.0,
            lot_size: 0.0,
            exch_kind: ExchangeKind::NoPartialFillExchange {},
            last_trades_cap: 0,
            roi_lb: 0.0,
            roi_ub: 0.0,
            initial_snapshot: None,
            fee_model: FeeModel::TradingValueFeeModel {
                fees: CommonFees::new(0.0, 0.0),
            },
            latency_offset: 0,
            parallel_load: true,
        }
    }

    /// 设置是否在回测过程中并行加载下一份数据。这可以通过减少数据加载时间加快回测，
    /// 但也会增加内存使用。
    ///
    /// Args:
    ///     preload: 是否在回测过程中并行预加载下一份数据。默认值为 `True`。
    pub fn parallel_load(mut slf: PyRefMut<Self>, parallel_load: bool) -> PyRefMut<Self> {
        slf.parallel_load = parallel_load;
        slf
    }

    /// 设置延迟偏移量，用于按指定数值调整行情延迟。在跨交易所回测中尤其有用，
    /// 例如行情数据采集地点与策略实际运行地点不同。
    ///
    /// Args:
    ///     latency_offset: 用于调整行情延迟的偏移量。默认值为 `0`。
    pub fn latency_offset(mut slf: PyRefMut<Self>, latency_offset: i64) -> PyRefMut<Self> {
        slf.latency_offset = latency_offset;
        slf
    }

    /// 设置 `ROIVectorMarketDepth <https://docs.rs/hftbacktest/latest/hftbacktest/depth/struct.ROIVectorMarketDepth.html>`_
    /// 的价格下界。仅在构建 `ROIVectorMarketDepthBacktest` 时有效。
    ///
    /// Args:
    ///     roi_lb: 关注价格范围的下界。
    pub fn roi_lb(mut slf: PyRefMut<Self>, roi_lb: f64) -> PyRefMut<Self> {
        slf.roi_lb = roi_lb;
        slf
    }

    /// 设置 `ROIVectorMarketDepth <https://docs.rs/hftbacktest/latest/hftbacktest/depth/struct.ROIVectorMarketDepth.html>`_
    /// 的价格上界。仅在构建 `ROIVectorMarketDepthBacktest` 时有效。
    ///
    /// Args:
    ///     roi_ub: 关注价格范围的上界。
    pub fn roi_ub(mut slf: PyRefMut<Self>, roi_ub: f64) -> PyRefMut<Self> {
        slf.roi_ub = roi_ub;
        slf
    }

    pub fn add_file(mut slf: PyRefMut<Self>, data: String) -> PyRefMut<Self> {
        slf.data.push(DataSource::File(data));
        slf
    }

    pub fn _add_data_ndarray(mut slf: PyRefMut<Self>, data: usize, len: usize) -> PyRefMut<Self> {
        let arr = slice_from_raw_parts_mut(data as *mut u8, len * size_of::<Event>());
        let data = unsafe { Data::<Event>::from_data_ptr(DataPtr::from_ptr(arr), 0) };
        slf.data.push(DataSource::Data(data));
        slf
    }

    /// 将资产设置为 `LinearAsset <https://docs.rs/hftbacktest/latest/hftbacktest/backtest/assettype/struct.LinearAsset.html>`_。
    ///
    /// Args:
    ///     contract_size: 资产合约乘数。
    pub fn linear_asset(mut slf: PyRefMut<Self>, contract_size: f64) -> PyRefMut<Self> {
        slf.asset_type = AssetType::LinearAsset { contract_size };
        slf
    }

    /// 将资产设置为 `InverseAsset <https://docs.rs/hftbacktest/latest/hftbacktest/backtest/assettype/struct.InverseAsset.html>`_。
    ///
    /// Args:
    ///     contract_size: 资产合约乘数。
    pub fn inverse_asset(mut slf: PyRefMut<Self>, contract_size: f64) -> PyRefMut<Self> {
        slf.asset_type = AssetType::InverseAsset { contract_size };
        slf
    }

    /// 已废弃：请改用 `constant_order_latency`。
    ///
    /// 使用 `ConstantLatency <https://docs.rs/hftbacktest/latest/hftbacktest/backtest/models/struct.ConstantLatency.html>`_
    /// 作为订单延迟模型。参数单位应与数据时间戳单位一致。HftBacktest 通常使用纳秒。
    ///
    /// Args:
    ///     entry_latency: 订单进入延迟。
    ///     resp_latency: 订单回报延迟。
    pub fn constant_latency(
        mut slf: PyRefMut<Self>,
        entry_latency: i64,
        resp_latency: i64,
    ) -> PyRefMut<Self> {
        Python::attach(|py| {
            PyErr::warn(
                py,
                &PyDeprecationWarning::type_object(py),
                c_str!("constant_latency() is deprecated; use constant_order_latency()."),
                1,
            )
        })
        .unwrap();

        slf.latency_model = LatencyModel::ConstantLatency {
            entry_latency,
            resp_latency,
        };
        slf
    }

    /// 使用 `ConstantLatency <https://docs.rs/hftbacktest/latest/hftbacktest/backtest/models/struct.ConstantLatency.html>`_
    /// 作为订单延迟模型。参数单位应与数据时间戳单位一致。HftBacktest 通常使用纳秒。
    ///
    /// Args:
    ///     entry_latency: 订单进入延迟。
    ///     resp_latency: 订单回报延迟。
    pub fn constant_order_latency(
        mut slf: PyRefMut<Self>,
        entry_latency: i64,
        resp_latency: i64,
    ) -> PyRefMut<Self> {
        slf.latency_model = LatencyModel::ConstantLatency {
            entry_latency,
            resp_latency,
        };
        slf
    }

    /// 使用 `IntpOrderLatency <https://docs.rs/hftbacktest/latest/hftbacktest/backtest/models/struct.IntpOrderLatency.html>`_
    /// 作为订单延迟模型。请参考数据格式说明。历史延迟数据的单位应与数据时间戳单位一致。
    /// HftBacktest 通常使用纳秒。
    ///
    /// Args:
    ///     data: `npz` 格式历史订单延迟数据文件路径列表。
    ///     latency_offset: 延迟偏移量，用于按指定数值调整订单进入延迟和订单回报延迟。
    ///                     在跨交易所回测中尤其有用，例如行情数据采集地点与策略实际运行地点不同。
    pub fn intp_order_latency(
        mut slf: PyRefMut<Self>,
        data: Vec<String>,
        latency_offset: i64,
    ) -> PyRefMut<Self> {
        slf.latency_model = LatencyModel::IntpOrderLatency {
            data: data
                .iter()
                .map(|file| DataSource::File(file.to_string()))
                .collect(),
            latency_offset,
        };
        slf
    }

    pub fn _intp_order_latency_ndarray(
        mut slf: PyRefMut<Self>,
        data: usize,
        len: usize,
        latency_offset: i64,
    ) -> PyRefMut<Self> {
        let arr = slice_from_raw_parts_mut(data as *mut u8, len * size_of::<OrderLatencyRow>());
        let data = unsafe { Data::<OrderLatencyRow>::from_data_ptr(DataPtr::from_ptr(arr), 0) };
        slf.latency_model = LatencyModel::IntpOrderLatency {
            data: vec![DataSource::Data(data)],
            latency_offset,
        };
        slf
    }

    /// 使用 `RiskAdverseQueueModel <https://docs.rs/hftbacktest/latest/hftbacktest/backtest/models/struct.RiskAdverseQueueModel.html>`_
    /// 作为队列位置模型。
    ///
    /// * `Order Fill - RiskAdverseQueueModel <https://hftbacktest.readthedocs.io/en/latest/order_fill.html#riskaversequeuemodel>`_
    pub fn risk_adverse_queue_model(mut slf: PyRefMut<Self>) -> PyRefMut<Self> {
        slf.queue_model = QueueModel::RiskAdverseQueueModel {};
        slf
    }

    /// 使用 `LogProbQueueModel` 作为队列位置模型。
    ///
    /// 详情见下方链接。
    ///
    /// * `Order Fill - ProbQueueModel <https://hftbacktest.readthedocs.io/en/latest/order_fill.html#probqueuemodel>`_
    /// * `ProbQueueModel <https://docs.rs/hftbacktest/latest/hftbacktest/backtest/models/struct.ProbQueueModel.html>`_
    /// * `LogProbQueueFunc <https://docs.rs/hftbacktest/latest/hftbacktest/backtest/models/struct.LogProbQueueFunc.html>`_
    pub fn log_prob_queue_model(mut slf: PyRefMut<Self>) -> PyRefMut<Self> {
        slf.queue_model = QueueModel::LogProbQueueModel {};
        slf
    }

    /// 使用 `LogProbQueueModel2` 作为队列位置模型。
    ///
    /// 详情见下方链接。
    ///
    /// * `Order Fill - ProbQueueModel <https://hftbacktest.readthedocs.io/en/latest/order_fill.html#probqueuemodel>`_
    /// * `ProbQueueModel <https://docs.rs/hftbacktest/latest/hftbacktest/backtest/models/struct.ProbQueueModel.html>`_
    /// * `LogProbQueueFunc2 <https://docs.rs/hftbacktest/latest/hftbacktest/backtest/models/struct.LogProbQueueFunc2.html>`_
    pub fn log_prob_queue_model2(mut slf: PyRefMut<Self>) -> PyRefMut<Self> {
        slf.queue_model = QueueModel::LogProbQueueModel2 {};
        slf
    }

    /// 使用 `PowerProbQueueModel` 作为队列位置模型。
    ///
    /// 详情见下方链接。
    ///
    /// * `Order Fill - ProbQueueModel <https://hftbacktest.readthedocs.io/en/latest/order_fill.html#probqueuemodel>`_
    /// * `ProbQueueModel <https://docs.rs/hftbacktest/latest/hftbacktest/backtest/models/struct.ProbQueueModel.html>`_
    /// * `PowerProbQueueFunc <https://docs.rs/hftbacktest/latest/hftbacktest/backtest/models/struct.PowerProbQueueFunc.html>`_
    pub fn power_prob_queue_model(mut slf: PyRefMut<Self>, n: f64) -> PyRefMut<Self> {
        slf.queue_model = QueueModel::PowerProbQueueModel { n };
        slf
    }

    /// 使用 `PowerProbQueueModel2` 作为队列位置模型。
    ///
    /// 详情见下方链接。
    ///
    /// * `Order Fill - ProbQueueModel <https://hftbacktest.readthedocs.io/en/latest/order_fill.html#probqueuemodel>`_
    /// * `ProbQueueModel <https://docs.rs/hftbacktest/latest/hftbacktest/backtest/models/struct.ProbQueueModel.html>`_
    /// * `PowerProbQueueFunc2 <https://docs.rs/hftbacktest/latest/hftbacktest/backtest/models/struct.PowerProbQueueFunc2.html>`_
    pub fn power_prob_queue_model2(mut slf: PyRefMut<Self>, n: f64) -> PyRefMut<Self> {
        slf.queue_model = QueueModel::PowerProbQueueModel2 { n };
        slf
    }

    /// 使用 `PowerProbQueueModel3` 作为队列位置模型。
    ///
    /// 详情见下方链接。
    ///
    /// * `Order Fill - ProbQueueModel <https://hftbacktest.readthedocs.io/en/latest/order_fill.html#probqueuemodel>`_
    /// * `ProbQueueModel <https://docs.rs/hftbacktest/latest/hftbacktest/backtest/models/struct.ProbQueueModel.html>`_
    /// * `PowerProbQueueFunc3 <https://docs.rs/hftbacktest/latest/hftbacktest/backtest/models/struct.PowerProbQueueFunc3.html>`_
    pub fn power_prob_queue_model3(mut slf: PyRefMut<Self>, n: f64) -> PyRefMut<Self> {
        slf.queue_model = QueueModel::PowerProbQueueModel3 { n };
        slf
    }

    /// 使用 `L3FIFOQueueModel` 作为队列位置模型。
    ///
    /// 详情见下方链接。
    ///
    /// * `Order Fill <https://hftbacktest.readthedocs.io/en/latest/order_fill.html>`_
    /// * `L3FIFOQueueModel <https://docs.rs/hftbacktest/latest/hftbacktest/backtest/models/struct.L3FIFOQueueModel.html>`_
    pub fn l3_fifo_queue_model(mut slf: PyRefMut<Self>) -> PyRefMut<Self> {
        slf.queue_model = QueueModel::L3FIFOQueueModel {};
        slf
    }

    /// 设置初始订单簿快照。
    pub fn initial_snapshot(mut slf: PyRefMut<Self>, file: String) -> PyRefMut<Self> {
        slf.initial_snapshot = Some(DataSource::File(file));
        slf
    }

    pub fn _initial_snapshot_ndarray(
        mut slf: PyRefMut<Self>,
        data: usize,
        len: usize,
    ) -> PyRefMut<Self> {
        let arr = slice_from_raw_parts_mut(data as *mut u8, len * size_of::<Event>());
        let data = unsafe { Data::<Event>::from_data_ptr(DataPtr::from_ptr(arr), 0) };
        slf.initial_snapshot = Some(DataSource::Data(data));
        slf
    }

    /// 设置资产 tick size。
    pub fn tick_size(mut slf: PyRefMut<Self>, tick_size: f64) -> PyRefMut<Self> {
        slf.tick_size = tick_size;
        slf
    }

    /// 设置资产 lot size。
    pub fn lot_size(mut slf: PyRefMut<Self>, lot_size: f64) -> PyRefMut<Self> {
        slf.lot_size = lot_size;
        slf
    }

    /// 使用 `NoPartiallFillExchange <https://docs.rs/hftbacktest/latest/hftbacktest/backtest/proc/struct.NoPartialFillExchange.html>`_
    /// 作为交易所模型。
    pub fn no_partial_fill_exchange(mut slf: PyRefMut<Self>) -> PyRefMut<Self> {
        slf.exch_kind = ExchangeKind::NoPartialFillExchange {};
        slf
    }

    /// 使用 `PartiallFillExchange <https://docs.rs/hftbacktest/latest/hftbacktest/backtest/proc/struct.PartialFillExchange.html>`_
    /// 作为交易所模型。
    pub fn partial_fill_exchange(mut slf: PyRefMut<Self>) -> PyRefMut<Self> {
        slf.exch_kind = ExchangeKind::PartialFillExchange {};
        slf
    }

    /// 设置保存最近市场成交的 vector 初始容量。默认值为 `0`，表示不保存最近成交。
    pub fn last_trades_capacity(mut slf: PyRefMut<Self>, capacity: usize) -> PyRefMut<Self> {
        slf.last_trades_cap = capacity;
        slf
    }

    /// 使用 `TradingValueFeeModel <https://docs.rs/hftbacktest/latest/hftbacktest/backtest/models/struct.TradingValueFeeModel.html>`_。
    /// 负手续费表示返佣。
    pub fn trading_value_fee_model(
        mut slf: PyRefMut<Self>,
        maker_fee: f64,
        taker_fee: f64,
    ) -> PyRefMut<Self> {
        slf.fee_model = FeeModel::TradingValueFeeModel {
            fees: CommonFees::new(maker_fee, taker_fee),
        };
        slf
    }

    /// 使用 `TradingQtyFeeModel <https://docs.rs/hftbacktest/latest/hftbacktest/backtest/models/struct.TradingQtyFeeModel.html>`_。
    /// 负手续费表示返佣。
    pub fn trading_qty_fee_model(
        mut slf: PyRefMut<Self>,
        maker_fee: f64,
        taker_fee: f64,
    ) -> PyRefMut<Self> {
        slf.fee_model = FeeModel::TradingQtyFeeModel {
            fees: CommonFees::new(maker_fee, taker_fee),
        };
        slf
    }

    /// 使用 `FlatPerTradeFeeModel <https://docs.rs/hftbacktest/latest/hftbacktest/backtest/models/struct.FlatPerTradeFeeModel.html>`_。
    /// 负手续费表示返佣。
    pub fn flat_per_trade_fee_model(
        mut slf: PyRefMut<Self>,
        maker_fee: f64,
        taker_fee: f64,
    ) -> PyRefMut<Self> {
        slf.fee_model = FeeModel::FlatPerTradeFeeModel {
            fees: CommonFees::new(maker_fee, taker_fee),
        };
        slf
    }
}

#[pymodule]
fn _hftbacktest(m: &Bound<'_, PyModule>) -> PyResult<()> {
    m.add_function(wrap_pyfunction!(build_hashmap_backtest, m)?)?;
    m.add_function(wrap_pyfunction!(build_roivec_backtest, m)?)?;
    #[cfg(feature = "live")]
    m.add_function(wrap_pyfunction!(build_hashmap_livebot, m)?)?;
    #[cfg(feature = "live")]
    m.add_function(wrap_pyfunction!(build_roivec_livebot, m)?)?;
    m.add_class::<BacktestAsset>()?;
    m.add_class::<LiveInstrument>()?;
    Ok(())
}

type LogProbQueueModelFunc = LogProbQueueFunc;
type LogProbQueueModel2Func = LogProbQueueFunc2;
type PowerProbQueueModelFunc = PowerProbQueueFunc;
type PowerProbQueueModel2Func = PowerProbQueueFunc2;
type PowerProbQueueModel3Func = PowerProbQueueFunc3;

#[pyfunction]
pub fn build_hashmap_backtest(assets: Vec<PyRefMut<BacktestAsset>>) -> PyResult<usize> {
    let mut local = Vec::new();
    let mut exch = Vec::new();
    let mut readers = Vec::new();
    for asset in assets {
        if let (QueueModel::L3FIFOQueueModel {}, ExchangeKind::PartialFillExchange {}) =
            (&asset.queue_model, &asset.exch_kind)
        {
            return PyResult::Err(PyErr::new::<PyValueError, _>(
                "L3PartialFillExchange is unsupported.",
            ));
        }

        let asst = build_asset!(
            asset,
            HashMapMarketDepth,
            [
                LinearAsset { contract_size },
                InverseAsset { contract_size }
            ],
            [
                ConstantLatency {
                    entry_latency,
                    resp_latency
                },
                IntpOrderLatency {
                    data,
                    latency_offset
                }
            ],
            [
                RiskAdverseQueueModel {},
                LogProbQueueModel {},
                LogProbQueueModel2 {},
                PowerProbQueueModel { n },
                PowerProbQueueModel2 { n },
                PowerProbQueueModel3 { n },
                L3FIFOQueueModel {}
            ],
            [NoPartialFillExchange {}, PartialFillExchange {}],
            [
                TradingValueFeeModel { fees },
                TradingQtyFeeModel { fees },
                FlatPerTradeFeeModel { fees },
            ]
        );
        local.push(asst.local);
        exch.push(asst.exch);
        readers.push(asst.reader);
    }

    let hbt = Backtest::new(local, exch, readers);
    Ok(Box::into_raw(Box::new(hbt)) as *mut c_void as usize)
}

#[pyfunction]
pub fn build_roivec_backtest(assets: Vec<PyRefMut<BacktestAsset>>) -> PyResult<usize> {
    let mut local = Vec::new();
    let mut exch = Vec::new();
    let mut readers = Vec::new();

    for asset in assets {
        if let (QueueModel::L3FIFOQueueModel {}, ExchangeKind::PartialFillExchange {}) =
            (&asset.queue_model, &asset.exch_kind)
        {
            return PyResult::Err(PyErr::new::<PyValueError, _>(
                "L3PartialFillExchange is unsupported.",
            ));
        }

        let asst = build_asset!(
            asset,
            ROIVectorMarketDepth,
            [
                LinearAsset { contract_size },
                InverseAsset { contract_size }
            ],
            [
                ConstantLatency {
                    entry_latency,
                    resp_latency
                },
                IntpOrderLatency {
                    data,
                    latency_offset
                }
            ],
            [
                RiskAdverseQueueModel {},
                LogProbQueueModel {},
                LogProbQueueModel2 {},
                PowerProbQueueModel { n },
                PowerProbQueueModel2 { n },
                PowerProbQueueModel3 { n },
                L3FIFOQueueModel {}
            ],
            [NoPartialFillExchange {}, PartialFillExchange {}],
            [
                TradingValueFeeModel { fees },
                TradingQtyFeeModel { fees },
                FlatPerTradeFeeModel { fees },
            ]
        );
        local.push(asst.local);
        exch.push(asst.exch);
        readers.push(asst.reader);
    }

    let hbt = Backtest::new(local, exch, readers);
    Ok(Box::into_raw(Box::new(hbt)) as *mut c_void as usize)
}

/// Builds a live trading instrument.
#[pyclass]
pub struct LiveInstrument {
    connector_name: String,
    symbol: String,
    tick_size: f64,
    lot_size: f64,
    last_trades_cap: usize,
    roi_lb: f64,
    roi_ub: f64,
}

unsafe impl Send for LiveInstrument {}

#[pymethods]
impl LiveInstrument {
    /// Constructs an instance of `LiveInstrument`.
    #[allow(clippy::new_without_default)]
    #[new]
    pub fn new() -> Self {
        Self {
            connector_name: String::new(),
            symbol: String::new(),
            tick_size: 0.0,
            lot_size: 0.0,
            last_trades_cap: 0,
            roi_lb: 0.0,
            roi_ub: 0.0,
        }
    }

    /// Sets a connector name.
    pub fn connector(mut slf: PyRefMut<Self>, name: String) -> PyRefMut<Self> {
        slf.connector_name = name;
        slf
    }

    /// Sets a symbol.
    pub fn symbol(mut slf: PyRefMut<Self>, symbol: String) -> PyRefMut<Self> {
        slf.symbol = symbol;
        slf
    }

    /// Sets the tick size of the asset.
    pub fn tick_size(mut slf: PyRefMut<Self>, tick_size: f64) -> PyRefMut<Self> {
        slf.tick_size = tick_size;
        slf
    }

    /// Sets the lot size of the asset.
    pub fn lot_size(mut slf: PyRefMut<Self>, lot_size: f64) -> PyRefMut<Self> {
        slf.lot_size = lot_size;
        slf
    }

    /// Sets the initial capacity of the vector storing the last market trades.
    /// The default value is `0`, indicating that no last trades are stored.
    pub fn last_trades_capacity(mut slf: PyRefMut<Self>, capacity: usize) -> PyRefMut<Self> {
        slf.last_trades_cap = capacity;
        slf
    }

    /// Sets the lower bound price of the `ROIVectorMarketDepth <https://docs.rs/hftbacktest/latest/hftbacktest/depth/struct.ROIVectorMarketDepth.html>`_.
    /// Only valid if `ROIVectorMarketDepthLiveBot` is built.
    ///
    /// Args:
    ///     roi_lb: the lower bound price of the range of interest.
    pub fn roi_lb(mut slf: PyRefMut<Self>, roi_lb: f64) -> PyRefMut<Self> {
        slf.roi_lb = roi_lb;
        slf
    }

    /// Sets the upper bound price of the `ROIVectorMarketDepth <https://docs.rs/hftbacktest/latest/hftbacktest/depth/struct.ROIVectorMarketDepth.html>`_.
    /// Only valid if `ROIVectorMarketDepthLiveBot` is built.
    ///
    /// Args:
    ///     roi_ub: the upper bound price of the range of interest.
    pub fn roi_ub(mut slf: PyRefMut<Self>, roi_ub: f64) -> PyRefMut<Self> {
        slf.roi_ub = roi_ub;
        slf
    }
}

#[cfg(feature = "live")]
#[pyfunction]
pub fn build_hashmap_livebot(instruments: Vec<PyRefMut<LiveInstrument>>) -> PyResult<usize> {
    let mut builder = LiveBotBuilder::new();
    for instrument in instruments {
        builder = builder.register(Instrument::new(
            &instrument.connector_name,
            &instrument.symbol,
            instrument.tick_size,
            instrument.lot_size,
            HashMapMarketDepth::new(instrument.tick_size, instrument.lot_size),
            instrument.last_trades_cap,
        ));
    }
    let hbt: HashMapMarketDepthLiveBot = builder
        .error_handler(|_error| Ok(()))
        .order_recv_hook(|_prev, _new| Ok(()))
        .build()
        .unwrap();

    Ok(Box::into_raw(Box::new(hbt)) as *mut c_void as usize)
}

#[cfg(feature = "live")]
#[pyfunction]
pub fn build_roivec_livebot(instruments: Vec<PyRefMut<LiveInstrument>>) -> PyResult<usize> {
    let mut builder = LiveBotBuilder::new();
    for instrument in instruments {
        builder = builder.register(Instrument::new(
            &instrument.connector_name,
            &instrument.symbol,
            instrument.tick_size,
            instrument.lot_size,
            ROIVectorMarketDepth::new(
                instrument.tick_size,
                instrument.lot_size,
                instrument.roi_lb,
                instrument.roi_ub,
            ),
            instrument.last_trades_cap,
        ));
    }
    let hbt: ROIVectorMarketDepthLiveBot = builder
        .error_handler(|_error| Ok(()))
        .order_recv_hook(|_prev, _new| Ok(()))
        .build()
        .unwrap();

    Ok(Box::into_raw(Box::new(hbt)) as *mut c_void as usize)
}
