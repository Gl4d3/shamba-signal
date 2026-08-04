from __future__ import annotations

from dataclasses import dataclass

from shamba_signal.modelling.tabfm_benchmark import BenchmarkRow
from shamba_tabfm.provider import TabFMPredictionProvider


@dataclass
class CapturedFit:
    columns: tuple[str, ...]
    counties: tuple[str, ...]
    targets: tuple[float, ...]


class FakeRegressor:
    instances: list["FakeRegressor"] = []

    def __init__(self, **kwargs: object) -> None:
        self.kwargs = kwargs
        self.fit_capture: CapturedFit | None = None
        FakeRegressor.instances.append(self)

    def fit(self, frame, targets):
        self.fit_capture = CapturedFit(
            columns=tuple(frame.columns),
            counties=tuple(frame["county_id"]),
            targets=tuple(float(value) for value in targets),
        )
        return self

    def predict(self, frame):
        return [float(value) + 0.25 for value in frame["lag_1_yield"]]


def _row(county: str, year: int, target: float) -> BenchmarkRow:
    return BenchmarkRow(
        county_id=county,
        year=year,
        yield_t_per_ha=target,
        provisional=False,
        temporal_features={
            "county_id": county,
            "year": year,
            "lag_1_yield": target - 0.1,
            "trailing_3_mean": target - 0.2,
        },
        weather_features={
            "precipitation_total_mm": 800.0,
            "wet_day_count": 90,
            "mean_temperature_c": 21.0,
            "max_temperature_c": 31.0,
        },
    )


def test_provider_freezes_configuration_and_temporal_columns() -> None:
    FakeRegressor.instances.clear()
    provider = TabFMPredictionProvider(
        model=object(),
        regressor_class=FakeRegressor,
    )

    predictions = provider.predict(
        model_name="tabfm_temporal",
        training_rows=(
            _row("beta", 2017, 2.0),
            _row("alpha", 2017, 1.0),
        ),
        evaluation_rows=(_row("alpha", 2018, 1.1),),
    )

    instance = FakeRegressor.instances[-1]
    assert instance.kwargs == {
        "model": provider.model,
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
    assert instance.fit_capture is not None
    assert instance.fit_capture.columns == (
        "county_id",
        "year",
        "lag_1_yield",
        "trailing_3_mean",
    )
    assert instance.fit_capture.counties == ("beta", "alpha")
    assert predictions == (1.25,)


def test_weather_provider_appends_only_the_four_approved_weather_columns() -> None:
    FakeRegressor.instances.clear()
    provider = TabFMPredictionProvider(
        model=object(), regressor_class=FakeRegressor
    )

    provider.predict(
        model_name="tabfm_weather",
        training_rows=(_row("alpha", 2017, 1.0),),
        evaluation_rows=(_row("alpha", 2018, 1.1),),
    )

    capture = FakeRegressor.instances[-1].fit_capture
    assert capture is not None
    assert capture.columns == (
        "county_id",
        "year",
        "lag_1_yield",
        "trailing_3_mean",
        "precipitation_total_mm",
        "wet_day_count",
        "mean_temperature_c",
        "max_temperature_c",
    )
