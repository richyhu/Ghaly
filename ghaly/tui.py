"""
Interactive TUI interface for ghaly.

This module provides a modern terminal-based UI similar to ClaudeCode,
supporting natural language conversation and AI-driven interactions.
"""

from typing import Any, Dict, List, Optional
from datetime import datetime

from textual.app import App, ComposeResult
from textual.containers import Container, Horizontal, Vertical
from textual.widgets import (
    Header,
    Footer,
    Input,
    RichLog,
    Button,
    Static,
    TabbedContent,
    TabPane,
    Tabs,
    DataTable,
    Markdown,
)
from textual.reactive import reactive
from textual import events
from textual.binding import Binding
from rich.text import Text
from rich.markdown import Markdown as RichMarkdown

from ghaly.config import ConfigManager
from ghaly.github_api import GitHubClient
from ghaly.analyzer import RepositoryAnalyzer
from ghaly.ai_client import AIClient


class Message:
    """Represents a chat message."""
    
    def __init__(self, role: str, content: str, timestamp: Optional[datetime] = None):
        self.role = role
        self.content = content
        self.timestamp = timestamp or datetime.now()
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "role": self.role,
            "content": self.content,
            "timestamp": self.timestamp.isoformat()
        }


class ChatLog(RichLog):
    """Custom rich log for chat messages."""
    
    def add_user_message(self, message: str) -> None:
        """Add a user message to the log."""
        timestamp = datetime.now().strftime("%H:%M:%S")
        self.write(f"[bold cyan]👤 用户 [{timestamp}][/bold cyan]")
        self.write(f"  {message}\n")
    
    def add_assistant_message(self, message: str) -> None:
        """Add an assistant message to the log."""
        timestamp = datetime.now().strftime("%H:%M:%S")
        self.write(f"[bold green]🤖 Ghaly [{timestamp}][/bold green]")
        self.write(f"  {message}\n")
    
    def add_system_message(self, message: str) -> None:
        """Add a system message to the log."""
        self.write(f"[bold yellow]⚙️ 系统[/bold yellow]")
        self.write(f"  {message}\n")
    
    def add_error_message(self, message: str) -> None:
        """Add an error message to the log."""
        self.write(f"[bold red]❌ 错误[/bold red]")
        self.write(f"  {message}\n")
    
    def add_info_message(self, message: str) -> None:
        """Add an info message to the log."""
        self.write(f"[bold blue]ℹ️ 信息[/bold blue]")
        self.write(f"  {message}\n")


class GhalyTUI(App):
    """Main TUI application for ghaly."""
    
    BINDINGS = [
        Binding("ctrl+q", "quit", "退出"),
        Binding("ctrl+c", "quit", "退出"),
        Binding("ctrl+l", "clear_chat", "清空聊天"),
        Binding("ctrl+h", "show_help", "帮助"),
    ]
    
    CSS = """
    Screen {
        background: #1a1a2e;
    }
    
    Header {
        background: #16213e;
        text-style: bold;
    }
    
    Footer {
        background: #16213e;
    }
    
    #chat-container {
        height: 1fr;
    }
    
    #input-container {
        height: 3;
        dock: bottom;
    }
    
    #sidebar {
        width: 30;
        background: #0f3460;
    }
    
    ChatLog {
        background: #1a1a2e;
        border: solid #e94560;
        padding: 1;
    }
    
    Input {
        margin: 1;
    }
    
    Button {
        margin: 1;
    }
    
    DataTable {
        background: #1a1a2e;
    }
    
    .welcome-text {
        text-align: center;
        color: #e94560;
    }
    """
    
    def __init__(self):
        super().__init__()
        self.config = ConfigManager()
        self.github_client: Optional[GitHubClient] = None
        self.analyzer: Optional[RepositoryAnalyzer] = None
        self.ai_client: Optional[AIClient] = None
        self.messages: List[Message] = []
        self.current_repository: Optional[str] = None
        
        self._init_clients()
    
    def _init_clients(self) -> None:
        """Initialize API clients."""
        token = self.config.get_token('github')
        if token:
            self.github_client = GitHubClient(token)
            self.analyzer = RepositoryAnalyzer(self.github_client)
        
        api_key = self.config.get_env('OPENAI_API_KEY') or self.config.get('openai.api_key')
        if api_key:
            self.ai_client = AIClient(api_key)
    
    def compose(self) -> ComposeResult:
        """Compose the UI."""
        yield Header()
        
        with Container(id="main-container"):
            with Horizontal():
                with Vertical(id="sidebar"):
                    yield Static("📊 快捷操作", classes="sidebar-title")
                    yield Button("🔍 分析仓库", id="btn-analyze", variant="primary")
                    yield Button("🤖 AI 搜索", id="btn-search", variant="primary")
                    yield Button("⚙️ 配置", id="btn-config", variant="default")
                    yield Button("ℹ️ 帮助", id="btn-help", variant="default")
                
                with Vertical(id="chat-container"):
                    yield ChatLog(id="chat-log")
            
            with Container(id="input-container"):
                yield Input(placeholder="输入命令或自然语言描述，例如：'分析 facebook/react 仓库'...", id="user-input")
        
        yield Footer()
    
    def on_mount(self) -> None:
        """Called when the app is mounted."""
        chat_log = self.query_one("#chat-log", ChatLog)
        chat_log.add_system_message("欢迎使用 Ghaly！")
        chat_log.add_info_message("你可以用自然语言与我对话，例如：")
        chat_log.add_info_message("  • '分析 facebook/react 仓库'")
        chat_log.add_info_message("  • '搜索 Python 机器学习项目'")
        chat_log.add_info_message("  • '查看我的认证状态'")
        chat_log.add_info_message("  • '配置 OAuth'")
        chat_log.add_info_message("\n按 Ctrl+Q 退出，Ctrl+H 查看帮助")
    
    def on_input_submitted(self, event: Input.Submitted) -> None:
        """Handle input submission."""
        user_input = event.value.strip()
        
        if not user_input:
            return
        
        chat_log = self.query_one("#chat-log", ChatLog)
        chat_log.add_user_message(user_input)
        
        event.value = ""
        
        self.process_user_input(user_input)
    
    def on_button_pressed(self, event: Button.Pressed) -> None:
        """Handle button presses."""
        button_id = event.button.id
        
        if button_id == "btn-analyze":
            self.query_one("#user-input", Input).value = "分析仓库"
        elif button_id == "btn-search":
            self.query_one("#user-input", Input).value = "搜索项目"
        elif button_id == "btn-config":
            self.query_one("#user-input", Input).value = "配置"
        elif button_id == "btn-help":
            self.action_show_help()
    
    def process_user_input(self, user_input: str) -> None:
        """Process user input with natural language understanding."""
        chat_log = self.query_one("#chat-log", ChatLog)
        
        try:
            if not self.ai_client:
                chat_log.add_error_message("AI 客户端未配置。请先配置 OpenAI API 密钥。")
                chat_log.add_info_message("使用 'ghaly auth configure' 配置 OAuth")
                chat_log.add_info_message("设置 OPENAI_API_KEY 环境变量")
                return
            
            chat_log.add_info_message("正在处理你的请求...")
            
            response = self.ai_client.chat(
                messages=[{"role": "user", "content": user_input}],
                system_prompt=self._get_system_prompt()
            )
            
            if response:
                chat_log.add_assistant_message(response)
                
                self._execute_command_from_response(response)
            else:
                chat_log.add_error_message("AI 响应失败，请重试。")
        
        except Exception as e:
            chat_log.add_error_message(f"处理请求时出错: {str(e)}")
    
    def _get_system_prompt(self) -> str:
        """Get the system prompt for AI."""
        return """你是 Ghaly，一个 GitHub 项目分析助手。你的任务是理解用户的自然语言请求，并返回结构化的命令。

你可以帮助用户：
1. 分析 GitHub 仓库的活跃度和健康状况
2. 搜索和推荐相似的项目
3. 查看 GitHub 认证状态
4. 配置 OAuth 应用

当用户提出请求时，请：
1. 理解用户的意图
2. 提取关键信息（仓库名称、搜索关键词等）
3. 返回相应的命令和说明

支持的命令格式：
- 分析仓库：ANALYZE <owner>/<repo> [--days N]
- 搜索项目：SEARCH <query> [--language <lang>] [--limit N]
- 查看状态：STATUS
- 配置：CONFIGURE

请用中文回复，并保持简洁友好。"""
    
    def _execute_command_from_response(self, response: str) -> None:
        """Execute command based on AI response."""
        chat_log = self.query_one("#chat-log", ChatLog)
        
        response_upper = response.upper()
        
        if "ANALYZE" in response_upper:
            self._execute_analyze_command(response)
        elif "SEARCH" in response_upper:
            self._execute_search_command(response)
        elif "STATUS" in response_upper:
            self._execute_status_command()
        elif "CONFIGURE" in response_upper:
            self._execute_configure_command()
    
    def _execute_analyze_command(self, response: str) -> None:
        """Execute analyze command."""
        chat_log = self.query_one("#chat-log", ChatLog)
        
        try:
            import re
            
            match = re.search(r'ANALYZE\s+([^\s]+)', response)
            if not match:
                chat_log.add_error_message("无法识别仓库名称")
                return
            
            repo_path = match.group(1)
            
            if "/" not in repo_path:
                chat_log.add_error_message("仓库名称格式错误，应为 'owner/repo'")
                return
            
            owner, repo = repo_path.split("/", 1)
            
            days_match = re.search(r'--days\s+(\d+)', response)
            days = int(days_match.group(1)) if days_match else 30
            
            chat_log.add_info_message(f"正在分析 {owner}/{repo} (最近 {days} 天)...")
            
            if not self.analyzer:
                chat_log.add_error_message("分析器未初始化，请先登录")
                return
            
            result = self.analyzer.analyze_repository(owner, repo)
            
            self._display_analysis_result(result)
        
        except Exception as e:
            chat_log.add_error_message(f"分析失败: {str(e)}")
    
    def _execute_search_command(self, response: str) -> None:
        """Execute search command."""
        chat_log = self.query_one("#chat-log", ChatLog)
        
        try:
            import re
            
            match = re.search(r'SEARCH\s+"([^"]+)"', response)
            if not match:
                chat_log.add_error_message("无法识别搜索关键词")
                return
            
            query = match.group(1)
            
            lang_match = re.search(r'--language\s+(\w+)', response)
            language = lang_match.group(1) if lang_match else None
            
            limit_match = re.search(r'--limit\s+(\d+)', response)
            limit = int(limit_match.group(1)) if limit_match else 5
            
            chat_log.add_info_message(f"正在搜索: {query}...")
            
            if not self.ai_client:
                chat_log.add_error_message("AI 客户端未配置")
                return
            
            results = self.ai_client.search_similar_projects(query, language=language, limit=limit)
            
            self._display_search_results(results)
        
        except Exception as e:
            chat_log.add_error_message(f"搜索失败: {str(e)}")
    
    def _execute_status_command(self) -> None:
        """Execute status command."""
        chat_log = self.query_one("#chat-log", ChatLog)
        
        token = self.config.get_token('github')
        
        if token:
            chat_log.add_info_message("✅ 已登录 GitHub")
            chat_log.add_info_message(f"Token: {token[:20]}...")
        else:
            chat_log.add_info_message("❌ 未登录 GitHub")
            chat_log.add_info_message("使用 'ghaly auth login' 登录")
        
        api_key = self.config.get_env('OPENAI_API_KEY') or self.config.get('openai.api_key')
        if api_key:
            chat_log.add_info_message("✅ OpenAI API 已配置")
        else:
            chat_log.add_info_message("❌ OpenAI API 未配置")
    
    def _execute_configure_command(self) -> None:
        """Execute configure command."""
        chat_log = self.query_one("#chat-log", ChatLog)
        chat_log.add_info_message("配置指南：")
        chat_log.add_info_message("1. GitHub OAuth:")
        chat_log.add_info_message("   - 访问 https://github.com/settings/developers")
        chat_log.add_info_message("   - 创建 OAuth 应用")
        chat_log.add_info_message("   - 运行: ghaly auth configure")
        chat_log.add_info_message("   - 运行: ghaly auth login")
        chat_log.add_info_message("\n2. OpenAI API:")
        chat_log.add_info_message("   - 设置环境变量: export OPENAI_API_KEY=your_key")
        chat_log.add_info_message("   - 或在 .env 文件中添加: OPENAI_API_KEY=your_key")
    
    def _display_analysis_result(self, result: Dict[str, Any]) -> None:
        """Display analysis result in chat."""
        chat_log = self.query_one("#chat-log", ChatLog)
        
        repo = result["repository"]
        metrics = result["metrics"]
        health = result["health"]
        
        chat_log.add_assistant_message(f"📊 仓库分析结果: {repo['full_name']}")
        chat_log.add_info_message(f"描述: {repo.get('description', '无')}")
        chat_log.add_info_message(f"语言: {repo.get('language', '未知')}")
        chat_log.add_info_message(f"⭐ Stars: {repo['stars']}")
        chat_log.add_info_message(f"🍴 Forks: {repo['forks']}")
        
        chat_log.add_info_message(f"\n📈 活跃度指标:")
        chat_log.add_info_message(f"  • 提交频率: {metrics['commit_frequency']['per_day']} 次/天")
        chat_log.add_info_message(f"  • Issue 活动: {metrics['issue_activity']['total']} 个")
        chat_log.add_info_message(f"  • PR 活动: {metrics['pr_activity']['total']} 个")
        chat_log.add_info_message(f"  • 贡献者: {metrics['contributor_activity']['total']} 人")
        
        status_emoji = "🟢" if health["status"] == "active" else "🟡" if health["status"] == "moderate" else "🔴"
        chat_log.add_info_message(f"\n{status_emoji} 健康评分: {health['score']}/100 ({health['status']})")
    
    def _display_search_results(self, results: List[Dict[str, Any]]) -> None:
        """Display search results in chat."""
        chat_log = self.query_one("#chat-log", ChatLog)
        
        if not results:
            chat_log.add_info_message("未找到相关项目")
            return
        
        chat_log.add_assistant_message(f"🔍 找到 {len(results)} 个相关项目:")
        
        for i, repo in enumerate(results, 1):
            chat_log.add_info_message(f"\n{i}. {repo.get('name', '未知')}")
            chat_log.add_info_message(f"   描述: {repo.get('description', '无')}")
            chat_log.add_info_message(f"   语言: {repo.get('language', '未知')}")
            chat_log.add_info_message(f"   Stars: {repo.get('stars', 0)}")
    
    def action_clear_chat(self) -> None:
        """Clear the chat log."""
        chat_log = self.query_one("#chat-log", ChatLog)
        chat_log.clear()
        chat_log.add_system_message("聊天记录已清空")
    
    def action_show_help(self) -> None:
        """Show help information."""
        chat_log = self.query_one("#chat-log", ChatLog)
        chat_log.add_system_message("📚 帮助信息")
        chat_log.add_info_message("\n快捷键:")
        chat_log.add_info_message("  Ctrl+Q - 退出")
        chat_log.add_info_message("  Ctrl+C - 退出")
        chat_log.add_info_message("  Ctrl+L - 清空聊天")
        chat_log.add_info_message("  Ctrl+H - 显示帮助")
        chat_log.add_info_message("\n自然语言示例:")
        chat_log.add_info_message("  • '分析 facebook/react 仓库'")
        chat_log.add_info_message("  • '搜索 Python 机器学习项目'")
        chat_log.add_info_message("  • '查看我的认证状态'")
        chat_log.add_info_message("  • '配置 OAuth'")


def run_tui() -> None:
    """Run the TUI application."""
    app = GhalyTUI()
    app.run()
