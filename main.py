import os 
import sys
import importlib.util
from openai import OpenAI
import json

def load_mcp_mod(mcp_path):
    try:
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
        res = funcs[func_name](*args)
        return f"执行成功：{res}"
    except Exception as e:
        return f"执行失败：{e}"

def main():
    MCP_PATH = input("MCP文件的目录:").strip()
    if not os.path.exists(MCP_PATH):
        print(f"[Warning] 文件不存在！")
        return 
    mcp_module, funcs = load_mcp_mod(MCP_PATH)
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
    system_prompt = """你是一个AI助手，可以帮用户操作电脑文件。
    当你需要执行文件操作时，请使用以下格式：
    
    EXECUTE: 函数名, 参数1, 参数2, ...
    
    只能输出这一行，不能有其他输出，例如：
    
    EXECUTE: mv, file1.txt, file2.txt
    
    或
    
    EXECUTE: cp, source.txt, dest.txt
    
    执行后我会告诉你结果，然后你可以继续对话。
    如果任务需要多步操作，请一步一步来。
    
    如果上一步操作失败，请分析原因并尝试其他方法。
    你不要输出原因，而应该接着在下一个输出使用你认为正确的输出
    如果所有步骤都完成，请总结操作结果。
    """
    addition_sys_prompt = input("(可选) 预设一下系统提示:")
    if addition_sys_prompt:
        system_prompt += addition_sys_prompt
    
    tools_desc = gen_tools_desc(funcs)
    if tools_desc:
        system_prompt = tools_desc + '\n' + system_prompt
    
    conv_his = [
        {"role": "system", "content": system_prompt}
    ]
    
    while True:
        try:
            user_inp = input("\n>>").strip()
            if user_inp.lower() in ['exit', 'quit', 'bye', '退出']:
                print("再见！")
                break
            if not user_inp:
                continue
            conv_his.append({"role": "user", "content": user_inp})
            
            MAX_ITER = 15
            final_resp = ""
            for step in range(MAX_ITER):
                response = client.chat.completions.create(
                    model="deepseek-chat",
                    messages=conv_his,
                    stream=False
                )
                get_reply = response.choices[0].message.content
                if get_reply.startswith("EXECUTE:"):
                    print(f"\n[步骤 {step + 1} ][AI 请求执行] {get_reply}")
                    
                    tokens = get_reply.replace("EXECUTE:", "").strip().split(",")
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
    