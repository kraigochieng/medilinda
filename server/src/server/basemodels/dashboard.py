from pydantic import BaseModel


class SeriesData(BaseModel):
    series: list[int]
    data: list[str]


class MetricValue(BaseModel):
    metric: str
    value: int | float
