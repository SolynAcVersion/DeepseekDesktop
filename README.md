# DeepseekDesktop

## 使用说明
使用 uv 启动 `main.py` (cpy=3.10.0) ， 根据操作进行

程序读取 Deepseek API KEY 时通过 手动输入 、 读取系统环境变量 `DEEPSEEK_API_KEY` 两种方式


## 目前功能
- 可调用线上 MCP Server，如 `MCP.so` 仓库上的服务器，只用改 `tools\mcp_config.json` 中的内容，这里默认是 `mcp-server-time` 。
- 允许输入本地MCP脚本文件，如操作文件、网络爬虫，这里提供了简单的操作文件实例工具 `tools\file.py` 和 `tools\network.py` 用来简单的agent功能。
- 允许在启动时输入自定义 System Prompt 系统提示词。
- 允许启动时自定义 Temperature 温度值。
- 较大操作链实施时，在有循环深度限制下，根据前一步的报错改正重试。最大操作循环深度，由 `MAX_ITER` 决定。


## 下一步计划
- 多内置一些好用的本地 MCP 之类 Function Calling 包，让 “Agent” 开箱即用
- 支持多 MCP Server 链接服务
- 增加本地历史储存功能
- 零 AI 基础人群友好的 GUI 界面
- 优化 token 使用
- i18n
- 不仅支持 DeepSeek，兼容各类 AI API 接口

## Ad (
若对深度学习有兴趣，想要接触了解一下，欢迎来看 [我的博客](https://www.cnblogs.com/yldeveloper) ，共同学习呀~


