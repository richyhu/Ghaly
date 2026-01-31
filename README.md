# Ghaly - GitHub Project Activity Analysis Tool / GitHub 项目活跃度分析工具

A powerful command-line tool for analyzing GitHub project health, discovering high-quality repositories, and getting AI-powered recommendations.

一个强大的命令行工具，用于分析 GitHub 项目健康度、发现高质量仓库，并获得 AI 驱动的推荐。

---

## Features / 功能特性

- 🔐 **OAuth Authentication / OAuth 认证**: Secure GitHub OAuth 2.0 authentication with automatic callback handling / 安全的 GitHub OAuth 2.0 认证，自动处理回调
- 📊 **Project Analysis / 项目分析**: Comprehensive repository activity and health metrics / 全面的仓库活动和健康度指标
- 🤖 **AI-Powered Insights / AI 智能分析**: Intelligent analysis using SiliconFlow GLM-4-9B-chat model / 使用 SiliconFlow GLM-4-9B-chat 模型进行智能分析
- 🔍 **Smart Search / 智能搜索**: Find similar projects with AI-powered recommendations / 使用 AI 推荐查找相似项目
- 🎨 **Beautiful CLI / 美观 CLI**: Rich, colorful command-line interface with tables / 丰富的彩色命令行界面，带表格显示
- 💬 **Interactive REPL / 交互式 REPL**: Simple text-based interface with natural language support (similar to ChatGPT/Claude) / 简单的文本界面，支持自然语言（类似 ChatGPT/Claude）

---

## Installation / 安装

### From PyPI (coming soon / 即将推出)

```bash
pip install ghaly
```

### From Source / 从源码安装

```bash
git clone https://github.com/ghaly/ghaly.git
cd ghaly
pip install -e .
```

### Development Installation / 开发环境安装

```bash
git clone https://github.com/ghaly/ghaly.git
cd ghaly
pip install -e ".[dev]"
```

---

## Quick Start / 快速开始

### 1. Configure GitHub OAuth / 配置 GitHub OAuth

First, create a GitHub OAuth App:
首先，创建一个 GitHub OAuth 应用：

1. Go to https://github.com/settings/developers / 访问 https://github.com/settings/developers
2. Click "New OAuth App" / 点击 "New OAuth App"
3. Fill in the details / 填写详细信息：
   - Application name: `ghaly`
   - Homepage URL: `http://localhost:8080`
   - Authorization callback URL: `http://localhost:8080/callback`
4. Copy the Client ID and Client Secret / 复制 Client ID 和 Client Secret

Then configure ghaly:
然后配置 ghaly：

```bash
ghaly auth configure
```

Or use environment variables:
或使用环境变量：

```bash
export GITHUB_CLIENT_ID=your_client_id
export GITHUB_CLIENT_SECRET=your_client_secret
export SILICONFLOW_API_KEY=your_siliconflow_api_key
```

### 2. Authenticate / 认证

```bash
ghaly auth login
```

This will automatically open a browser window where you can authorize ghaly.
这将自动打开浏览器窗口，你可以在其中授权 ghaly。

### 3. Check Status / 检查状态

```bash
ghaly auth status
```

### 4. Analyze a Repository / 分析仓库

```bash
ghaly analyze facebook/react
```

### 5. Search for Projects / 搜索项目

```bash
ghaly search "machine learning" --language python
```

### 6. Interactive Mode (Recommended) / 交互模式（推荐）

```bash
ghaly interactive
```

This launches a simple text-based interactive interface similar to ChatGPT/Claude, where you can:
这将启动一个类似 ChatGPT/Claude 的简单文本交互界面，你可以：

- Chat with natural language (支持中文) / 使用自然语言聊天（支持中文）
- Get AI-powered recommendations / 获取 AI 驱动的推荐
- Analyze repositories without memorizing commands / 无需记忆命令即可分析仓库
- Enjoy a clean, intuitive interface / 享受简洁直观的界面

**Examples in Interactive Mode / 交互模式示例：**
- "分析 facebook/react 仓库" / "Analyze facebook/react repository"
- "搜索 Python 机器学习项目" / "Search Python machine learning projects"
- "查看我的认证状态" / "Check my authentication status"
- "配置 OAuth" / "Configure OAuth"

**Commands / 命令：**
- `quit` or `exit` - 退出 / Exit
- `help` - 显示帮助 / Show help
- `clear` - 清空屏幕 / Clear screen
- `status` - 查看认证状态 / Check authentication status

---

## Usage Examples / 使用示例

### Analyze Repository Health / 分析仓库健康度

```bash
# Analyze a repository (default: last 30 days)
# 分析仓库（默认：最近 30 天）
ghaly analyze python/cpython

# Analyze with custom time period
# 使用自定义时间周期分析
ghaly analyze facebook/react --days 7

# Analyze using owner and name parameters
# 使用 owner 和 name 参数分析
ghaly analyze --owner microsoft --name vscode
```

### Search with AI / 使用 AI 搜索

```bash
# Basic search
# 基本搜索
ghaly search "web framework"

# Search with language filter
# 使用语言过滤器搜索
ghaly search "machine learning" --language python

# Limit results
# 限制结果数量
ghaly search "data visualization" --limit 20
```

### Authentication Workflow / 认证流程

```bash
# First time setup
# 首次设置
ghaly auth configure
ghaly auth login

# Check if authenticated
# 检查是否已认证
ghaly auth status

# Logout when done
# 完成后退出
ghaly auth logout
```

---

## Commands / 命令

### Authentication / 认证

```bash
ghaly auth configure    # Configure GitHub OAuth credentials / 配置 GitHub OAuth 凭证
ghaly auth login        # Authenticate with GitHub (auto-opens browser) / 使用 GitHub 认证（自动打开浏览器）
ghaly auth status       # Check authentication status / 检查认证状态
ghaly auth logout       # Logout and remove credentials / 退出并删除凭证
```

### Analysis / 分析

```bash
ghaly analyze <repo>    # Analyze a repository / 分析仓库
ghaly analyze <repo> --days N       # Analyze with custom time period / 使用自定义时间周期分析
```

### Search / 搜索

```bash
ghaly search <query>    # Search for repositories with AI / 使用 AI 搜索仓库
ghaly search <query> --language <lang>     # Filter by language / 按语言过滤
ghaly search <query> --limit <n>  # Limit results / 限制结果数量
```

### Configuration / 配置

```bash
ghaly config-show       # Show current configuration / 显示当前配置
ghaly config-reset      # Reset configuration to defaults / 重置配置为默认值
```

### Interactive Mode / 交互模式

```bash
ghaly interactive       # Launch interactive REPL mode / 启动交互式 REPL 模式
```

### Help / 帮助

```bash
ghaly --help            # Show help / 显示帮助
ghaly <command> --help  # Show command-specific help / 显示特定命令的帮助
```

---

## Configuration / 配置

Ghaly stores configuration in `~/.ghaly/` or `.ghaly/` (project directory):
Ghaly 将配置存储在 `~/.ghaly/` 或 `.ghaly/`（项目目录）中：

- `config.json`: Main configuration file / 主配置文件
- `tokens.json`: OAuth tokens (secure, permissions: 600) / OAuth 令牌（安全，权限：600）
- `.env`: Environment variables / 环境变量

You can also use environment variables:
你也可以使用环境变量：

- `GITHUB_CLIENT_ID`: GitHub OAuth Client ID / GitHub OAuth 客户端 ID
- `GITHUB_CLIENT_SECRET`: GitHub OAuth Client Secret / GitHub OAuth 客户端密钥
- `SILICONFLOW_API_KEY`: SiliconFlow API key for AI features / SiliconFlow API 密钥，用于 AI 功能

---

## Development / 开发

### Project Structure / 项目结构

```
ghaly/
├── ghaly/
│   ├── __init__.py
│   ├── __main__.py
│   ├── cli.py          # CLI commands / CLI 命令
│   ├── auth.py         # OAuth authentication / OAuth 认证
│   ├── config.py       # Configuration management / 配置管理
│   ├── oauth_server.py # OAuth callback server / OAuth 回调服务器
│   ├── github_api.py   # GitHub API client / GitHub API 客户端
│   ├── analyzer.py     # Repository analyzer / 仓库分析器
│   ├── ai_client.py    # AI client / AI 客户端
│   ├── repl.py         # Interactive REPL interface / 交互式 REPL 界面
│   └── tests/          # Test files / 测试文件
├── pyproject.toml      # Project configuration / 项目配置
├── .env.example        # Example environment variables / 环境变量示例
├── .gitignore
├── LICENSE
└── README.md
```

### Running Tests / 运行测试

```bash
pytest
```

### Code Quality / 代码质量

```bash
black ghaly/
isort ghaly/
flake8 ghaly/
mypy ghaly/
```

---

## Analysis Metrics / 分析指标

Ghaly calculates the following metrics:
Ghaly 计算以下指标：

### Health Score (0-100) / 健康度评分 (0-100)
- **Commits / 提交**: Frequency and consistency of commits / 提交的频率和一致性
- **Issues / 问题**: Issue activity and close rate / 问题活动和关闭率
- **Pull Requests / 拉取请求**: PR activity and merge rate / PR 活动和合并率
- **Contributors / 贡献者**: Number of active contributors / 活跃贡献者数量
- **Engagement / 参与度**: Stars, forks, and community activity / 星标、分支和社区活动

### Health Status / 健康状态
- **ACTIVE** (70-100): Highly active and healthy / 高度活跃和健康
- **MODERATE** (40-69): Moderately active / 中度活跃
- **INACTIVE** (0-39): Low activity / 低活跃度

### Activity Metrics / 活动指标
- **Commit Frequency / 提交频率**: Commits per day/week/month / 每天/周/月的提交数
- **Issue Activity / 问题活动**: Total, open, closed, close rate / 总数、打开、关闭、关闭率
- **PR Activity / PR 活动**: Total, open, merged, merge rate / 总数、打开、合并、合并率
- **Contributors / 贡献者**: Total number and top contributors / 总数和顶级贡献者
- **Code Velocity / 代码速度**: High/Medium/Low based on commit rate / 基于提交率的高/中/低
- **Community Engagement / 社区参与度**: Very High/High/Moderate/Low/Very Low / 很高/高/中等/低/很低

---

## Roadmap / 路线图

- [x] Phase 1: Environment Setup + OAuth Authentication / 阶段 1：环境设置 + OAuth 认证
- [x] Phase 2: Core Function Development / 阶段 2：核心功能开发
- [x] Phase 3: AI Function Implementation / 阶段 3：AI 功能实现
- [x] Phase 4: Testing and Optimization / 阶段 4：测试和优化
- [x] Phase 5: Interactive TUI Interface / 阶段 5：交互式 TUI 界面
- [ ] Phase 6: Performance Optimization (planned) / 阶段 6：性能优化（计划中）
- [ ] Phase 7: PyPI Release (planned) / 阶段 7：PyPI 发布（计划中）

---

## Contributing / 贡献

Contributions are welcome! Please feel free to submit a Pull Request.
欢迎贡献！请随时提交 Pull Request。

### Development Setup / 开发设置

```bash
# Fork and clone
# Fork 并克隆
git clone https://github.com/your-username/ghaly.git
cd ghaly

# Create virtual environment
# 创建虚拟环境
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate / Windows: venv\Scripts\activate

# Install dependencies
# 安装依赖
pip install -e ".[dev]"

# Run tests
# 运行测试
pytest

# Run with coverage
# 运行并生成覆盖率报告
pytest --cov=ghaly --cov-report=html
```

### Code Style / 代码风格

We use:
我们使用：

- **Black** for code formatting / 用于代码格式化
- **isort** for import sorting / 用于导入排序
- **flake8** for linting / 用于代码检查
- **mypy** for type checking / 用于类型检查

Please ensure your code passes all checks before submitting.
请确保你的代码在提交前通过所有检查。

---

## License / 许可证

MIT License - see LICENSE file for details
MIT 许可证 - 详见 LICENSE 文件

---

## Support / 支持

For issues and questions, please open an issue on GitHub.
如有问题和疑问，请在 GitHub 上提交 issue。

---

## Acknowledgments / 致谢

- Built with [Click](https://click.palletsprojects.com/) / 使用 [Click](https://click.palletsprojects.com/) 构建
- Uses [Authlib](https://authlib.org/) for OAuth / 使用 [Authlib](https://authlib.org/) 进行 OAuth
- Powered by [SiliconFlow](https://siliconflow.cn/) for AI features / 由 [SiliconFlow](https://siliconflow.cn/) 提供 AI 功能支持
- Beautiful output with [Rich](https://rich.readthedocs.io/) / 使用 [Rich](https://rich.readthedocs.io/) 实现美观输出
- GitHub API integration with [Requests](https://requests.readthedocs.io/) / 使用 [Requests](https://requests.readthedocs.io/) 集成 GitHub API
