"""Weather Agent - 专门处理天气查询任务"""

from __future__ import annotations

from app.agents.base import Agent, AgentContext, AgentResponse
from app.agents.weather_api import WeatherAPITool
from app.agents.llm_proxy import LLMProxy, LLMRequest


class WeatherAgent(Agent):
    """负责查询和分析天气信息"""
    
    def __init__(self, weather_tool: WeatherAPITool, llm_proxy: LLMProxy) -> None:
        super().__init__("Weather")
        self.weather_tool = weather_tool
        self.llm_proxy = llm_proxy
    
    def execute(self, context: AgentContext) -> AgentResponse:
        """执行天气查询任务"""
        # 从任务描述中提取城市名称
        task_desc = context.payload.get("task") or context.goal
        location = self._extract_location(task_desc)
        
        # 获取天气数据
        weather = self.weather_tool.get_current_weather(location, lang="zh")
        
        if weather is None:
            return AgentResponse(
                success=False,
                output={"location": location, "error": "Failed to fetch weather"},
                message="Weather fetch failed",
            )
        
        # 使用 LLM 生成友好的天气描述
        description = self._generate_description(weather, task_desc)
        
        output = {
            "location": weather.location,
            "temperature": weather.temperature,
            "condition": weather.condition,
            "humidity": weather.humidity,
            "wind_speed": weather.wind_speed,
            "weather_data": weather.to_dict(),
            "formatted_text": weather.to_text(),
            "description": description,
        }
        
        return AgentResponse(
            success=True,
            output=output,
            message=f"Weather data retrieved for {weather.location}",
        )
    
    def _extract_location(self, text: str) -> str:
        """从任务描述中提取城市名称"""
        import re
        
        text_lower = text.lower()
        
        # 移除常见前缀
        prefixes = [
            "查询", "搜索", "获取", "查看", "天气", "weather", "查",
            "使用google search", "使用google", "google",
        ]
        
        cleaned = text
        for prefix in prefixes:
            cleaned = re.sub(f"^{prefix}\\s*", "", cleaned, flags=re.IGNORECASE).strip()
        
        # 尝试匹配常见城市名模式
        # 中文城市名通常2-3个字
        chinese_city = re.search(r'([北上广深杭成都重庆天津南京苏州武汉西安]{2,3})', cleaned)
        if chinese_city:
            return chinese_city.group(1)
        
        # 英文城市名
        english_city = re.search(r'([A-Za-z\s]{3,20})', cleaned)
        if english_city:
            return english_city.group(1).strip()
        
        # 默认返回清理后的文本
        return cleaned.strip() or "Beijing"
    
    def _generate_description(self, weather: WeatherData, task: str) -> str:
        """生成友好的天气描述"""
        prompt = (
            f"Generate a friendly weather description in Chinese based on this data:\n"
            f"Location: {weather.location}\n"
            f"Temperature: {weather.temperature}°C\n"
            f"Condition: {weather.condition}\n"
            f"Humidity: {weather.humidity}%\n"
            f"Wind: {weather.wind_speed} km/h\n\n"
            f"Provide a brief, natural description (2-3 sentences)."
        )
        
        try:
            description = self.llm_proxy.complete(
                LLMRequest(prompt=prompt, temperature=0.3, model=None)
            )
            return description.strip()
        except Exception:
            return f"{weather.location}当前温度{weather.temperature}°C，{weather.condition}。"

