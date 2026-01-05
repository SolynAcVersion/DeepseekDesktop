import os 
import sys
import importlib.util
from openai import OpenAI
import json
from mcp_utils import MCPServerManager, load_mcp_conf, exec_mcp_tools


def load_mcp_mod(mcp_path):
    try:
        if mcp_path.endswith('.json'):
            mcp_manager = MCPServerManager()
            tool_names = load_mcp_conf(mcp_path, mcp_manager)
            if not tool_names:
                return None, {}
            funcs = {}
            for ser_name in mcp_manager.servers.keys():
                for tool in mcp_manager.tools.get(ser_name, []):
                    tool_name = tool.get('name', '')
                    if tool_name:
                        func_name = f"mcp_{ser_name}_{tool_name}"
                        def make_tool_func(name_ser, name_tool, desc):
                            def tool_func(**kwargs):
                                res = mcp_manager.call_tool(name_ser, name_tool, kwargs)
                                return json.dumps(res, ensure_ascii=False, indent=2)
                            tool_func.__name__ = name_tool
                            tool_func.__doc__ = tool.get('description', desc)
                            return tool_func
                        
                        funcs[func_name] = make_tool_func(ser_name, tool_name, tool.get('description', '无描述'))
            class MCPModule:
                def __init__(self):
                    self.manager = mcp_manager
            return MCPModule(), funcs             
                    
        else:
            module_name = os.path.basename(mcp_path).replace('.py', '')
            spec = importlib.util.spec_from_file_location(module_name, mcp_path)
            if spec is None:
                raise ImportError(f"[Warning] 无法从 {mcp_path} 加载模块")
            mcp_module = importlib.util.module_from_spec(spec)
            sys.modules[module_name] = mcp_module
            spec.loader.exec_module(mcp_module)
            print(f"[Info] 加载 {module_name} 成功")
            funcs = {}
            for attr_name in dir(mcp_module):
                attr = getattr(mcp_module, attr_name)
                if callable(attr) and not attr_name.startswith('_'):
                    funcs[attr_name] = attr
            return mcp_module, funcs
        
    except Exception as e:
        print(f"[Warning] 加载失败：{e}")
        return None, {}


def load_mult_mcp_mod(mcp_paths):
    all_funcs = {}
    all_mods = []
    
    for path in mcp_paths:
        mod, funcs = load_mcp_mod(path)
        if mod:
            all_mods.append(mod)
        if funcs:
            for func_name, func in funcs.items():
                if func_name in all_funcs:
                    print(f"[Warning] 函数 '{func_name}' 在多个MCP文件中存在，将使用最后加载的版本")
                all_funcs[func_name] = func
    return all_mods, all_funcs

def gen_tools_desc(funcs):
    if not funcs:
        return ""
    desc = "你可以用一下工具来操作文件：\n"
    for func_name, func in funcs.items():
        doc = func.__doc__ or "无描述"
        desc += f"- {func_name}: {doc}\n"
    return desc

def exec_func(funcs, func_name, *args):
    if func_name not in funcs:
        return f"错误：函数 '{func_name}' 不存在"
    try:
        # 对于MCP工具（以mcp_开头），需要关键字参数
        if func_name.startswith('mcp_'):
            kwargs = {}
            for arg in args:
                if '=' in arg:
                    key, value = arg.split('=', 1)
                    kwargs[key.strip()] = value.strip()
                elif arg.strip():
                    kwargs['value'] = arg.strip()
            
            res = funcs[func_name](**kwargs)
        else:
            # 普通函数使用位置参数
            res = funcs[func_name](*args)
        
        return f"执行成功：{res}"
    except Exception as e:
        return f"执行失败：{e}"

def main():
    MCP_PATH = input("MCP文件所在的目录(支持.py或.json)(多个文件用空格隔开):").strip()
    mcp_paths = [p.strip() for p in MCP_PATH.split() if p.strip()]
    
    if not mcp_paths:
        print("[Error] 未输入任何文件路径")
    
    valid_paths = []
    for path in mcp_paths:
        if not os.path.exists(path):
            print(f"[Warning] 文件不存在：{path}")
        else:
            valid_paths.append(path)

    print(f"[Info] 将加载 {len(valid_paths)} 个MCP文件")
    mcp_module, funcs = load_mult_mcp_mod(valid_paths)
    if not funcs:
        print("[Warning] MCP文件有问题，无法识别文件")
    api_key = input("输入 DeepSeek API KEY（或留空使用环境变量 DEEPSEEK_API_KEY ）:").strip()
    if not api_key:
        api_key = os.environ.get("DEEPSEEK_API_KEY")
        if not api_key:
            print("[Error] 环境变量中也未找到 API KEY")
            api_key = input("请手动输入 API_KEY :")
            if not api_key:
                exit()
    print("[Info] 获取 API KEY 成功")
    
    client = OpenAI(
        api_key=api_key,
        base_url='https://api.deepseek.com'
    )
    system_prompt = """
    你是一个AI助手，主要职责是满足用户需求，同时在必要时协助操作电脑。

当用户明确要求执行电脑操作（例如移动文件、复制文件、运行程序等）时，请严格使用以下格式输出指令（仅一行，无其他文本）：

EXECUTE: 命令 ￥| 参数1 ￥| 参数2 ￥| ...
其中 ￥| 两个字符共同组成一个分隔符

例如：
EXECUTE: mv ￥| file1.txt ￥| file2.txt
EXECUTE: cp ￥| source.txt ￥| dest.txt

重要规则：

仅在用户明确要求操作电脑、查询时间等查询联网接口时使用EXECUTE指令，其他所有情况（包括写小说、回答问题、提供建议、创作内容等）都直接输出内容。

如果用户要求创作内容（如小说、文章、代码等），请直接输出内容本身，不要尝试保存或操作文件，除非用户明确要求保存到特定位置。

如果任务需要多步操作，请逐步执行，每次只输出一个EXECUTE指令。

如果操作失败，请在下一步尝试其他可行方案，不要解释原因或描述过程。

严禁说 
"让我尝试使用系统命令来运行Python："
"我需要先查看完整的HTML文件内容。让我重新读取文件"
"我尝试使用Python来解析HTML文件并查找PDF链接"
之类的思路!!!

所有操作完成后，请简要总结结果。

请始终遵循以上规则，确保响应简洁、准确。
    """
    addition_sys_prompt = input("(可选) 预设一下系统提示:")
    if addition_sys_prompt:
        system_prompt += addition_sys_prompt
    
    TEMPERATUREs = input("(可选，默认为 1.0 ) 请设置一下温度值:").strip()

    if not TEMPERATUREs:
        TEMPERATURE = 1.0
    else:
        TEMPERATURE = float(TEMPERATUREs)

    while TEMPERATURE > 1.5 or TEMPERATURE < 0.0:
        print("温度值应在 0.0 到 1.5 之间，请重新输入")
        temp_input = input("请设置温度值: ").strip()
        if not temp_input:
            TEMPERATURE = 1.0
        else:
            TEMPERATURE = float(temp_input)
    tools_desc = gen_tools_desc(funcs)
    if tools_desc:
        system_prompt = tools_desc + '\n' + system_prompt
    
    conv_his = [
        {"role": "system", "content": system_prompt}
    ]
    
    while True:
        try:
            user_inp = input("\n>>").strip()
            if user_inp.lower() in ['exit', 'quit', 'bye', '退出', '再见']:
                print("再见！")
                break
            if not user_inp:
                continue
            
            if user_inp.lower() in ['tool', 'tools', '工具']:
                print("\n可用工具：")
                for i, func_name in enumerate(funcs.keys(), 1):
                    func = func[func_name]
                    doc = func.__doc__ or "无描述"
                    print(f"{i:2}. {func_name}: {doc[:60]}...")
                continue
            
            if user_inp.lower() in ['clear', '清空']:
                conv_his = [{"role": "system", "content": system_prompt}]
                print("对话历史已清空")
                continue
            
            conv_his.append({"role": "user", "content": user_inp})
            
            MAX_ITER = 15
            final_resp = ""
            for step in range(MAX_ITER):
                response = client.chat.completions.create(
                    model="deepseek-chat",
                    temperature=TEMPERATURE,
                    messages=conv_his,
                    stream=False
                )
                get_reply = response.choices[0].message.content
                if get_reply.startswith("EXECUTE:"):
                    print(f"\n[步骤 {step + 1} ][AI 请求执行] {get_reply}")
                    
                    tokens = get_reply.replace("EXECUTE:", "").strip().split("￥|")
                    tokens = [t.strip() for t in tokens]
                    
                    if len(tokens) < 1:
                        res = "错误！你的命令格式不正确"
                    else:
                        func_name = tokens[0]
                        args = tokens[1: ] if len(tokens) > 1 else []
                        res = exec_func(funcs, func_name, *args)
                        
                    print(f"[Info] AI 执行结果：{res}")
                    
                    conv_his.append({"role": "assistant", "content": get_reply})
                    conv_his.append({"role": "user", "content": f"执行结果：{res}\n请根据这个结果决定下一步操作。如果任务完成，请总结告诉我结果。"})
                    
                    # if "错误" in res or "失败" in res:
                    #     print("[Warning] 执行失败，建议手动检查")
                    #     final_resp = f"上一步执行失败：{res}"
                    #     break
                else:
                    final_resp = get_reply
                    conv_his.append({"role": "assistant", "content": get_reply}) 
                    break
            else:
                print(f"[Warning] 已达最大执行步数 {MAX_ITER} ,自动停止")
                final_resp = f"已达到最大执行步数({MAX_ITER})，任务可能未完全完成"
            if final_resp:
                print(f"\n[AI] {final_resp}")
            
        except KeyboardInterrupt:
            print("\n[Error] 中断操作，再见！")
            break
        except Exception as e:
            print(f"\n[Error] 错误：{e}")
            continue

if __name__ == "__main__":
    main()
    