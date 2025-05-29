from dataclasses import dataclass
from typing import Optional, List


@dataclass
class WeatherData:
    state: str
    temperature: float
    temperature_unit: str
    humidity: int
    cloud_coverage: int
    pressure: float
    pressure_unit: str
    wind_bearing: int
    wind_gust_speed: float
    wind_speed: float
    wind_speed_unit: str
    visibility: float
    visibility_unit: str
    precipitation_unit: str
    thunder_probability: int
    attribution: str
    friendly_name: str
    supported_features: int

    @classmethod
    def from_dict(cls, data: dict, state: str) -> "WeatherData":
        """Create a WeatherData instance from a dictionary."""
        return cls(
            state=state,
            temperature=float(data["temperature"]),
            temperature_unit=data["temperature_unit"],
            humidity=int(data["humidity"]),
            cloud_coverage=int(data["cloud_coverage"]),
            pressure=float(data["pressure"]),
            pressure_unit=data["pressure_unit"],
            wind_bearing=int(data["wind_bearing"]),
            wind_gust_speed=float(data["wind_gust_speed"]),
            wind_speed=float(data["wind_speed"]),
            wind_speed_unit=data["wind_speed_unit"],
            visibility=float(data["visibility"]),
            visibility_unit=data["visibility_unit"],
            precipitation_unit=data["precipitation_unit"],
            thunder_probability=int(data["thunder_probability"]),
            attribution=data["attribution"],
            friendly_name=data["friendly_name"],
            supported_features=int(data["supported_features"]),
        )

    def to_dict(self) -> dict:
        """Convert the WeatherData instance back to a dictionary."""
        return {
            "state": self.state,
            "temperature": self.temperature,
            "temperature_unit": self.temperature_unit,
            "humidity": self.humidity,
            "cloud_coverage": self.cloud_coverage,
            "pressure": self.pressure,
            "pressure_unit": self.pressure_unit,
            "wind_bearing": self.wind_bearing,
            "wind_gust_speed": self.wind_gust_speed,
            "wind_speed": self.wind_speed,
            "wind_speed_unit": self.wind_speed_unit,
            "visibility": self.visibility,
            "visibility_unit": self.visibility_unit,
            "precipitation_unit": self.precipitation_unit,
            "thunder_probability": self.thunder_probability,
            "attribution": self.attribution,
            "friendly_name": self.friendly_name,
            "supported_features": self.supported_features,
        }
