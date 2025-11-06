"""Researcher（研究员）智能体：负责网络搜索和信息收集。"""

from __future__ import annotations

from typing import List

from app.agents.base import Agent, AgentContext, AgentResponse
from app.agents.search_tool import GoogleSearchTool
from app.agents.llm_proxy import LLMProxy, LLMRequest


class ResearcherAgent(Agent):
    """负责搜索互联网信息并总结搜索结果。"""
    
    def __init__(self, search_tool: GoogleSearchTool, llm_proxy: LLMProxy) -> None:
        super().__init__("Researcher")
        self.search_tool = search_tool
        self.llm_proxy = llm_proxy
    
    def execute(self, context: AgentContext) -> AgentResponse:
        """执行搜索任务。
        
        从 context.payload 中提取搜索查询，执行搜索，并使用 LLM 总结结果。
        支持多查询搜索（如对比分析任务）。
        """
        # 从 payload 或 goal 中提取搜索查询
        task_desc = context.payload.get("task") or ""
        goal = context.goal or ""
        original_text = task_desc or goal
        
        num_results = context.payload.get("num_results")
        
        # 检测是否需要多查询搜索（对比分析类任务）
        queries = self._extract_search_queries(original_text, goal)
        
        # 执行所有搜索查询（优化：减少结果数量，避免过多数据）
        all_results = []
        all_formatted = []
        query_summaries = []
        
        # 限制每个查询的结果数量，避免数据过多
        results_per_query = min(num_results or 3, 3)  # 最多3个结果/查询
        
        for query in queries:
            results = self.search_tool.search(query, results_per_query)
            if results:
                all_results.extend(results)
                formatted = self.search_tool.format_results(results)
                all_formatted.append(f"Query: {query}\n{formatted}")
                # 为每个查询生成简短摘要（优化：减少LLM调用时间）
                summary = self._summarize_results(query, formatted)
                query_summaries.append(f"{query}: {summary}")
        
        if not all_results:
            return AgentResponse(
                success=False,
                output={"queries": queries, "results": []},
                message="No search results found",
            )
        
        # 合并所有搜索结果并生成总体摘要（优化：限制输入长度）
        combined_formatted = "\n\n".join(all_formatted)
        # 限制总体摘要的输入长度
        if len(combined_formatted) > 3000:
            combined_formatted = combined_formatted[:3000] + "\n... (truncated for performance)"
        
        overall_summary = self._summarize_results(
            f"Research on: {', '.join(queries)}", 
            combined_formatted
        )
        
        output = {
            "query": queries[0] if len(queries) == 1 else ", ".join(queries),
            "queries": queries,  # 保存所有查询
            "results": [r.to_dict() for r in all_results],
            "formatted_results": combined_formatted,
            "summary": overall_summary,
            "query_summaries": query_summaries,  # 每个查询的单独摘要
            "num_results": len(all_results),
        }
        
        return AgentResponse(
            success=True,
            output=output,
            message=f"Research completed: found {len(all_results)} results from {len(queries)} queries",
        )
    
    def _extract_search_queries(self, text: str, goal: str = "") -> List[str]:
        """从任务描述中提取搜索查询（支持多查询，如对比分析）"""
        import re
        
        # 检查是否是对比分析类任务
        comparison_keywords = ["对比", "比较", "compare", "comparison", "对比分析", "比较分析"]
        text_combined = (text + " " + goal).lower()
        
        if any(keyword in text_combined for keyword in comparison_keywords):
            # 对比分析任务：提取对比的主体
            # 例如："对比分析中美经济" -> ["中国经济", "美国经济"]
            return self._extract_comparison_queries(text, goal)
        else:
            # 普通任务：提取单个查询
            query = self._extract_search_query(text or goal)
            return [query] if query else []
    
    def _extract_comparison_queries(self, text: str, goal: str = "") -> List[str]:
        """提取对比分析任务的多个搜索查询"""
        import re
        
        combined = text + " " + goal
        
        # 常见对比模式
        # "中美经济" -> ["中国经济", "美国经济"]
        # "A和B的对比" -> ["A", "B"]
        
        # 提取中文对比模式：X和Y、X与Y、X vs Y
        patterns = [
            r'([^和与、,，]+)[和与]([^和与、,，]+)',  # "中美" 或 "中国和美国"
            r'([^和与、,，]+)[,，]([^和与、,，]+)',  # "中国,美国"
            r'([^和与、,，]+)\s+vs\s+([^和与、,，]+)',  # "China vs USA"
        ]
        
        for pattern in patterns:
            match = re.search(pattern, combined)
            if match:
                part1 = match.group(1).strip()
                part2 = match.group(2).strip()
                
                # 提取主题（如"经济"、"政策"等）
                # 移除对比关键词
                theme_match = re.search(r'(对比|比较|分析|compare|comparison|analysis)\s*(.+?)(的|$)', combined, re.IGNORECASE)
                theme = ""
                if theme_match:
                    theme = theme_match.group(2).strip()
                    # 移除已提取的部分
                    theme = re.sub(part1, "", theme, flags=re.IGNORECASE)
                    theme = re.sub(part2, "", theme, flags=re.IGNORECASE)
                    theme = theme.strip()
                
                # 构建查询
                queries = []
                if part1 and part2:
                    if theme:
                        queries.append(f"{part1} {theme}")
                        queries.append(f"{part2} {theme}")
                    else:
                        queries.append(part1)
                        queries.append(part2)
                
                if queries:
                    return queries
        
        # 如果没有匹配到对比模式，尝试简单规则提取，避免LLM调用
        # 优化：减少LLM调用，使用规则提取
        simple_queries = self._simple_extract_comparison(text)
        if simple_queries:
            return simple_queries
        
        # 最后才使用LLM（作为后备方案）
        return self._llm_extract_comparison_queries(combined)
    
    def _simple_extract_comparison(self, text: str) -> List[str]:
        """使用简单规则提取对比查询（避免LLM调用）"""
        import re
        
        # 常见模式："中美经济" -> ["中国经济", "美国经济"]
        # 提取常见国家/地区缩写
        country_patterns = {
            "中美": ["中国", "美国"],
            "中欧": ["中国", "欧洲"],
            "中日": ["中国", "日本"],
            "中韩": ["中国", "韩国"],
        }
        
        for pattern, countries in country_patterns.items():
            if pattern in text:
                # 提取主题
                theme_match = re.search(rf'{pattern}(.+)', text)
                theme = theme_match.group(1).strip() if theme_match else ""
                return [f"{c}{theme}" for c in countries]
        
        return []
    
    def _llm_extract_comparison_queries(self, text: str) -> List[str]:
        """使用LLM提取对比分析任务的搜索查询（后备方案）"""
        # 优化：使用更短的prompt，减少响应时间
        prompt = (
            f"Extract 2-3 search queries from: {text[:200]}\n"
            f"One per line, no numbering.\n"
            f"Queries:"
        )
        
        try:
            response = self.llm_proxy.complete(
                LLMRequest(prompt=prompt, temperature=0.2, model=None)  # 降低temperature加快响应
            )
            queries = [line.strip("-• ").strip() for line in response.splitlines() if line.strip()]
            return queries[:3] if queries else [self._extract_search_query(text)]
        except Exception:
            return [self._extract_search_query(text)]
    
    def _extract_search_query(self, text: str) -> str:
        """从任务描述中提取搜索查询。"""
        import re
        
        text_lower = text.lower()
        
        # 移除常见的任务前缀和工具名称
        prefixes = [
            "use google search to", "use google to", "使用google search",
            "使用google", "使用搜索", "search for", "search about", 
            "find information about", "look up", "research about",
            "query about", "query for", "google for",
            "搜索", "查找", "研究", "查询", "检索",
        ]
        
        cleaned_text = text
        for prefix in prefixes:
            if text_lower.startswith(prefix):
                # 找到匹配的前缀，移除它（保持原始大小写）
                pattern = re.escape(prefix)
                cleaned_text = re.sub(f"^{pattern}", "", text, flags=re.IGNORECASE).strip()
                break
        
        # 移除可能的动词后缀（中英文）
        # 例如："查询杭州天气" -> "杭州天气"
        cleaned_text = re.sub(r"^(to\s+|about\s+)", "", cleaned_text, flags=re.IGNORECASE).strip()
        
        return cleaned_text if cleaned_text else text
    
    def _summarize_results(self, query: str, results_text: str) -> str:
        """使用 LLM 总结搜索结果（优化版：限制输入长度）。"""
        # 限制results_text长度，避免prompt过长导致LLM响应慢
        max_length = 2000  # 限制为2000字符
        if len(results_text) > max_length:
            results_text = results_text[:max_length] + "\n... (truncated)"
        
        prompt = (
            f"Summarize these search results for '{query}' in 2-3 sentences. "
            f"Focus on key facts and data.\n\n"
            f"Results:\n{results_text}\n\n"
            f"Summary:"
        )
        
        try:
            summary = self.llm_proxy.complete(
                LLMRequest(prompt=prompt, temperature=0.3, model=None)
            )
            return summary.strip()
        except Exception as exc:
            self.logger.error(f"Failed to summarize results: {exc}")
            return f"Found {results_text.count('URL:')} search results for '{query}'"

