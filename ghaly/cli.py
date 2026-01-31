"""
Command-line interface module for ghaly.

This module provides CLI commands for authentication, project analysis,
and AI-powered recommendations.
"""

import sys
import webbrowser
from typing import Any, Dict, Optional

import click
from rich.console import Console
from rich.table import Table

from ghaly.auth import AuthError, GitHubOAuth, get_github_oauth
from ghaly.config import ConfigError, ConfigManager, get_config
from ghaly.oauth_server import OAuthServerError, start_callback_server
from ghaly.github_api import GitHubClient, GitHubAPIError
from ghaly.analyzer import RepositoryAnalyzer, HealthStatus
from ghaly.ai_client import AIClient, AIError
from ghaly.repl import run_repl


console = Console()


@click.group()
@click.version_option(version="0.1.0", prog_name="ghaly")
@click.pass_context
def cli(ctx: click.Context) -> None:
    """
    Ghaly - GitHub Project Activity Analysis Tool
    
    A command-line tool for analyzing GitHub project health and
    discovering high-quality repositories with AI-powered insights.
    """
    ctx.ensure_object(dict)
    ctx.obj['config'] = get_config()


@cli.group()
def auth() -> None:
    """Authentication commands for GitHub OAuth."""
    pass


@auth.command()
@click.option('--client-id', prompt='GitHub Client ID', help='GitHub OAuth App Client ID')
@click.option('--client-secret', prompt='GitHub Client Secret', hide_input=True, help='GitHub OAuth App Client Secret')
@click.option('--redirect-uri', default='http://localhost:8080/callback', help='OAuth redirect URI')
def configure(client_id: str, client_secret: str, redirect_uri: str) -> None:
    """
    Configure GitHub OAuth credentials.
    
    Set up your GitHub OAuth application credentials for authentication.
    You can create an OAuth app at https://github.com/settings/developers
    """
    config = get_config()
    
    config.set('github.client_id', client_id)
    config.set('github.client_secret', client_secret)
    config.set('github.redirect_uri', redirect_uri)
    
    console.print("[green]✓[/green] GitHub OAuth credentials configured successfully!")
    console.print("\nNext steps:")
    console.print("1. Run [cyan]ghaly auth login[/cyan] to authenticate")
    console.print("2. Or set OPENAI_API_KEY environment variable for AI features")


@auth.command()
def login() -> None:
    """
    Authenticate with GitHub using OAuth.
    
    This will open a browser window where you can authorize ghaly
    to access your GitHub account.
    """
    try:
        oauth = get_github_oauth()
        
        if oauth.is_authenticated():
            console.print("[yellow]You are already authenticated.[/yellow]")
            if click.confirm("Do you want to re-authenticate?"):
                oauth.revoke_token()
            else:
                return
        
        auth_url = oauth.get_authorization_url()
        
        console.print("\n[cyan]GitHub OAuth Authentication[/cyan]")
        console.print("=" * 50)
        console.print("\nOpening browser for authorization...")
        
        with console.status("[cyan]Waiting for authorization...[/cyan]"):
            try:
                webbrowser.open(auth_url)
            except Exception:
                console.print("\n[yellow]Could not open browser automatically.[/yellow]")
                console.print(f"\nPlease visit this URL manually:\n[blue]{auth_url}[/blue]\n")
            
            try:
                code, state = start_callback_server(port=8080, timeout=120)
                
                if not code:
                    console.print("[red]✗[/red] Authentication timed out. Please try again.")
                    sys.exit(1)
                
                token_data = oauth.exchange_code_for_token(code, state)
                
            except OAuthServerError as e:
                console.print(f"[red]Server Error:[/red] {e}")
                console.print("\nFalling back to manual code entry...")
                console.print(f"\nPlease visit: [blue]{auth_url}[/blue]")
                code = click.prompt("\nPaste the authorization code here")
                token_data = oauth.exchange_code_for_token(code)
        
        console.print("[green]✓[/green] Authentication successful!")
        
        user_info = oauth.get_authenticated_user()
        console.print(f"\nWelcome, [cyan]{user_info.get('login', 'User')}[/cyan]!")
        
    except ConfigError as e:
        console.print(f"[red]Configuration Error:[/red] {e}")
        console.print("\nPlease run [cyan]ghaly auth configure[/cyan] first.")
        sys.exit(1)
    except AuthError as e:
        console.print(f"[red]Authentication Error:[/red] {e}")
        sys.exit(1)
    except Exception as e:
        console.print(f"[red]Unexpected Error:[/red] {e}")
        sys.exit(1)


@auth.command()
def status() -> None:
    """
    Check authentication status.
    
    Display current authentication status and user information.
    """
    try:
        oauth = get_github_oauth()
        
        if not oauth.is_authenticated():
            console.print("[yellow]Not authenticated[/yellow]")
            console.print("\nRun [cyan]ghaly auth login[/cyan] to authenticate.")
            return
        
        if oauth.verify_token():
            console.print("[green]✓[/green] Authenticated")
            
            user_info = oauth.get_authenticated_user()
            
            table = Table(title="User Information")
            table.add_column("Field", style="cyan")
            table.add_column("Value", style="green")
            
            table.add_row("Username", user_info.get('login', 'N/A'))
            table.add_row("Name", user_info.get('name', 'N/A'))
            table.add_row("Email", user_info.get('email', 'N/A'))
            table.add_row("Bio", user_info.get('bio', 'N/A'))
            table.add_row("Public Repos", str(user_info.get('public_repos', 0)))
            table.add_row("Followers", str(user_info.get('followers', 0)))
            
            console.print(table)
        else:
            console.print("[red]✗[/red] Token expired or invalid")
            console.print("\nRun [cyan]ghaly auth login[/cyan] to re-authenticate.")
            
    except AuthError as e:
        console.print(f"[red]Error:[/red] {e}")


@auth.command()
def logout() -> None:
    """
    Logout and remove stored credentials.
    
    This will revoke the access token and remove all stored
    authentication data.
    """
    try:
        oauth = get_github_oauth()
        
        if not oauth.is_authenticated():
            console.print("[yellow]Not authenticated[/yellow]")
            return
        
        if click.confirm("Are you sure you want to logout?"):
            oauth.revoke_token()
            console.print("[green]✓[/green] Logged out successfully!")
            
    except AuthError as e:
        console.print(f"[red]Error:[/red] {e}")


@cli.command()
@click.argument('repository', required=False)
@click.option('--owner', '-o', help='Repository owner (username or organization)')
@click.option('--name', '-n', help='Repository name')
@click.option('--days', '-d', default=30, help='Number of days to analyze (default: 30)')
def analyze(repository: Optional[str], owner: Optional[str], name: Optional[str], days: int) -> None:
    """
    Analyze a GitHub repository's activity and health.
    
    REPOSITORY: Full repository path in format 'owner/repo' (e.g., 'facebook/react')
    
    Example:
        ghaly analyze facebook/react
        ghaly analyze --owner facebook --name react
        ghaly analyze facebook/react --days 60
    """
    if not repository and not (owner and name):
        console.print("[red]Error:[/red] Please provide a repository to analyze.")
        console.print("\nUsage:")
        console.print("  ghaly analyze owner/repo")
        console.print("  ghaly analyze --owner owner --name repo")
        sys.exit(1)
    
    try:
        oauth = get_github_oauth()
        
        if not oauth.is_authenticated():
            console.print("[yellow]Not authenticated[/yellow]")
            console.print("\nRun [cyan]ghaly auth login[/cyan] to authenticate.")
            sys.exit(1)
        
        if repository:
            if '/' in repository:
                owner, name = repository.split('/', 1)
            else:
                console.print("[red]Error:[/red] Invalid repository format. Use 'owner/repo'.")
                sys.exit(1)
        
        console.print(f"\n[cyan]Analyzing repository:[/cyan] {owner}/{name}")
        console.print(f"[cyan]Analysis period:[/cyan] Last {days} days\n")
        
        with console.status("[cyan]Fetching repository data...[/cyan]"):
            access_token = oauth.get_access_token()
            config = get_config()
            
            github_client = GitHubClient(
                access_token=access_token,
                api_base_url=config.get('github.api_base_url')
            )
            
            analyzer_config = {
                "activity_days": days,
                "health_thresholds": config.get('analysis.health_thresholds', {
                    "active": 10,
                    "moderate": 5
                })
            }
            
            analyzer = RepositoryAnalyzer(github_client, analyzer_config)
            result = analyzer.analyze_repository(owner, name)
        
        _display_analysis_result(result, days)
        
    except GitHubAPIError as e:
        console.print(f"[red]GitHub API Error:[/red] {e}")
        sys.exit(1)
    except AuthError as e:
        console.print(f"[red]Authentication Error:[/red] {e}")
        console.print("\nRun [cyan]ghaly auth login[/cyan] to re-authenticate.")
        sys.exit(1)
    except Exception as e:
        console.print(f"[red]Error:[/red] {e}")
        sys.exit(1)


def _display_analysis_result(result: Dict[str, Any], days: int) -> None:
    """
    Display repository analysis results in a formatted way.
    
    Args:
        result: Analysis result dictionary
        days: Number of days analyzed
    """
    repo = result["repository"]
    health = result["health"]
    metrics = result["metrics"]
    
    health_colors = {
        "active": "green",
        "moderate": "yellow",
        "inactive": "red"
    }
    health_color = health_colors.get(health["status"], "white")
    
    console.print(f"\n[bold cyan]{repo['full_name']}[/bold cyan]")
    console.print(f"{repo['description'] or 'No description'}\n")
    
    health_table = Table(title="Health Score")
    health_table.add_column("Metric", style="cyan")
    health_table.add_column("Score", justify="right")
    
    health_table.add_row("Overall Health", f"[{health_color}]{health['score']}/100 ({health['status'].upper()})[/{health_color}]")
    health_table.add_row("Commits", f"{health['breakdown']['commits']}/100")
    health_table.add_row("Issues", f"{health['breakdown']['issues']}/100")
    health_table.add_row("Pull Requests", f"{health['breakdown']['pull_requests']}/100")
    health_table.add_row("Contributors", f"{health['breakdown']['contributors']}/100")
    health_table.add_row("Engagement", f"{health['breakdown']['engagement']}/100")
    
    console.print(health_table)
    
    metrics_table = Table(title=f"Activity Metrics (Last {days} Days)")
    metrics_table.add_column("Metric", style="cyan")
    metrics_table.add_column("Value", justify="right")
    
    metrics_table.add_row("Commits", f"{metrics['commit_frequency']['total']} ({metrics['commit_frequency']['per_day']}/day)")
    metrics_table.add_row("Issues", f"{metrics['issue_activity']['total']} ({metrics['issue_activity']['open']} open, {metrics['issue_activity']['closed']} closed)")
    metrics_table.add_row("Issue Close Rate", f"{metrics['issue_activity']['close_rate']}%")
    
    if metrics['issue_activity']['avg_response_time_hours']:
        metrics_table.add_row("Avg Response Time", f"{metrics['issue_activity']['avg_response_time_hours']}h")
    
    metrics_table.add_row("Pull Requests", f"{metrics['pr_activity']['total']} ({metrics['pr_activity']['open']} open, {metrics['pr_activity']['merged']} merged)")
    metrics_table.add_row("PR Merge Rate", f"{metrics['pr_activity']['merge_rate']}%")
    metrics_table.add_row("Contributors", str(metrics['contributor_activity']['total']))
    metrics_table.add_row("Code Velocity", metrics['code_velocity']['velocity'].capitalize())
    metrics_table.add_row("Community Engagement", metrics['community_engagement']['level'].replace('_', ' ').title())
    
    console.print(metrics_table)
    
    info_table = Table(title="Repository Information")
    info_table.add_column("Field", style="cyan")
    info_table.add_column("Value")
    
    info_table.add_row("Language", repo['language'] or 'N/A')
    info_table.add_row("Stars", str(repo['stars']))
    info_table.add_row("Forks", str(repo['forks']))
    info_table.add_row("Contributors", str(result['contributors']))
    
    if repo['created_at']:
        created = repo['created_at'][:10]
        info_table.add_row("Created", created)
    
    if repo['updated_at']:
        updated = repo['updated_at'][:10]
        info_table.add_row("Last Updated", updated)
    
    console.print(info_table)
    
    if result['languages']:
        lang_table = Table(title="Languages")
        lang_table.add_column("Language", style="cyan")
        lang_table.add_column("Usage", justify="right")
        
        total_bytes = sum(result['languages'].values())
        sorted_langs = sorted(result['languages'].items(), key=lambda x: x[1], reverse=True)
        
        for lang, bytes_count in sorted_langs[:5]:
            percentage = round(bytes_count / total_bytes * 100, 1)
            lang_table.add_row(lang, f"{percentage}%")
        
        console.print(lang_table)
    
    if metrics['contributor_activity']['top_contributors']:
        contrib_table = Table(title="Top Contributors")
        contrib_table.add_column("Rank", justify="right", style="cyan")
        contrib_table.add_column("Username")
        contrib_table.add_column("Contributions", justify="right")
        
        for idx, contributor in enumerate(metrics['contributor_activity']['top_contributors'], 1):
            contrib_table.add_row(
                str(idx),
                contributor['login'],
                str(contributor['contributions'])
            )
        
        console.print(contrib_table)


@cli.command()
@click.argument('query')
@click.option('--language', '-l', help='Filter by programming language')
@click.option('--limit', default=10, help='Maximum number of results')
def search(query: str, language: Optional[str], limit: int) -> None:
    """
    Search for GitHub repositories with AI-powered analysis.
    
    QUERY: Search query for repositories
    
    Example:
        ghaly search "machine learning"
        ghaly search "web framework" --language python
    """
    try:
        config = get_config()
        
        api_key = config.get_env('SILICONFLOW_API_KEY')
        if not api_key:
            console.print("[red]Error:[/red] SiliconFlow API key not configured.")
            console.print("\nPlease set SILICONFLOW_API_KEY in your .env file or environment variables.")
            sys.exit(1)
        
        console.print(f"\n[cyan]Searching for:[/cyan] {query}")
        if language:
            console.print(f"[cyan]Language:[/cyan] {language}")
        console.print(f"[cyan]Limit:[/cyan] {limit}")
        
        with console.status("[cyan]Generating AI-powered search queries...[/cyan]"):
            ai_client = AIClient(
                api_key=api_key,
                model="THUDM/glm-4-9b-chat"
            )
            
            recommendations = ai_client.recommend_similar_projects(
                query=query,
                language=language,
                limit=limit
            )
        
        _display_search_results(query, recommendations, language)
        
    except AIError as e:
        console.print(f"[red]AI Error:[/red] {e}")
        sys.exit(1)
    except Exception as e:
        console.print(f"[red]Error:[/red] {e}")
        sys.exit(1)


def _display_search_results(
    query: str,
    recommendations: Dict[str, Any],
    language: Optional[str]
) -> None:
    """
    Display AI-powered search results.
    
    Args:
        query: Original search query
        recommendations: AI recommendations
        language: Programming language filter
    """
    console.print(f"\n[bold cyan]AI-Powered Search Results[/bold cyan]")
    console.print(f"Query: {query}\n")
    
    if recommendations.get("search_queries"):
        queries_table = Table(title="Suggested Search Queries")
        queries_table.add_column("#", style="cyan", justify="right")
        queries_table.add_column("Query")
        
        for idx, q in enumerate(recommendations["search_queries"], 1):
            queries_table.add_row(str(idx), q)
        
        console.print(queries_table)
    
    if recommendations.get("recommendations"):
        rec_table = Table(title="AI Recommendations")
        rec_table.add_column("#", style="cyan", justify="right")
        rec_table.add_column("Query")
        rec_table.add_column("Reason")
        
        for idx, rec in enumerate(recommendations["recommendations"], 1):
            rec_table.add_row(str(idx), rec.get("query", ""), rec.get("reason", ""))
        
        console.print(rec_table)
    
    console.print("\n[yellow]Tip:[/yellow] Use these queries with GitHub search or try:")
    console.print(f"  ghaly analyze <owner>/<repo>")
    console.print(f"  Or visit: https://github.com/search?q={query}")


@cli.command()
def config_show() -> None:
    """
    Show current configuration.
    
    Display all configuration settings (sensitive values are hidden).
    """
    config = get_config()
    
    console.print("\n[cyan]Configuration[/cyan]")
    console.print("=" * 50)
    
    table = Table()
    table.add_column("Key", style="cyan")
    table.add_column("Value", style="green")
    
    github_client_id = config.get('github.client_id')
    table.add_row("github.client_id", github_client_id[:8] + "..." if github_client_id else "Not set")
    table.add_row("github.redirect_uri", config.get('github.redirect_uri', 'Not set'))
    table.add_row("openai.api_key", "Set" if config.get_env('OPENAI_API_KEY') else "Not set")
    table.add_row("Config Directory", str(config.config_dir))
    
    console.print(table)
    
    if config.is_configured():
        console.print("\n[green]✓[/green] Configuration is complete!")
    else:
        console.print("\n[yellow]⚠[/yellow] Configuration incomplete. Run [cyan]ghaly auth configure[/cyan].")


@cli.command()
def config_reset() -> None:
    """
    Reset configuration to default values.
    
    This will reset all configuration settings to their defaults.
    """
    config = get_config()
    
    if click.confirm("Are you sure you want to reset all configuration?"):
        config.reset_config()
        config.clear_all_tokens()
        console.print("[green]✓[/green] Configuration reset successfully!")


@cli.command()
def interactive() -> None:
    """
    Launch interactive REPL mode.
    
    Start a simple text-based interactive interface similar to ChatGPT/Claude,
    supporting natural language conversation and AI-driven interactions.
    
    Example:
        ghaly interactive
    """
    try:
        run_repl()
    except KeyboardInterrupt:
        console.print("\n[yellow]已退出交互模式[/yellow]")
    except Exception as e:
        console.print(f"\n[red]错误:[/red] {str(e)}")


def main() -> None:
    """Main entry point for the CLI."""
    cli()


if __name__ == '__main__':
    main()
