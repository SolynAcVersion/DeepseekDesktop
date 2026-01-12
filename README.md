# DeepseekDesktop

## 使用说明

1.UI界面使用（最建议）:

直接启动 release 中的 exe 可执行文件。

操作指南见 release note

或：

使用 uv 启动 `gui.py` (cpy=3.10.0) 

```bash
uv run python ./gui.py
```


为能够连接使用 OCR ，请预先启动 `.\tools\addition\Umi-OCR\Umi-OCR.exe` , 并保证主机、端口为 `127.0.0.1` , `1224` （即默认情况）。


2.命令行使用:

先安装依赖库

```bash
uv sync
```

使用 uv 启动 `aiclass.py` (cpy=3.10.0) 

```bash
uv run python ./aiclass.py
```

若还没有 uv , 请先安装

```bash
pip install uv
```

程序读取 Deepseek API KEY 时通过 手动输入 、 读取系统环境变量 `DEEPSEEK_API_KEY` 两种方式

读取 MCP 文件时支持 `.py` , `.json` 文件输入，支持多文件输入（不同文件中间用空格分开）。

建议使用局部路径，如

`./tools/files.py ./tools/mcp_config.json`


## 目前功能
- 可调用线上 MCP Server，如 `MCP.so` 仓库上的服务器，只用改 `tools\mcp_config.json` 中的内容，支持 `npx` , `uvx` ，这里默认是 `howtocook-mcp` 。注：`tools\mcp_config.json` 中只能添加一个 MCP Server
- 允许输入本地MCP脚本文件，如操作文件、网络爬虫等，这里提供了简单的操作工具 `tools\files.py` 和 `tools\network.py` 等用来简单的agent功能。
- 允许在启动时输入自定义 System Prompt 系统提示词。
- 允许启动时自定义 Temperature 温度值。
- 较大操作链实施时，在有循环深度限制下，根据前一步的报错改正重试。最大操作循环深度，由 `MAX_ITER` 决定。
- 内置 `tools\ocr.py` OCR 工具函数，对图片, PDF 文档进行文字识别。
- 完备的注释系统，方便维护、查阅。



## 正在更新
- 零 AI 基础人群友好的 GUI 界面 #3
- 增加本地历史储存功能 #2
- i18n
- 完备的注释系统，极大可读性可维护性 #2

## 下一步计划
- 添加 RAG
- 支持多 MCP Server 链接服务
- 优化 token 使用



## 项目架构
- `old_console.py` 命令行主程序(停更)
- `aiclass.py` 对原命令行主程序封装得到的类(持续更新)，其中 `main()` 还实现了一个简单的控制台版 AI Agent
- `gui.py` UI界面实现(使用PySide6)
- `mcp_utils.py` MCP连接实现
- `tools` 包含额外的本地MCP服务 `files.py` , `network.py` , `osmanager.py` , `ocr.py` 以及简单写了连接 `howtocook-mcp` 的配置文件 `mcp_config.json`。
- `uv.lock` Python 依赖库


## 鸣谢
- Umi-OCR in https://github.com/hiroi-sora/Umi-OCR
- PySide 界面原型 in https://zhuanlan.zhihu.com/p/1906002163316028282


## Ad (
若对深度学习有兴趣，想要接触了解一下，欢迎来看 [我的博客](https://www.cnblogs.com/yldeveloper) ，共同学习呀~


