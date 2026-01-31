"""
Interactive REPL interface for ghaly - ClaudeCode style.

This module provides a clean, modern text-based interface
similar to ClaudeCode with proper input box styling.
"""

from typing import Any, Dict, List, Optional
from datetime import datetime
import sys
import getpass
import os

from rich.console import Console
from rich.panel import Panel
from rich.markdown import Markdown
from rich.text import Text
from rich.align import Align
from rich.style import Style
from rich.table import Table

from ghaly.config import ConfigManager
from ghaly.github_api import GitHubClient
from ghaly.analyzer import RepositoryAnalyzer
from ghaly.ai_client import AIClient
from ghaly.i18n import Translator


class ClaudeCodeStyleREPL:
    """ClaudeCode-style REPL interface for ghaly."""
    
    def __init__(self):
        self.console = Console()
        self.config = ConfigManager()
        self.translator = Translator(self.config.get_language())
        self.github_client: Optional[GitHubClient] = None
        self.analyzer: Optional[RepositoryAnalyzer] = None
        self.ai_client: Optional[AIClient] = None
        self.messages: List[Dict[str, str]] = []
        self.running = True
        self.user_name = getpass.getuser()
        self.github_username = None
        self.current_path = os.getcwd()
        self.ctrl_c_count = 0
        
        self._init_clients()
    
    def _init_clients(self) -> None:
        """Initialize API clients."""
        token_data = self.config.get_token('github')
        if token_data:
            token = token_data.get('access_token', token_data.get('token'))
            if token:
                self.github_client = GitHubClient(token)
                self.analyzer = RepositoryAnalyzer(self.github_client)
                try:
                    user_data = self.github_client.get_user()
                    self.github_username = user_data.get('login', None)
                except Exception:
                    self.github_username = None
        
        self.ai_client = AIClient()
    
    def _print_welcome_banner(self) -> None:
        """Print welcome banner with ghaly logo."""
        logo_text = """
  ██████╗██╗  ██╗█████╗██╗ ██╗   ██╗ 
 ██╔════╝██║  ████╔══████║ ╚██╗ ██╔╝ 
 ██║  ███████████████████║  ╚████╔╝ 
 ██║   ████╔══████╔══████║   ╚██╔╝  
 ╚██████╔██║  ████║  ███████████║   
  ╚═════╝╚═╝  ╚═╚═╝  ╚═╚══════╚═╝   
"""
        
        welcome_info = Text()
        welcome_info.append(self.translator.get("welcome_title"), style="bold white")
        welcome_info.append("\n\n")
        welcome_info.append(self.translator.get("welcome_subtitle") + " • v0.1.0", style="dim white")
        welcome_info.append("\n\n")
        display_name = self.github_username if self.github_username else self.user_name
        welcome_info.append(f"{self.translator.get('username')}: {display_name}", style="dim white")
        welcome_info.append("\n")
        welcome_info.append(f"{self.translator.get('working_dir')}: {self.current_path}", style="dim white")
        welcome_info.append("\n\n")
        welcome_info.append("────────────────────────", style="rgb(255,165,0)")
        welcome_info.append("\n\n")
        welcome_info.append("• Analyze facebook/react repository", style="white")
        welcome_info.append("\n")
        welcome_info.append("• Search Python ML projects", style="white")
        welcome_info.append("\n")
        welcome_info.append("• View authentication status", style="white")
        welcome_info.append("\n")
        welcome_info.append("• Configure OAuth", style="white")
        welcome_info.append("\n\n")
        welcome_info.append(self.translator.get("exit_hint"), style="dim white")
        welcome_info.append("\n")
        welcome_info.append(self.translator.get("help_hint"), style="dim white")
        
        table = Table(show_header=False, show_footer=False, box=None, padding=0)
        table.add_column(width=45)
        table.add_column()
        
        logo = Text()
        logo.append(logo_text, style="bold rgb(255,165,0)")
        
        table.add_row(logo, welcome_info)
        
        panel = Panel(
            table,
            border_style="rgb(255,165,0)",
            padding=(1, 2)
        )
        self.console.print(panel)
    
    def _print_input_box(self) -> str:
        """Print input box with simple style."""
        self.console.print()
        self.console.print(f"[bold rgb(255,165,0)]➜[/bold rgb(255,165,0)] [white]", end="")
        user_input = input("")
        return user_input.strip()
    
    def _print_user_message(self, message: str) -> None:
        """Print user message."""
        timestamp = datetime.now().strftime("%H:%M")
        content = Text(message, style="white")
        panel = Panel(
            content,
            title=f"[bold rgb(255,165,0)]你 [{timestamp}][/bold rgb(255,165,0)]",
            border_style="rgb(255,165,0)",
            padding=(0, 1)
        )
        self.console.print()
        self.console.print(panel)
    
    def _print_assistant_message(self, message: str) -> None:
        """Print assistant message."""
        timestamp = datetime.now().strftime("%H:%M")
        
        if message.strip().startswith('#') or '```' in message:
            content = Markdown(message)
        else:
            content = Text(message, style="white")
        
        panel = Panel(
            content,
            title=f"[bold rgb(255,165,0)]Ghaly [{timestamp}][/bold rgb(255,165,0)]",
            border_style="rgb(255,165,0)",
            padding=(0, 1)
        )
        self.console.print()
        self.console.print(panel)
    
    def _print_system_message(self, message: str) -> None:
        """Print system message."""
        content = Text(message, style="white")
        panel = Panel(
            content,
            title="[bold yellow]系统[/bold yellow]",
            border_style="yellow",
            padding=(0, 1)
        )
        self.console.print()
        self.console.print(panel)
    
    def _print_error_message(self, message: str) -> None:
        """Print error message."""
        content = Text(message, style="white")
        panel = Panel(
            content,
            title="[bold red]错误[/bold red]",
            border_style="red",
            padding=(0, 1)
        )
        self.console.print()
        self.console.print(panel)
    
    def _print_info_message(self, message: str) -> None:
        """Print info message."""
        content = Text(message, style="white")
        panel = Panel(
            content,
            title="[bold cyan]信息[/bold cyan]",
            border_style="cyan",
            padding=(0, 1)
        )
        self.console.print()
        self.console.print(panel)
    
    def _print_help(self) -> None:
        """Print help information."""
        help_text = f"""
[bold rgb(255,165,0)]📚 {self.translator.get("help_title")}[/bold rgb(255,165,0)]

[bold yellow]{self.translator.get("help_analyze")}:[/bold yellow]
  [white]•[/white] [dim]{self.translator.get("help_usage_analyze")}[/dim]

[bold yellow]{self.translator.get("help_search")}:[/bold yellow]
  [white]•[/white] [dim]{self.translator.get("help_usage_search")}[/dim]

[bold yellow]{self.translator.get("help_language")}:[/bold yellow]
  [white]•[/white] [dim]{self.translator.get("help_usage_language")}[/dim]

[bold yellow]{self.translator.get("help_status")}:[/bold yellow]
  [white]•[/white] [dim]/status[/dim]

[bold yellow]{self.translator.get("help_logout")}:[/bold yellow]
  [white]•[/white] [dim]/logout[/dim]

[bold yellow]{self.translator.get("help_clear")}:[/bold yellow]
  [white]•[/white] [dim]/clear[/dim]

[bold yellow]{self.translator.get("help_help")}:[/bold yellow]
  [white]•[/white] [dim]/help[/dim]

[bold yellow]{self.translator.get("help_exit")}:[/bold yellow]
  [white]•[/white] [dim]/quit 或 /exit[/dim]
        """
        self.console.print(Panel(help_text, title="[bold]帮助[/bold]", border_style="rgb(255,165,0)", padding=(1, 2)))
    
    def _get_system_prompt(self) -> str:
        """Get system prompt for AI."""
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
    
    def _process_user_input(self, user_input: str) -> None:
        """Process user input with natural language understanding."""
        user_input = user_input.strip()
        
        if not user_input:
            return
        
        self._print_user_message(user_input)
        
        if user_input.lower() in ['/quit', '/exit', '/退出']:
            self.running = False
            self._print_system_message(self.translator.get("success") + "!")
            return
        
        if user_input.lower() in ['/help', '/帮助']:
            self._print_help()
            return
        
        if user_input.lower() in ['/clear', '/清空']:
            self.console.clear()
            self._print_welcome_banner()
            return
        
        if user_input.lower() in ['/status', '/状态']:
            self._execute_status_command()
            return
        
        if user_input.lower() in ['/logout', '/退出登录']:
            self._execute_logout_command()
            return
        
        if user_input.lower().startswith('/language') or user_input.lower().startswith('/语言'):
            self._execute_language_command(user_input)
            return
        
        try:
            from rich.progress import Progress, SpinnerColumn, TextColumn, BarColumn, TaskProgressColumn, TimeRemainingColumn
            
            with Progress(
                SpinnerColumn(),
                TextColumn("[progress.description]{task.description}"),
                BarColumn(),
                TaskProgressColumn(),
                TimeRemainingColumn(),
                console=self.console,
                expand=True
            ) as progress:
                task = progress.add_task(
                    f"[cyan]{self.translator.get('processing_request')}[/cyan]",
                    total=100
                )
                
                progress.update(task, advance=20)
                
                response = self.ai_client.chat(
                    messages=[{"role": "user", "content": user_input}],
                    system_prompt=self._get_system_prompt()
                )
                
                progress.update(task, advance=80)
                progress.update(task, completed=100)
            
            if response:
                self._print_assistant_message(response)
                self._execute_command_from_response(response)
            else:
                self._print_error_message(self.translator.get("ai_response_failed"))
        
        except Exception as e:
            import traceback
            error_str = str(e)
            if "Api key is invalid" in error_str or "Unauthorized" in error_str:
                self._print_error_message(self.translator.get("api_key_invalid"))
            else:
                self._print_error_message(f"{self.translator.get('processing_error')}: {str(e)}")
                self._print_info_message(f"{self.translator.get('error_details')}: {traceback.format_exc()}")
    
    def _execute_command_from_response(self, response: str) -> None:
        """Execute command based on AI response."""
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
        try:
            import re
            from rich.progress import Progress, SpinnerColumn, TextColumn, BarColumn, TaskProgressColumn, TimeRemainingColumn
            
            match = re.search(r'ANALYZE\s+([^\s\n]+)', response)
            if not match:
                self._print_error_message(self.translator.get("repo_not_recognized"))
                return
            
            repo_path = match.group(1)
            
            if "/" not in repo_path:
                self._print_error_message(self.translator.get("repo_name_error"))
                return
            
            owner, repo = repo_path.split("/", 1)
            
            days_match = re.search(r'--days\s+(\d+)', response)
            days = int(days_match.group(1)) if days_match else 30
            
            if not self.analyzer:
                self._print_error_message(self.translator.get("analyzer_not_initialized"))
                return
            
            with Progress(
                SpinnerColumn(),
                TextColumn("[progress.description]{task.description}"),
                BarColumn(),
                TaskProgressColumn(),
                TimeRemainingColumn(),
                console=self.console,
                expand=True
            ) as progress:
                task = progress.add_task(
                    f"[cyan]{self.translator.get('analyzing_repo')} {owner}/{repo} ({self.translator.get('last_days')} {days} {self.translator.get('days')})...[/cyan]",
                    total=100
                )
                
                progress.update(task, advance=10)
                
                result = self.analyzer.analyze_repository(owner, repo)
                
                progress.update(task, advance=90)
                progress.update(task, completed=100)
            
            if isinstance(result, dict):
                self._display_analysis_result(result)
            else:
                self._print_error_message(f"{self.translator.get('analysis_result_format_error')}: {type(result)}")
        
        except Exception as e:
            import traceback
            self._print_error_message(f"{self.translator.get('analysis_failed')}: {str(e)}")
            self._print_info_message(f"{self.translator.get('error_details')}: {traceback.format_exc()}")
    
    def _execute_search_command(self, response: str) -> None:
        """Execute search command."""
        try:
            import re
            from rich.progress import Progress, SpinnerColumn, TextColumn, BarColumn, TaskProgressColumn, TimeRemainingColumn
            
            match = re.search(r'SEARCH\s+"([^"]+)"', response)
            if not match:
                self._print_error_message(self.translator.get("search_keyword_error"))
                return
            
            query = match.group(1)
            
            lang_match = re.search(r'--language\s+(\w+)', response)
            language = lang_match.group(1) if lang_match else None
            
            limit_match = re.search(r'--limit\s+(\d+)', response)
            limit = int(limit_match.group(1)) if limit_match else 5
            
            if not self.ai_client:
                self._print_error_message(self.translator.get("ai_client_not_configured"))
                return
            
            with Progress(
                SpinnerColumn(),
                TextColumn("[progress.description]{task.description}"),
                BarColumn(),
                TaskProgressColumn(),
                TimeRemainingColumn(),
                console=self.console,
                expand=True
            ) as progress:
                task = progress.add_task(
                    f"[cyan]{self.translator.get('searching')}: {query}...[/cyan]",
                    total=100
                )
                
                progress.update(task, advance=10)
                
                results = self.ai_client.search_similar_projects(query, language=language, limit=limit)
                
                progress.update(task, advance=90)
                progress.update(task, completed=100)
            
            self._display_search_results(results)
        
        except Exception as e:
            import traceback
            self._print_error_message(f"{self.translator.get('search_failed')}: {str(e)}")
            self._print_info_message(f"{self.translator.get('error_details')}: {traceback.format_exc()}")
    
    def _execute_status_command(self) -> None:
        """Execute status command."""
        token_data = self.config.get_token('github')
        
        if token_data:
            token = token_data.get('access_token', token_data.get('token'))
            if token:
                self._print_info_message(f"✅ {self.translator.get('logged_in')}")
                self._print_info_message(f"Token: {token[:20]}...")
                if self.github_username:
                    self._print_info_message(f"{self.translator.get('username')}: {self.github_username}")
            else:
                self._print_info_message(f"❌ {self.translator.get('not_logged_in')}")
                self._print_info_message(self.translator.get("login_prompt"))
        else:
            self._print_info_message(f"❌ {self.translator.get('not_logged_in')}")
            self._print_info_message(self.translator.get("login_prompt"))
        
        api_key = self.config.get_env('OPENAI_API_KEY') or self.config.get('openai.api_key')
        if api_key:
            self._print_info_message("✅ OpenAI API " + self.translator.get("info"))
        else:
            self._print_info_message("❌ OpenAI API " + self.translator.get("not_logged_in"))
            self._print_info_message("设置 OPENAI_API_KEY 环境变量")
    
    def _execute_logout_command(self) -> None:
        """Execute logout command."""
        try:
            self.config.remove_token('github')
            self.github_client = None
            self.analyzer = None
            self.github_username = None
            self._print_system_message("已退出登录")
            self._print_info_message("使用 'ghaly auth login' 重新登录")
        except Exception as e:
            self._print_error_message(f"退出登录失败: {str(e)}")
    
    def _execute_configure_command(self) -> None:
        """Execute configure command."""
        config_text = """
[bold rgb(255,165,0)]配置指南：[/bold rgb(255,165,0)]

[bold yellow]1. GitHub OAuth:[/bold yellow]
   [white]•[/white] [dim]访问 https://github.com/settings/developers[/dim]
   [white]•[/white] [dim]创建 OAuth 应用[/dim]
   [white]•[/white] [dim]运行: [cyan]ghaly auth configure[/cyan][/dim]
   [white]•[/white] [dim]运行: [cyan]ghaly auth login[/cyan][/dim]

[bold yellow]2. SiliconFlow API:[/bold yellow]
   [white]•[/white] [dim]已内置配置，无需手动设置[/dim]
        """
        self.console.print(Panel(config_text, title="[bold]配置[/bold]", border_style="rgb(255,165,0)", padding=(1, 2)))
    
    def _execute_language_command(self, user_input: str) -> None:
        """Execute language command."""
        try:
            import re
            
            match = re.search(r'/language\s+(\w+)', user_input, re.IGNORECASE)
            if not match:
                current_lang = self.config.get_language()
                lang_name = "中文" if current_lang == "zh" else "English"
                self._print_info_message(f"{self.translator.get('language_current')}: {lang_name} ({current_lang})")
                self._print_info_message(self.translator.get("language_options"))
                return
            
            new_lang = match.group(1).lower()
            
            if new_lang not in ['zh', 'en']:
                self._print_error_message(self.translator.get("language_invalid"))
                self._print_info_message(self.translator.get("language_options"))
                return
            
            self.config.set_language(new_lang)
            self.translator.set_language(new_lang)
            
            lang_name = "中文" if new_lang == "zh" else "English"
            self._print_system_message(f"{self.translator.get('language_switched')} {lang_name}")
            
            self.console.clear()
            self._print_welcome_banner()
        
        except Exception as e:
            import traceback
            self._print_error_message(f"{self.translator.get('processing_error')}: {str(e)}")
            self._print_info_message(f"{self.translator.get('error_details')}: {traceback.format_exc()}")
    
    def _display_analysis_result(self, result: Dict[str, Any]) -> None:
        """Display analysis result."""
        try:
            if not isinstance(result, dict):
                self._print_error_message(f"{self.translator.get('error')}: {type(result)}")
                return
            
            repo = result.get("repository", {})
            metrics = result.get("metrics", {})
            health = result.get("health", {})
            
            if not isinstance(repo, dict) or not isinstance(metrics, dict) or not isinstance(health, dict):
                self._print_error_message("结果数据结构错误")
                return
            
            result_text = f"""
[bold rgb(255,165,0)]📊 {self.translator.get('repo_info')}: {repo.get('full_name', '未知')}[/bold rgb(255,165,0)]

[yellow]{self.translator.get('description')}:[/yellow] [white]{repo.get('description', '无')}
[yellow]{self.translator.get('language')}:[/yellow] [white]{repo.get('language', '未知')}
[yellow]⭐ Stars:[/yellow] [white]{repo.get('stars', 0)}
[yellow]🍴 Forks:[/yellow] [white]{repo.get('forks', 0)}

[bold rgb(255,165,0)]📈 {self.translator.get('activity_metrics')}:[/bold rgb(255,165,0)]
  [white]•[/white] [dim]{self.translator.get('commit_frequency')}: {metrics.get('commit_frequency', {}).get('per_day', 0)} {self.translator.get('commits_per_day')}[/dim]
  [white]•[/white] [dim]{self.translator.get('issue_activity')}: {metrics.get('issue_activity', {}).get('total', 0)} 个[/dim]
  [white]•[/white] [dim]{self.translator.get('pr_activity')}: {metrics.get('pr_activity', {}).get('total', 0)} 个[/dim]
  [white]•[/white] [dim]{self.translator.get('contributors')}: {metrics.get('contributor_activity', {}).get('total', 0)} 人[/dim]

"""
            
            status = health.get('status', 'unknown')
            status_emoji = "🟢" if status == "active" else "🟡" if status == "moderate" else "🔴"
            result_text += f"{status_emoji} [bold rgb(255,165,0)]{self.translator.get('health_status')}: {health.get('score', 0)}/100 ({status})[/bold rgb(255,165,0)]"
            
            self.console.print(Panel(result_text, title="[bold]分析结果[/bold]", border_style="rgb(255,165,0)", padding=(1, 2)))
        
        except Exception as e:
            import traceback
            self._print_error_message(f"{self.translator.get('processing_error')}: {str(e)}")
            self._print_info_message(f"{self.translator.get('error_details')}: {traceback.format_exc()}")
    
    def _display_search_results(self, results: List[Dict[str, Any]]) -> None:
        """Display search results."""
        try:
            if not results:
                self._print_info_message(self.translator.get("no_results"))
                return
            
            if not isinstance(results, list):
                self._print_error_message(f"{self.translator.get('error')}: {type(results)}")
                return
            
            result_text = f"[bold rgb(255,165,0)]🔍 {self.translator.get('total_results')} {len(results)} {self.translator.get('results')}:[/bold rgb(255,165,0)]\n\n"
            
            for i, repo in enumerate(results, 1):
                if not isinstance(repo, dict):
                    continue
                result_text += f"[bold yellow]{i}. {repo.get('name', '未知')}[/bold yellow]\n"
                result_text += f"   [dim]{self.translator.get('description')}: {repo.get('description', '无')}[/dim]\n"
                result_text += f"   [dim]{self.translator.get('language')}: {repo.get('language', '未知')}[/dim]\n"
                result_text += f"   [dim]Stars: {repo.get('stars', 0)}\n\n[/dim]"
            
            self.console.print(Panel(result_text, title="[bold]搜索结果[/bold]", border_style="rgb(255,165,0)", padding=(1, 2)))
        
        except Exception as e:
            import traceback
            self._print_error_message(f"{self.translator.get('processing_error')}: {str(e)}")
            self._print_info_message(f"{self.translator.get('error_details')}: {traceback.format_exc()}")
    
    def run(self) -> None:
        """Run REPL loop."""
        import os
        print('\033[2J\033[H', end='', flush=True)
        os.system('clear' if os.name != 'nt' else 'cls')
        self.console.clear()
        self._print_welcome_banner()
        
        while self.running:
            try:
                user_input = self._print_input_box()
                self._process_user_input(user_input)
                self.ctrl_c_count = 0
            except KeyboardInterrupt:
                self.ctrl_c_count += 1
                if self.ctrl_c_count == 1:
                    self.console.print("\n[yellow]再按一次 Ctrl+C 退出[/yellow]")
                elif self.ctrl_c_count == 2:
                    self.console.print("\n[yellow]再按一次 Ctrl+C 确认退出[/yellow]")
                else:
                    self.running = False
                    self.console.print("\n[bold yellow]再见！[/bold yellow]")
            except EOFError:
                self.running = False
                self.console.print("\n[bold yellow]再见！[/bold yellow]")


def run_repl() -> None:
    """Run REPL interface."""
    repl = ClaudeCodeStyleREPL()
    repl.run()
