"""PyTorch TabFM prediction provider with a frozen experiment configuration."""

from __future__ import annotations

import math
from collections.abc import Sequence
from typing import Any

import pandas as pd

from shamba_signal.modelling.tabfm_benchmark import (
    TEMPORAL_COLUMNS,
    WEATHER_COLUMNS,
    BenchmarkRow,
)

TABFM_COMMIT = "b8a8b090c66d1b9e7af278003461582219996b6a"
CHECKPOINT = "tabfm_v1_0_0"
SUPPORTED_MODELS = {"tabfm_temporal": False, "tabfm_weather": True}


class TabFMPredictionProvider:
    """Create a fresh sklearn-compatible TabFM regressor for each temporal fold."""

    def __init__(self, *, model: object, regressor_class: type[Any]) -> None:
        self.model = model
        self.regressor_class = regressor_class

    @property
    def manifest(self) -> dict[str, object]:
        return {
            "tabfm_commit": TABFM_COMMIT,
            "checkpoint": CHECKPOINT,
            "backend": "pytorch",
            "n_estimators": 16,
            "max_num_rows": None,
            "max_num_features": 500,
            "batch_size": 1,
            "random_state": 42,
            "cat_encoder_mode": "alphabetical",
            "enable_nnls": False,
            "n_feature_crosses": 0,
            "n_svd_features": 0,
            "cache_context": False,
        }

    def predict(
        self,
        *,
        model_name: str,
        training_rows: tuple[BenchmarkRow, ...],
        evaluation_rows: tuple[BenchmarkRow, ...],
    ) -> tuple[float, ...]:
        try:
            include_weather = SUPPORTED_MODELS[model_name]
        except KeyError as exc:
            raise ValueError(f"unsupported TabFM model: {model_name}") from exc
        if not training_rows or not evaluation_rows:
            raise ValueError("TabFM prediction requires training and evaluation rows")

        columns = TEMPORAL_COLUMNS + (WEATHER_COLUMNS if include_weather else ())
        training_frame = _frame(
            training_rows, columns, include_weather=include_weather
        )
        evaluation_frame = _frame(
            evaluation_rows, columns, include_weather=include_weather
        )
        targets = [row.yield_t_per_ha for row in training_rows]
        regressor = self.regressor_class(
            model=self.model,
            n_estimators=16,
            max_num_rows=None,
            max_num_features=500,
            batch_size=1,
            random_state=42,
            cat_encoder_mode="alphabetical",
            enable_nnls=False,
            n_feature_crosses=0,
            n_svd_features=0,
            cache_context=False,
        )
        regressor.fit(training_frame, targets)
        predictions = tuple(
            float(value) for value in regressor.predict(evaluation_frame)
        )
        if len(predictions) != len(evaluation_rows):
            raise ValueError(
                f"TabFM returned {len(predictions)} predictions for "
                f"{len(evaluation_rows)} evaluation rows"
            )
        if not all(math.isfinite(value) for value in predictions):
            raise ValueError("TabFM returned non-finite predictions")
        return predictions


def _frame(
    rows: Sequence[BenchmarkRow],
    columns: Sequence[str],
    *,
    include_weather: bool,
) -> pd.DataFrame:
    records = [dict(row.features(include_weather=include_weather)) for row in rows]
    return pd.DataFrame.from_records(records, columns=list(columns))


def load_pytorch_provider(*, device: str = "auto") -> TabFMPredictionProvider:
    """Load the non-commercial regression checkpoint in the isolated environment."""

    try:
        import torch
        from tabfm import TabFMRegressor
        from tabfm import tabfm_v1_0_0_pytorch as tabfm_v1_0_0
    except ImportError as exc:
        raise RuntimeError(
            "TabFM dependencies are unavailable. Run `uv sync --project "
            "experiments/tabfm` before executing the benchmark."
        ) from exc

    resolved_device = device
    if device == "auto":
        resolved_device = "cuda" if torch.cuda.is_available() else "cpu"
    if resolved_device == "cuda" and not torch.cuda.is_available():
        raise RuntimeError("CUDA was requested but PyTorch reports no CUDA device")
    if resolved_device not in {"cpu", "cuda"}:
        raise ValueError("device must be one of: auto, cpu, cuda")

    try:
        model = tabfm_v1_0_0.load(model_type="regression")
    except Exception as exc:
        raise RuntimeError(
            "The TabFM regression checkpoint could not be loaded. Confirm Hugging "
            "Face access and acceptance of the non-commercial checkpoint licence."
        ) from exc
    if hasattr(model, "to"):
        model = model.to(resolved_device)
    if hasattr(model, "eval"):
        model.eval()
    return TabFMPredictionProvider(model=model, regressor_class=TabFMRegressor)
