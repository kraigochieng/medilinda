from pydantic import BaseModel, ConfigDict


class SeriesData(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    series: list[int]
    data: list[str]


class MetricValue(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    metric: str
    value: int | float
