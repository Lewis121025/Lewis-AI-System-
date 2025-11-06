"""天气 API 工具模块 - 集成免费天气服务"""

from __future__ import annotations

import logging
from typing import Optional, Dict, Any, List
from dataclasses import dataclass
from datetime import datetime, timedelta

import requests

from app.config import Settings, get_settings

LOGGER = logging.getLogger(__name__)


@dataclass
class WeatherData:
    """天气数据类"""
    
    location: str
    temperature: float
    condition: str
    humidity: int
    wind_speed: float
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "location": self.location,
            "temperature": self.temperature,
            "condition": self.condition,
            "humidity": self.humidity,
            "wind_speed": self.wind_speed,
        }
    
    def to_text(self) -> str:
        return (
            f"地点: {self.location}\n"
            f"温度: {self.temperature}°C\n"
            f"天气: {self.condition}\n"
            f"湿度: {self.humidity}%\n"
            f"风速: {self.wind_speed} km/h"
        )


class WeatherAPITool:
    """免费天气 API 工具类
    
    使用 WeatherAPI.com 提供的免费服务
    免费额度：100万次/月
    """
    
    def __init__(self, settings: Optional[Settings] = None) -> None:
        self.settings = settings or get_settings()
        self.api_key = self.settings.weather_api_key
        self.base_url = "http://api.weatherapi.com/v1"
    
    def is_configured(self) -> bool:
        """检查天气 API 是否已配置"""
        return bool(self.api_key)
    
    def get_current_weather(self, location: str, lang: str = "zh") -> Optional[WeatherData]:
        """获取当前天气
        
        Args:
            location: 城市名称（中文或英文）
            lang: 语言代码（zh=中文, en=英文）
        
        Returns:
            天气数据或 None
        """
        if not self.is_configured():
            LOGGER.warning("Weather API not configured. Please set WEATHER_API_KEY in .env")
            return self._offline_weather(location)
        
        try:
            url = f"{self.base_url}/current.json"
            params = {
                "key": self.api_key,
                "q": location,
                "lang": lang,
                "aqi": "no",  # 不需要空气质量数据
            }
            
            LOGGER.info(f"Fetching weather for: {location}")
            response = requests.get(url, params=params, timeout=10)
            response.raise_for_status()
            
            data = response.json()
            location_data = data.get("location", {})
            current = data.get("current", {})
            
            weather = WeatherData(
                location=location_data.get("name", location),
                temperature=current.get("temp_c", 0),
                condition=current.get("condition", {}).get("text", "Unknown"),
                humidity=current.get("humidity", 0),
                wind_speed=current.get("wind_kph", 0),
            )
            
            LOGGER.info(f"Weather data retrieved for {weather.location}")
            return weather
            
        except requests.RequestException as exc:
            LOGGER.error(f"Weather API error: {exc}")
            return self._offline_weather(location)
        except Exception as exc:
            LOGGER.exception(f"Unexpected error fetching weather: {exc}")
            return self._offline_weather(location)
    
    def get_forecast(self, location: str, hours: int = 72, lang: str = "zh") -> List[Dict[str, Any]]:
        """获取指定小时数的天气预报（通用方法）
        
        Args:
            location: 城市名称（中文或英文）
            hours: 需要获取的小时数（默认72小时，最大支持10天=240小时）
            lang: 语言代码（zh=中文, en=英文）
        
        Returns:
            天气预报列表，每个元素包含时间、温度、天气状况等
        """
        # 限制最大小时数（API通常最多支持10天）
        max_hours = 240  # 10天
        hours = min(hours, max_hours)
        days_needed = (hours + 23) // 24  # 向上取整到天数
        
        if not self.is_configured():
            LOGGER.warning("Weather API not configured. Returning simulated forecast data")
            return self._offline_forecast(location, hours)
        
        try:
            # 使用forecast API获取预报（包含每小时数据）
            url = f"{self.base_url}/forecast.json"
            params = {
                "key": self.api_key,
                "q": location,
                "lang": lang,
                "days": min(days_needed, 10),  # API最多支持10天
                "aqi": "no",
                "alerts": "no",
            }
            
            LOGGER.info(f"Fetching {hours}h forecast ({days_needed} days) for: {location}")
            response = requests.get(url, params=params, timeout=10)
            response.raise_for_status()
            
            data = response.json()
            forecast_days = data.get("forecast", {}).get("forecastday", [])
            
            # 提取指定小时数的每小时数据
            hourly_data = []
            for day in forecast_days:
                hour_list = day.get("hour", [])
                for hour_info in hour_list:
                    hourly_data.append({
                        "time": hour_info.get("time", ""),
                        "temperature": hour_info.get("temp_c", 0),
                        "condition": hour_info.get("condition", {}).get("text", "Unknown"),
                        "humidity": hour_info.get("humidity", 0),
                        "wind_speed": hour_info.get("wind_kph", 0),
                    })
                    # 只取指定的小时数
                    if len(hourly_data) >= hours:
                        break
                if len(hourly_data) >= hours:
                    break
            
            LOGGER.info(f"Retrieved {len(hourly_data)} hours of forecast data for {location}")
            return hourly_data
            
        except requests.RequestException as exc:
            LOGGER.error(f"Weather API error: {exc}")
            return self._offline_forecast(location, hours)
        except Exception as exc:
            LOGGER.exception(f"Unexpected error fetching forecast: {exc}")
            return self._offline_forecast(location, hours)
    
    def get_forecast_72h(self, location: str, lang: str = "zh") -> List[Dict[str, Any]]:
        """获取未来72小时的天气预报（向后兼容方法）"""
        return self.get_forecast(location, hours=72, lang=lang)
    
    def _offline_forecast(self, location: str, hours: int) -> List[Dict[str, Any]]:
        """离线模式下的模拟预报数据"""
        LOGGER.debug(f"Returning offline {hours}h forecast data for: {location}")
        now = datetime.now()
        forecast = []
        for i in range(hours):
            hour_time = now + timedelta(hours=i)
            forecast.append({
                "time": hour_time.strftime("%Y-%m-%d %H:00"),
                "temperature": 22.5 + (i % 24 - 12) * 0.5,  # 模拟温度变化
                "condition": "Partly Cloudy (Simulated)",
                "humidity": 55 + (i % 10 - 5),
                "wind_speed": 15.0 + (i % 5 - 2),
            })
        return forecast
    
    def _offline_forecast_72h(self, location: str) -> List[Dict[str, Any]]:
        """离线模式下的模拟72小时预报数据（向后兼容）"""
        return self._offline_forecast(location, 72)
    
    def _offline_weather(self, location: str) -> WeatherData:
        """离线模式下的模拟天气数据"""
        LOGGER.debug(f"Returning offline weather data for: {location}")
        return WeatherData(
            location=location,
            temperature=22.5,
            condition="Partly Cloudy (Simulated)",
            humidity=55,
            wind_speed=15.0,
        )

