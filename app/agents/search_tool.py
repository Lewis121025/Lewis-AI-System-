"""Google Custom Search 搜索工具模块。"""

from __future__ import annotations

import logging
from typing import List, Optional
from dataclasses import dataclass

import requests

from app.config import Settings, get_settings

LOGGER = logging.getLogger(__name__)


@dataclass
class SearchResult:
    """搜索结果数据类。"""
    
    title: str
    link: str
    snippet: str
    
    def to_dict(self) -> dict:
        return {
            "title": self.title,
            "link": self.link,
            "snippet": self.snippet,
        }


class GoogleSearchTool:
    """Google Custom Search API 工具类。
    
    使用 Google Custom Search JSON API 进行网络搜索。
    需要配置 google_search_api_key 和 google_search_engine_id。
    """
    
    def __init__(self, settings: Optional[Settings] = None) -> None:
        self.settings = settings or get_settings()
        self.api_key = self.settings.google_search_api_key
        self.cx = self.settings.google_search_engine_id
        self.max_results = self.settings.google_search_max_results
        self.base_url = "https://www.googleapis.com/customsearch/v1"
    
    def is_configured(self) -> bool:
        """检查搜索工具是否已正确配置。"""
        return bool(self.api_key and self.cx)
    
    def search(self, query: str, num_results: Optional[int] = None) -> List[SearchResult]:
        """执行搜索查询。
        
        Args:
            query: 搜索关键词
            num_results: 返回结果数量（默认使用配置值）
        
        Returns:
            搜索结果列表
        """
        if not self.is_configured():
            LOGGER.warning(
                "Google Search API not configured. "
                "Please set GOOGLE_SEARCH_API_KEY and GOOGLE_SEARCH_ENGINE_ID in .env"
            )
            return self._offline_search(query)
        
        num = num_results or self.max_results
        
        try:
            params = {
                "key": self.api_key,
                "cx": self.cx,
                "q": query,
                "num": min(num, 10),  # Google API 限制单次最多 10 个结果
            }
            
            LOGGER.info(f"Searching Google for: {query}")
            response = requests.get(self.base_url, params=params, timeout=10)
            response.raise_for_status()
            
            data = response.json()
            items = data.get("items", [])
            
            results = []
            for item in items[:num]:
                results.append(SearchResult(
                    title=item.get("title", ""),
                    link=item.get("link", ""),
                    snippet=item.get("snippet", ""),
                ))
            
            LOGGER.info(f"Found {len(results)} search results")
            return results
            
        except requests.RequestException as exc:
            LOGGER.error(f"Google Search API error: {exc}")
            return self._offline_search(query)
        except Exception as exc:
            LOGGER.exception(f"Unexpected error during search: {exc}")
            return self._offline_search(query)
    
    def _offline_search(self, query: str) -> List[SearchResult]:
        """离线模式下的模拟搜索结果。"""
        LOGGER.debug(f"Returning offline search results for: {query}")
        return [
            SearchResult(
                title=f"Offline result for '{query}'",
                link="https://example.com",
                snippet=(
                    f"This is a simulated search result. "
                    f"Configure Google Search API to get real results for: {query}"
                ),
            )
        ]
    
    def format_results(self, results: List[SearchResult]) -> str:
        """将搜索结果格式化为文本。"""
        if not results:
            return "No search results found."
        
        formatted = []
        for i, result in enumerate(results, 1):
            formatted.append(
                f"{i}. {result.title}\n"
                f"   URL: {result.link}\n"
                f"   {result.snippet}\n"
            )
        
        return "\n".join(formatted)

