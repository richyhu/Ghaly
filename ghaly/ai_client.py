"""
AI client module for ghaly.

This module provides AI-powered analysis and recommendation functionality
using SiliconFlow API (GLM-4-9B-chat model).
"""

from typing import Any, Dict, List, Optional

import requests


class AIError(Exception):
    """Exception raised for AI API errors."""
    pass


class AIClient:
    """
    AI client for project analysis and recommendations.
    
    Uses SiliconFlow API with GLM-4-9B-chat model for
    analyzing GitHub repositories and providing intelligent insights.
    """
    
    def __init__(
        self,
        api_key: Optional[str] = None,
        api_base_url: str = "https://api.siliconflow.cn/v1/chat/completions",
        model: str = "THUDM/glm-4-9b-chat"
    ):
        """
        Initialize AI client.
        
        Args:
            api_key: SiliconFlow API key (optional, will use default if not provided)
            api_base_url: API base URL
            model: Model name to use
        """
        if api_key is None:
            api_key = "sk-wtyqgtudvkbrhpxzuvaswvnexlmozbtvtejubenacihcxvup"
        
        self.api_key = api_key
        self.api_base_url = api_base_url
        self.model = model
        self.session = requests.Session()
        self.session.headers.update({
            "Content-Type": "application/json",
            "Authorization": f"Bearer {api_key}"
        })
    
    def _clean_json_response(self, content: str) -> str:
        """
        Clean AI response content by removing markdown code blocks.
        
        Args:
            content: Raw AI response content
            
        Returns:
            Cleaned JSON string
        """
        content = content.strip()
        
        if content.startswith('```json'):
            content = content[7:]
        elif content.startswith('```'):
            content = content[3:]
        
        if content.endswith('```'):
            content = content[:-3]
        
        return content.strip()
    
    def _make_request(self, messages: List[Dict[str, str]], **kwargs) -> Dict[str, Any]:
        """
        Make request to AI API.
        
        Args:
            messages: List of message dictionaries
            **kwargs: Additional parameters for the API
            
        Returns:
            Response JSON data
            
        Raises:
            AIError: If request fails
        """
        try:
            payload = {
                "model": self.model,
                "messages": messages,
                **kwargs
            }
            
            response = self.session.post(
                self.api_base_url,
                json=payload,
                timeout=30
            )
            
            response.raise_for_status()
            result = response.json()
            
            if "choices" not in result or not result["choices"]:
                raise AIError("No response from AI model")
            
            return result
            
        except requests.HTTPError as e:
            if e.response is not None:
                try:
                    error_data = e.response.json()
                    if isinstance(error_data, dict):
                        error_obj = error_data.get('error')
                        if isinstance(error_obj, dict):
                            error_msg = error_obj.get('message', str(e))
                        else:
                            error_msg = str(error_obj) if error_obj else str(e)
                    else:
                        error_msg = str(error_data)
                except (ValueError, KeyError, AttributeError):
                    error_msg = str(e)
                raise AIError(f"AI API error: {error_msg}")
            else:
                raise AIError(f"HTTP error: {e}")
        except requests.RequestException as e:
            raise AIError(f"Request failed: {e}")
    
    def analyze_repository(
        self,
        name: str,
        description: str,
        language: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Analyze a repository using AI.
        
        Args:
            name: Repository name
            description: Repository description
            language: Programming language
            
        Returns:
            Dictionary containing analysis results
        """
        system_prompt = """你是一个 GitHub 项目分析专家。你的任务是分析 GitHub 仓库，提取关键信息并提供智能见解。

请分析给定的仓库信息，并返回以下格式的 JSON 响应：
{
    "summary": "项目的简要总结（1-2句话）",
    "tech_stack": ["技术栈1", "技术栈2", ...],
    "features": ["功能1", "功能2", ...],
    "use_cases": ["使用场景1", "使用场景2", ...],
    "keywords": ["关键词1", "关键词2", ...]
}

要求：
1. summary: 简洁明了，突出项目核心价值
2. tech_stack: 提取主要技术栈和框架
3. features: 列出 3-5 个主要功能
4. use_cases: 列出 2-3 个典型使用场景
5. keywords: 提取 5-8 个相关关键词，用于搜索相似项目
6. 只返回 JSON，不要有其他文字"""
        
        user_message = f"""仓库名称：{name}
描述：{description}
编程语言：{language or '未知'}"""
        
        messages = [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_message}
        ]
        
        response = self._make_request(messages)
        
        content = response["choices"][0]["message"]["content"]
        
        try:
            import json
            content = self._clean_json_response(content)
            analysis = json.loads(content)
            
            return {
                "summary": analysis.get("summary", ""),
                "tech_stack": analysis.get("tech_stack", []),
                "features": analysis.get("features", []),
                "use_cases": analysis.get("use_cases", []),
                "keywords": analysis.get("keywords", [])
            }
        except json.JSONDecodeError:
            raise AIError(f"Failed to parse AI response: {content}")
    
    def recommend_similar_projects(
        self,
        query: str,
        language: Optional[str] = None,
        limit: int = 10
    ) -> Dict[str, Any]:
        """
        Generate search queries and recommendations using AI.
        
        Args:
            query: User's search query
            language: Programming language filter
            limit: Maximum number of recommendations
            
        Returns:
            Dictionary containing search queries and recommendations
        """
        system_prompt = """你是一个 GitHub 项目搜索专家。你的任务是根据用户的查询生成优化的搜索关键词和推荐策略。

请根据给定的查询，返回以下格式的 JSON 响应：
{
    "search_queries": ["搜索查询1", "搜索查询2", "搜索查询3"],
    "recommendations": [
        {
            "query": "优化后的搜索查询",
            "reason": "为什么推荐这个查询"
        }
    ]
}

要求：
1. search_queries: 生成 3-5 个优化的 GitHub 搜索查询
2. recommendations: 提供 2-3 个推荐搜索策略
3. 考虑编程语言（如果提供）
4. 只返回 JSON，不要有其他文字"""
        
        user_message = f"""搜索查询：{query}
编程语言：{language or '未指定'}
推荐数量：{limit}"""
        
        messages = [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_message}
        ]
        
        response = self._make_request(messages)
        
        content = response["choices"][0]["message"]["content"]
        
        try:
            import json
            content = self._clean_json_response(content)
            recommendations = json.loads(content)
            
            return {
                "search_queries": recommendations.get("search_queries", []),
                "recommendations": recommendations.get("recommendations", [])
            }
        except json.JSONDecodeError:
            raise AIError(f"Failed to parse AI response: {content}")
    
    def extract_keywords(
        self,
        text: str,
        max_keywords: int = 10
    ) -> List[str]:
        """
        Extract keywords from text using AI.
        
        Args:
            text: Text to extract keywords from
            max_keywords: Maximum number of keywords to extract
            
        Returns:
            List of keywords
        """
        system_prompt = f"""你是一个关键词提取专家。你的任务是从给定的文本中提取最重要的关键词。

请提取关键词并返回 JSON 格式：
{{
    "keywords": ["关键词1", "关键词2", "关键词3", ...]
}}

要求：
1. 提取 {max_keywords} 个最相关的关键词
2. 关键词应该是技术术语、项目名称或功能描述
3. 只返回 JSON，不要有其他文字"""
        
        messages = [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": text}
        ]
        
        response = self._make_request(messages)
        
        content = response["choices"][0]["message"]["content"]
        
        try:
            import json
            content = self._clean_json_response(content)
            result = json.loads(content)
            return result.get("keywords", [])
        except json.JSONDecodeError:
            raise AIError(f"Failed to parse AI response: {content}")
    
    def generate_project_insights(
        self,
        repo_data: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Generate insights from repository analysis data.
        
        Args:
            repo_data: Repository analysis data
            
        Returns:
            Dictionary containing insights and recommendations
        """
        system_prompt = """你是一个 GitHub 项目健康度分析专家。你的任务是根据仓库的健康度数据生成智能见解和建议。

请根据给定的健康度数据，返回以下格式的 JSON 响应：
{
    "health_assessment": "整体健康度评估（1-2句话）",
    "strengths": ["优势1", "优势2", ...],
    "weaknesses": ["劣势1", "劣势2", ...],
    "recommendations": ["建议1", "建议2", "建议3"]
}

要求：
1. health_assessment: 基于健康度评分给出整体评估
2. strengths: 列出 2-3 个项目优势
3. weaknesses: 列出 1-2 个需要改进的地方
4. recommendations: 提供 2-3 个具体的改进建议
5. 只返回 JSON，不要有其他文字"""
        
        health = repo_data.get("health", {})
        metrics = repo_data.get("metrics", {})
        
        user_message = f"""健康度评分：{health.get('score', 0)}/100
健康状态：{health.get('status', 'unknown')}

提交频率：{metrics.get('commit_frequency', {}).get('per_day', 0)}/天
Issue 关闭率：{metrics.get('issue_activity', {}).get('close_rate', 0)}%
PR 合并率：{metrics.get('pr_activity', {}).get('merge_rate', 0)}%
贡献者数量：{metrics.get('contributor_activity', {}).get('total', 0)}"""
        
        messages = [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_message}
        ]
        
        response = self._make_request(messages)
        
        content = response["choices"][0]["message"]["content"]
        
        try:
            import json
            content = self._clean_json_response(content)
            insights = json.loads(content)
            
            return {
                "health_assessment": insights.get("health_assessment", ""),
                "strengths": insights.get("strengths", []),
                "weaknesses": insights.get("weaknesses", []),
                "recommendations": insights.get("recommendations", [])
            }
        except json.JSONDecodeError:
            raise AIError(f"Failed to parse AI response: {content}")
    
    def chat(
        self,
        messages: List[Dict[str, str]],
        system_prompt: Optional[str] = None,
        **kwargs
    ) -> str:
        """
        Chat with AI using a simple message interface.
        
        Args:
            messages: List of message dictionaries with 'role' and 'content'
            system_prompt: Optional system prompt to prepend
            **kwargs: Additional parameters for the API
            
        Returns:
            AI response text
        """
        final_messages = []
        
        if system_prompt:
            final_messages.append({"role": "system", "content": system_prompt})
        
        final_messages.extend(messages)
        
        response = self._make_request(final_messages, **kwargs)
        
        return response["choices"][0]["message"]["content"]
    
    def search_similar_projects(
        self,
        query: str,
        language: Optional[str] = None,
        limit: int = 5
    ) -> List[Dict[str, Any]]:
        """
        Search for similar projects using AI.
        
        Args:
            query: Search query
            language: Programming language filter
            limit: Maximum number of results
            
        Returns:
            List of similar projects
        """
        recommendations = self.recommend_similar_projects(query, language, limit)
        
        search_queries = recommendations.get("search_queries", [])
        
        projects = []
        
        for search_query in search_queries[:limit]:
            projects.append({
                "name": f"基于 '{search_query}' 的搜索结果",
                "description": f"使用查询: {search_query}",
                "language": language or "未知",
                "stars": 0,
                "url": f"https://github.com/search?q={search_query}"
            })
        
        return projects
