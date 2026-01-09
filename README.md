# DeepseekDesktop

## 使用说明
使用 uv 启动 `main.py` (cpy=3.10.0) ， 根据操作进行

程序读取 Deepseek API KEY 时通过 手动输入 、 读取系统环境变量 `DEEPSEEK_API_KEY` 两种方式

读取 MCP 文件时支持 `.py` , `.json` 文件输入，支持多文件输入（不同文件中间用空格分开）。

建议使用局部路径，如

`./tools/files.py ./tools/mcp_config.json`

为能够连接使用 OCR ，请预先启动 `.\tools\addition\Umi-OCR\Umi-OCR.exe` , 并保证主机、端口为 `127.0.0.1` , `1224` （即默认情况）。

## 目前功能
- 可调用线上 MCP Server，如 `MCP.so` 仓库上的服务器，只用改 `tools\mcp_config.json` 中的内容，支持 `npx` , `uvx` ，这里默认是 `howtocook-mcp` 。
- 允许输入本地MCP脚本文件，如操作文件、网络爬虫等，这里提供了简单的操作工具 `tools\files.py` 和 `tools\network.py` 用来简单的agent功能。
- 允许在启动时输入自定义 System Prompt 系统提示词。
- 允许启动时自定义 Temperature 温度值。
- 较大操作链实施时，在有循环深度限制下，根据前一步的报错改正重试。最大操作循环深度，由 `MAX_ITER` 决定。
- 内置 `tools\ocr.py` OCR 工具函数，对图片, PDF 文档进行文字识别。


## 下一步计划
- 零 AI 基础人群友好的 GUI 界面
- 增加本地历史储存功能
- 添加 RAG
- 支持多 MCP Server 链接服务
- 优化 token 使用
- i18n


## 项目架构
- `main.py` 主程序
- `mcp_utils.py` MCP连接实现
- `tools` 包含额外的本地MCP服务 `files.py` , `network.py` , `osmanager.py` , `ocr.py` 以及简单写了连接 `howtocook-mcp` 的配置文件 `mcp_config.json`。


## 鸣谢
- Umi-OCR in https://github.com/hiroi-sora/Umi-OCR


## Ad (
若对深度学习有兴趣，想要接触了解一下，欢迎来看 [我的博客](https://www.cnblogs.com/yldeveloper) ，共同学习呀~


