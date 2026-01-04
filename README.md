# DeepseekDesktop

## 使用说明
使用 uv 启动 `main.py` (cpy=3.10.0) ， 根据操作进行

其中，MCP 文件路径目前仅支持单文件，最好用局部路径输入

程序读取 Deepseek API KEY 时通过 手动输入 、 读取环境变量 `DEEPSEEK_API_KEY` 两种方式

最大操作循环深度，由 `MAX_ITER` 决定

## 目前功能
- 允许输入本地MCP脚本文件，如操作文件、网络爬虫，这里提供了简单的操作文件实例工具 `demomcp.py` 。
- 允许在启动时输入自定义 System Prompt 系统提示词。
- 较大操作链实施时，在有循环深度限制下，根据前一步的报错改正重试。


## 下一步计划
- 增加本地历史储存功能
- 支持 SSE MCP Server
- 支持直接调用使用 `MCP.so` 等在线 MCP Server 仓库
- 零 AI 基础人群友好的 GUI 界面
- 不仅支持 DeepSeek，兼容各类 AI API 接口




