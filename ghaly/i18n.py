"""
Internationalization (i18n) module for ghaly.

This module provides translation support for UI strings in multiple languages.
"""

from typing import Dict


TRANSLATIONS: Dict[str, Dict[str, str]] = {
    "zh": {
        "welcome_title": "欢迎使用 GHALY",
        "welcome_subtitle": "GitHub 项目活动分析工具",
        "logged_in": "已登录 GitHub",
        "not_logged_in": "未登录 GitHub",
        "login_prompt": "使用 'ghaly auth login' 登录",
        "username": "用户名",
        "working_dir": "工作目录",
        "input_prompt": "请输入你的问题或命令",
        "help_hint": "输入 /help 查看可用命令",
        "exit_hint": "按 Ctrl+C 退出",
        "processing_request": "正在处理你的请求...",
        "analyzing_repo": "正在分析",
        "searching": "正在搜索",
        "last_days": "最近",
        "days": "天",
        "ai_response_failed": "AI 响应失败，请重试。",
        "api_key_invalid": "AI API 密钥无效，请检查配置。",
        "processing_error": "处理请求时出错",
        "error_details": "详细信息",
        "command_not_recognized": "无法识别的命令",
        "repo_name_error": "仓库名称格式错误，应为 'owner/repo'",
        "repo_not_recognized": "无法识别仓库名称",
        "search_keyword_error": "无法识别搜索关键词",
        "ai_client_not_configured": "AI 客户端未配置",
        "analyzer_not_initialized": "分析器未初始化，请先登录",
        "analysis_failed": "分析失败",
        "search_failed": "搜索失败",
        "analysis_result_format_error": "分析结果格式错误",
        "logout_confirm": "确认退出登录？",
        "logout_confirm_hint": "请输入 'yes' 确认，或输入 'no' 取消",
        "logout_cancelled": "已取消退出登录",
        "logout_success": "已成功退出登录",
        "language_switched": "语言已切换为",
        "language_invalid": "无效的语言选项",
        "language_options": "可用语言: zh (中文), en (English)",
        "language_current": "当前语言",
        "help_title": "可用命令",
        "help_analyze": "分析 GitHub 仓库",
        "help_search": "搜索相似项目",
        "help_status": "查看登录状态",
        "help_logout": "退出登录",
        "help_language": "切换语言",
        "help_clear": "清空屏幕",
        "help_help": "显示帮助信息",
        "help_exit": "退出程序",
        "help_usage_analyze": "用法: /analyze <owner/repo> [--days <days>]",
        "help_usage_search": "用法: /search \"<query>\" [--language <lang>] [--limit <num>]",
        "help_usage_language": "用法: /language <zh|en>",
        "repo_info": "仓库信息",
        "repo_name": "仓库名称",
        "description": "描述",
        "language": "语言",
        "stars": "星标",
        "forks": "分支",
        "created": "创建时间",
        "updated": "更新时间",
        "last_push": "最后推送",
        "activity_metrics": "活动指标",
        "commit_frequency": "提交频率",
        "commits_total": "总提交数",
        "commits_per_day": "每天",
        "commits_per_week": "每周",
        "commits_per_month": "每月",
        "issue_activity": "Issue 活动",
        "pr_activity": "PR 活动",
        "contributor_activity": "贡献者活动",
        "code_velocity": "代码速度",
        "community_engagement": "社区参与度",
        "health_status": "健康状态",
        "health_active": "活跃",
        "health_moderate": "中等",
        "health_inactive": "不活跃",
        "health_score": "健康分数",
        "languages": "编程语言",
        "contributors": "贡献者",
        "search_results": "搜索结果",
        "no_results": "未找到结果",
        "total_results": "共找到",
        "results": "个结果",
        "loading": "加载中",
        "done": "完成",
        "error": "错误",
        "warning": "警告",
        "info": "信息",
        "success": "成功",
        "assistant": "助手",
        "user": "用户",
        "system": "系统"
    },
    "en": {
        "welcome_title": "Welcome to GHALY",
        "welcome_subtitle": "GitHub Project Activity Analysis Tool",
        "logged_in": "Logged in to GitHub",
        "not_logged_in": "Not logged in to GitHub",
        "login_prompt": "Use 'ghaly auth login' to login",
        "username": "Username",
        "working_dir": "Working Directory",
        "input_prompt": "Enter your question or command",
        "help_hint": "Type /help to see available commands",
        "exit_hint": "Press Ctrl+C to exit",
        "processing_request": "Processing your request...",
        "analyzing_repo": "Analyzing",
        "searching": "Searching",
        "last_days": "Last",
        "days": "days",
        "ai_response_failed": "AI response failed, please try again.",
        "api_key_invalid": "AI API key is invalid, please check configuration.",
        "processing_error": "Error processing request",
        "error_details": "Details",
        "command_not_recognized": "Unrecognized command",
        "repo_name_error": "Repository name format error, should be 'owner/repo'",
        "repo_not_recognized": "Unable to recognize repository name",
        "search_keyword_error": "Unable to recognize search keyword",
        "ai_client_not_configured": "AI client not configured",
        "analyzer_not_initialized": "Analyzer not initialized, please login first",
        "analysis_failed": "Analysis failed",
        "search_failed": "Search failed",
        "analysis_result_format_error": "Analysis result format error",
        "logout_confirm": "Confirm logout?",
        "logout_confirm_hint": "Enter 'yes' to confirm, or 'no' to cancel",
        "logout_cancelled": "Logout cancelled",
        "logout_success": "Successfully logged out",
        "language_switched": "Language switched to",
        "language_invalid": "Invalid language option",
        "language_options": "Available languages: zh (中文), en (English)",
        "language_current": "Current language",
        "help_title": "Available Commands",
        "help_analyze": "Analyze GitHub repository",
        "help_search": "Search similar projects",
        "help_status": "View login status",
        "help_logout": "Logout",
        "help_language": "Switch language",
        "help_clear": "Clear screen",
        "help_help": "Show help information",
        "help_exit": "Exit program",
        "help_usage_analyze": "Usage: /analyze <owner/repo> [--days <days>]",
        "help_usage_search": 'Usage: /search "<query>" [--language <lang>] [--limit <num>]',
        "help_usage_language": "Usage: /language <zh|en>",
        "repo_info": "Repository Information",
        "repo_name": "Repository Name",
        "description": "Description",
        "language": "Language",
        "stars": "Stars",
        "forks": "Forks",
        "created": "Created",
        "updated": "Updated",
        "last_push": "Last Push",
        "activity_metrics": "Activity Metrics",
        "commit_frequency": "Commit Frequency",
        "commits_total": "Total Commits",
        "commits_per_day": "per day",
        "commits_per_week": "per week",
        "commits_per_month": "per month",
        "issue_activity": "Issue Activity",
        "pr_activity": "PR Activity",
        "contributor_activity": "Contributor Activity",
        "code_velocity": "Code Velocity",
        "community_engagement": "Community Engagement",
        "health_status": "Health Status",
        "health_active": "Active",
        "health_moderate": "Moderate",
        "health_inactive": "Inactive",
        "health_score": "Health Score",
        "languages": "Programming Languages",
        "contributors": "Contributors",
        "search_results": "Search Results",
        "no_results": "No results found",
        "total_results": "Found",
        "results": "results",
        "loading": "Loading",
        "done": "Done",
        "error": "Error",
        "warning": "Warning",
        "info": "Info",
        "success": "Success",
        "assistant": "Assistant",
        "user": "User",
        "system": "System"
    }
}


def translate(key: str, language: str = "zh", **kwargs) -> str:
    """
    Translate a key to the specified language.
    
    Args:
        key: Translation key
        language: Language code ('zh' or 'en')
        **kwargs: Format arguments for the translated string
        
    Returns:
        Translated string
    """
    if language not in TRANSLATIONS:
        language = "zh"
    
    translations = TRANSLATIONS[language]
    text = translations.get(key, key)
    
    if kwargs:
        return text.format(**kwargs)
    
    return text


def get_available_languages() -> list[str]:
    """
    Get list of available languages.
    
    Returns:
        List of language codes
    """
    return list(TRANSLATIONS.keys())


class Translator:
    """
    Translator class for managing translations.
    """
    
    def __init__(self, language: str = "zh"):
        """
        Initialize translator.
        
        Args:
            language: Language code ('zh' or 'en')
        """
        self.language = language
    
    def set_language(self, language: str) -> None:
        """
        Set current language.
        
        Args:
            language: Language code ('zh' or 'en')
        """
        if language in TRANSLATIONS:
            self.language = language
    
    def get(self, key: str, **kwargs) -> str:
        """
        Get translated string.
        
        Args:
            key: Translation key
            **kwargs: Format arguments for the translated string
            
        Returns:
            Translated string
        """
        return translate(key, self.language, **kwargs)
    
    def __call__(self, key: str, **kwargs) -> str:
        """
        Get translated string using callable syntax.
        
        Args:
            key: Translation key
            **kwargs: Format arguments for the translated string
            
        Returns:
            Translated string
        """
        return self.get(key, **kwargs)
