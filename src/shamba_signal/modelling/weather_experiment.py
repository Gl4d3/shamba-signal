"""One bounded county-year weather value experiment.

The feature source is Open-Meteo's Historical Weather API using ERA5
reanalysis.  Values describe the completed label year, so this is strictly a
retrospective end-of-year backtest, never a mid-season forecasting workflow.
"""

from __future__ import annotations

import json
import math
import urllib.parse
import urllib.request
from collections.abc import Mapping, Sequence
from dataclasses import dataclass
from datetime import UTC, datetime
from pathlib import Path

import numpy as np

from shamba_signal.modelling.temporal_baselines import (
    BaselineExperiment,
    LaggedExample,
    Metrics,
    PanelExample,
    build_lagged_examples,
    run_baseline_experiment,
)

OPEN_METEO_ARCHIVE_URL = "https://archive-api.open-meteo.com/v1/archive"
OPEN_METEO_DATASET = "era5"
WEATHER_FEATURE_NAMES = (
    "annual precipitation total (mm)",
    "wet-day count (daily precipitation > 1 mm)",
    "annual mean 2 m temperature (°C)",
    "annual maximum 2 m temperature (°C)",
)

# Representative interior points, intentionally kept separate from the official
# label sources.  Reanalysis is spatially coarse enough that these are county
# proxies, not farm or pixel measurements.
COUNTY_COORDINATES: Mapping[str, tuple[float, float]] = {
    "baringo": (0.5, 36.0), "bomet": (-0.8, 35.3), "bungoma": (0.6, 34.6),
    "busia": (0.5, 34.1), "elgeyo_marakwet": (0.8, 35.5), "embu": (-0.5, 37.5),
    "garissa": (-0.5, 39.6), "homa_bay": (-0.5, 34.5), "isiolo": (0.4, 37.6),
    "kajiado": (-2.2, 36.8), "kakamega": (0.3, 34.8), "kericho": (-0.3, 35.3),
    "kiambu": (-1.1, 36.8), "kilifi": (-3.6, 39.8), "kirinyaga": (-0.6, 37.3),
    "kisii": (-0.7, 34.8), "kisumu": (-0.2, 34.8), "kitui": (-1.3, 38.0),
    "kwale": (-4.1, 39.4), "laikipia": (0.3, 36.8), "lamu": (-2.0, 40.9),
    "machakos": (-1.5, 37.3), "makueni": (-2.2, 37.8), "mandera": (3.9, 41.8),
    "marsabit": (2.5, 37.9), "meru": (0.2, 37.8), "migori": (-1.0, 34.5),
    "mombasa": (-4.0, 39.7), "muranga": (-0.8, 37.1), "nairobi_city": (-1.3, 36.85),
    "nakuru": (-0.2, 36.1), "nandi": (0.2, 35.1), "narok": (-1.2, 35.5),
    "nyamira": (-0.6, 34.9), "nyandarua": (-0.2, 36.5), "nyeri": (-0.4, 36.95),
    "samburu": (1.2, 37.2), "siaya": (0.1, 34.3), "taita_taveta": (-3.3, 38.5),
    "tana_river": (-1.6, 39.7), "tharaka_nithi": (0.0, 37.9),
    "trans_nzoia": (1.1, 34.9), "turkana": (3.0, 35.6),
    "uasin_gishu": (0.5, 35.3), "vihiga": (0.1, 34.7), "wajir": (1.7, 40.1),
    "west_pokot": (1.6, 35.2),
}


@dataclass(frozen=True)
class DailyWeather:
    date: str
    precipitation_mm: float
    mean_temperature_c: float
    max_temperature_c: float


@dataclass(frozen=True)
class WeatherFeature:
    county_id: str
    year: int
    precipitation_total_mm: float
    wet_day_count: int
    mean_temperature_c: float
    max_temperature_c: float


@dataclass(frozen=True)
class WeatherPrediction:
    county_id: str
    year: int
    actual_yield_t_per_ha: float
    split: str
    provisional: bool
    previous_year_prediction: float
    county_mean_prediction: float
    ridge_prediction: float
    weather_ridge_prediction: float


@dataclass(frozen=True)
class WeatherExperiment:
    selected_alpha: float
    validation_metrics: Mapping[str, Metrics]
    test_metrics: Mapping[str, Metrics]
    predictions: tuple[WeatherPrediction, ...]


@dataclass(frozen=True)
class _WeatherRidgeModel:
    counties: tuple[str, ...]
    means: np.ndarray
    scales: np.ndarray
    coefficients: np.ndarray


def aggregate_annual_weather(
    *, county_id: str, year: int, days: Sequence[DailyWeather]
) -> WeatherFeature:
    """Aggregate a complete label year into the four declared weather features."""
    if not days:
        raise ValueError(f"weather payload has no daily rows for {county_id} {year}")
    values = np.asarray(
        [[day.precipitation_mm, day.mean_temperature_c, day.max_temperature_c] for day in days],
        dtype=float,
    )
    if not np.isfinite(values).all():
        raise ValueError(f"weather payload has non-finite values for {county_id} {year}")
    return WeatherFeature(
        county_id=county_id,
        year=year,
        precipitation_total_mm=float(values[:, 0].sum()),
        wet_day_count=int(np.count_nonzero(values[:, 0] > 1.0)),
        mean_temperature_c=float(values[:, 1].mean()),
        max_temperature_c=float(values[:, 2].max()),
    )


def features_from_open_meteo_payload(
    *, county_id: str, payload: Mapping[str, object]
) -> tuple[WeatherFeature, ...]:
    """Parse Open-Meteo daily JSON and return one complete feature row per year."""
    daily = payload.get("daily")
    if not isinstance(daily, Mapping):
        raise ValueError("Open-Meteo response is missing daily data")
    fields = ("time", "precipitation_sum", "temperature_2m_mean", "temperature_2m_max")
    series = [daily.get(field) for field in fields]
    if not all(isinstance(values, list) and values for values in series):
        raise ValueError("Open-Meteo daily payload has missing values")
    if len({len(values) for values in series}) != 1:
        raise ValueError("Open-Meteo daily payload has unequal series lengths")
    grouped: dict[int, list[DailyWeather]] = {}
    for date, precipitation, mean_temperature, max_temperature in zip(*series, strict=True):
        if not isinstance(date, str):
            raise ValueError("Open-Meteo daily time values must be strings")
        try:
            year = int(date[:4])
            day = DailyWeather(
                date,
                float(precipitation),
                float(mean_temperature),
                float(max_temperature),
            )
        except (TypeError, ValueError) as exc:
            raise ValueError("Open-Meteo daily payload has non-numeric weather values") from exc
        grouped.setdefault(year, []).append(day)
    return tuple(
        aggregate_annual_weather(county_id=county_id, year=year, days=days)
        for year, days in sorted(grouped.items())
    )


def features_from_open_meteo_batch(
    county_ids: Sequence[str], payload: object
) -> tuple[WeatherFeature, ...]:
    """Bind Open-Meteo's multi-location response to the requested county order."""
    responses = payload if isinstance(payload, list) else [payload]
    if len(responses) != len(county_ids):
        raise ValueError("Open-Meteo batch response does not match requested county count")
    features: list[WeatherFeature] = []
    for county_id, response in zip(county_ids, responses, strict=True):
        if not isinstance(response, Mapping):
            raise ValueError("Open-Meteo batch response contains an invalid location payload")
        features.extend(features_from_open_meteo_payload(county_id=county_id, payload=response))
    return tuple(sorted(features, key=lambda item: (item.year, item.county_id)))


def fetch_open_meteo_features(
    *, county_ids: Sequence[str], raw_cache_dir: Path, start_year: int, end_year: int
) -> tuple[tuple[WeatherFeature, ...], dict[str, object]]:
    """Fetch and cache one reproducible ERA5 daily payload per county."""
    raw_cache_dir.mkdir(parents=True, exist_ok=True)
    requested_counties = sorted(set(county_ids))
    coordinates: list[tuple[float, float]] = []
    for county_id in requested_counties:
        coordinate = COUNTY_COORDINATES.get(county_id)
        if coordinate is None:
            raise ValueError(f"no representative coordinate for county: {county_id}")
        coordinates.append(coordinate)
    cache_path = raw_cache_dir / f"open-meteo-era5-batch-{start_year}-{end_year}.json"
    metadata_path = cache_path.with_suffix(".metadata.json")
    if cache_path.is_file():
        payload = json.loads(cache_path.read_text(encoding="utf-8"))
        if metadata_path.is_file():
            cache_metadata = json.loads(metadata_path.read_text(encoding="utf-8"))
            retrieved_at_utc = cache_metadata.get("retrieved_at_utc")
            if not isinstance(retrieved_at_utc, str) or not retrieved_at_utc:
                raise ValueError("Open-Meteo cache metadata has no retrieval timestamp")
        else:
            retrieved_at_utc = datetime.fromtimestamp(
                cache_path.stat().st_mtime, UTC
            ).replace(microsecond=0).isoformat()
            metadata_path.write_text(
                json.dumps({"retrieved_at_utc": retrieved_at_utc}, sort_keys=True) + "\n",
                encoding="utf-8",
            )
    else:
        params = urllib.parse.urlencode(
            {
                "latitude": ",".join(str(latitude) for latitude, _ in coordinates),
                "longitude": ",".join(str(longitude) for _, longitude in coordinates),
                "start_date": f"{start_year}-01-01",
                "end_date": f"{end_year}-12-31",
                "daily": "precipitation_sum,temperature_2m_mean,temperature_2m_max",
                "timezone": "Africa/Nairobi",
                "models": OPEN_METEO_DATASET,
            }
        )
        request = urllib.request.Request(
            f"{OPEN_METEO_ARCHIVE_URL}?{params}",
            headers={"User-Agent": "ShambaSignalResearch/0.1"},
        )
        with urllib.request.urlopen(request, timeout=120) as response:
            payload = json.loads(response.read().decode("utf-8"))
        cache_path.write_text(json.dumps(payload, sort_keys=True) + "\n", encoding="utf-8")
        retrieved_at_utc = datetime.now(UTC).replace(microsecond=0).isoformat()
        metadata_path.write_text(
            json.dumps({"retrieved_at_utc": retrieved_at_utc}, sort_keys=True) + "\n",
            encoding="utf-8",
        )
    collected = features_from_open_meteo_batch(requested_counties, payload)
    return (
        collected,
        {
            "source": "Open-Meteo Historical Weather API",
            "endpoint": OPEN_METEO_ARCHIVE_URL,
            "model": OPEN_METEO_DATASET,
            "retrieved_at_utc": retrieved_at_utc,
            "feature_definitions": list(WEATHER_FEATURE_NAMES),
            "county_coordinate_note": (
                "Representative county interior points; not farm or pixel data."
            ),
        },
    )


def _metric(actual: Sequence[float], predicted: Sequence[float]) -> Metrics:
    errors = np.asarray(predicted, dtype=float) - np.asarray(actual, dtype=float)
    return Metrics(
        mae=float(np.mean(np.abs(errors))),
        rmse=float(np.sqrt(np.mean(errors**2))),
    )


def _weather_features(
    row: LaggedExample, feature: WeatherFeature, counties: Sequence[str]
) -> list[float]:
    return [
        float(row.year - 2012), row.lag_1_yield, row.trailing_3_mean,
        feature.precipitation_total_mm, float(feature.wet_day_count),
        feature.mean_temperature_c, feature.max_temperature_c,
        *(1.0 if row.county_id == county else 0.0 for county in counties[1:]),
    ]


def _fit_weather_ridge(
    rows: Sequence[LaggedExample], features: Mapping[tuple[str, int], WeatherFeature], alpha: float
) -> _WeatherRidgeModel:
    if alpha < 0 or not math.isfinite(alpha):
        raise ValueError("ridge alpha must be finite and non-negative")
    counties = tuple(sorted({row.county_id for row in rows}))
    raw = np.asarray(
        [_weather_features(row, features[(row.county_id, row.year)], counties) for row in rows],
        dtype=float,
    )
    means, scales = raw.mean(axis=0), raw.std(axis=0)
    scales[scales == 0] = 1.0
    design = np.column_stack([np.ones(len(rows)), (raw - means) / scales])
    target = np.asarray([row.yield_t_per_ha for row in rows], dtype=float)
    penalty = np.eye(design.shape[1])
    penalty[0, 0] = 0.0
    return _WeatherRidgeModel(
        counties=counties,
        means=means,
        scales=scales,
        coefficients=np.linalg.solve(design.T @ design + alpha * penalty, design.T @ target),
    )


def _predict_weather_ridge(
    model: _WeatherRidgeModel,
    rows: Sequence[LaggedExample],
    features: Mapping[tuple[str, int], WeatherFeature],
) -> np.ndarray:
    raw = np.asarray(
        [
            _weather_features(row, features[(row.county_id, row.year)], model.counties)
            for row in rows
        ],
        dtype=float,
    )
    design = np.column_stack([np.ones(len(rows)), (raw - model.means) / model.scales])
    return design @ model.coefficients


def _require_complete_features(
    rows: Sequence[LaggedExample], features: Mapping[tuple[str, int], WeatherFeature]
) -> None:
    missing = sorted({(row.county_id, row.year) for row in rows} - set(features))
    if missing:
        raise ValueError(f"weather features are missing county-year rows: {missing[:3]}")


def run_weather_experiment(
    examples: Sequence[PanelExample],
    weather_features: Sequence[WeatherFeature],
    *,
    alpha_candidates: Sequence[float],
) -> WeatherExperiment:
    """Select regularization on 2022 and use provisional 2023 exactly once."""
    if not alpha_candidates:
        raise ValueError("at least one ridge alpha candidate is required")
    baseline: BaselineExperiment = run_baseline_experiment(
        examples, alpha_candidates=alpha_candidates
    )
    features = {(item.county_id, item.year): item for item in weather_features}
    lagged = build_lagged_examples(examples)
    train = tuple(row for row in lagged if row.split == "train")
    validation = tuple(row for row in lagged if row.split == "validation")
    test = tuple(row for row in lagged if row.split == "test")
    _require_complete_features((*train, *validation, *test), features)
    selected_alpha = min(
        (float(alpha) for alpha in alpha_candidates),
        key=lambda alpha: _metric(
            [row.yield_t_per_ha for row in validation],
            _predict_weather_ridge(
                _fit_weather_ridge(train, features, alpha), validation, features
            ),
        ).mae,
    )
    validation_prediction = _predict_weather_ridge(
        _fit_weather_ridge(train, features, selected_alpha), validation, features
    )
    test_prediction = _predict_weather_ridge(
        _fit_weather_ridge((*train, *validation), features, selected_alpha), test, features
    )
    weather_pairs = (*zip(validation, validation_prediction, strict=True),)
    weather_pairs += (*zip(test, test_prediction, strict=True),)
    weather_predictions = {
        (row.county_id, row.year): float(value) for row, value in weather_pairs
    }
    predictions = tuple(
        WeatherPrediction(
            county_id=item.county_id, year=item.year,
            actual_yield_t_per_ha=item.actual_yield_t_per_ha,
            split=item.split,
            provisional=item.provisional,
            previous_year_prediction=item.previous_year_prediction,
            county_mean_prediction=item.county_mean_prediction,
            ridge_prediction=item.ridge_prediction,
            weather_ridge_prediction=weather_predictions[(item.county_id, item.year)],
        )
        for item in baseline.predictions
    )
    def metrics_for(split: str) -> dict[str, Metrics]:
        selected = [item for item in predictions if item.split == split]
        actual = [item.actual_yield_t_per_ha for item in selected]
        return {
            "previous_year": _metric(actual, [item.previous_year_prediction for item in selected]),
            "county_mean": _metric(actual, [item.county_mean_prediction for item in selected]),
            "ridge": _metric(actual, [item.ridge_prediction for item in selected]),
            "weather_ridge": _metric(actual, [item.weather_ridge_prediction for item in selected]),
        }
    return WeatherExperiment(
        selected_alpha=selected_alpha,
        validation_metrics=metrics_for("validation"),
        test_metrics=metrics_for("test"),
        predictions=predictions,
    )
