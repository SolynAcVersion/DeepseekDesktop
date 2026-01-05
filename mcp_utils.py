import json
import subprocess
import os
import time
import queue
import threading

class MCPServerManager:
    
    def __init__(self):
        self.servers = {}
        self.processes = {}
        self.tools = {}
        self.output_queues = {}  # 存储服务器输出
        self.stop_events = {}    # 停止事件
        self.read_threads = {}   # 读取线程
    
    def parse_config(self, conf_json):
        # 解析MCP配置
        try:
            conf = json.loads(conf_json)
            mcp_servers = conf.get("mcpServers", {})
            
            for ser_name, ser_conf in mcp_servers.items():
                self.servers[ser_name] = {
                    "command": ser_conf["command"],
                    "args": ser_conf.get("args", [])
                }
            return True
        except Exception as e:
            print(f"[Warning] 解析MCP配置出错：{e}")
            return False
        
    def start_ser(self, ser_name):
        if ser_name not in self.servers:
            print(f"[Warning] 未找到服务器 {ser_name}")
            return None
        
        ser_conf = self.servers[ser_name]
        
        try:
            process = subprocess.Popen(
                [ser_conf["command"]] + ser_conf["args"],
                stdin=subprocess.PIPE,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True,
                bufsize=1,
                encoding='utf-8'                
            )
            self.processes[ser_name] = process
            
            # 创建队列和停止事件
            self.output_queues[ser_name] = queue.Queue()
            self.stop_events[ser_name] = threading.Event()
            
            # 启动读取线程
            def read_loop(proc, output_q, stop_flag):
                """读取服务器输出的线程"""
                while not stop_flag.is_set():
                    try:
                        line = proc.stdout.readline()
                        if line:
                            line = line.strip()
                            output_q.put(line)
                        else:
                            time.sleep(0.1)
                    except:
                        break
            
            thread = threading.Thread(
                target=read_loop,
                args=(process, self.output_queues[ser_name], self.stop_events[ser_name]),
                daemon=True
            )
            thread.start()
            self.read_threads[ser_name] = thread
            
            print(f"[Info] 启动 {ser_name} 成功")
            time.sleep(1)  # 给服务器启动时间
            
            return process
        except Exception as e:
            print(f"[Warning] 启动服务器失败: {e}")
            return None
    
    def send_mcp_req(self, ser_name, req, timeout=3):
        # send mcp requests
        if ser_name not in self.processes:
            print(f"[Warning] 服务 {ser_name} 还未运行")
            return None
        process = self.processes[ser_name]
        
        try:
            # send request with ONE newline
            req_json = json.dumps(req)
            process.stdin.write(req_json + '\n')
            process.stdin.flush()
            
            # 如果是通知（没有id字段），不等待响应
            if 'id' not in req:
                return None
            
            # 如果是请求（有id字段），等待响应
            start_time = time.time()
            while time.time() - start_time < timeout:
                try:
                    # 从队列获取响应
                    line = self.output_queues[ser_name].get(timeout=0.1)
                    if line and line.startswith('{'):
                        try:
                            resp = json.loads(line)
                            # 检查ID是否匹配
                            if 'id' in resp and resp['id'] == req['id']:
                                return resp
                        except:
                            pass
                except queue.Empty:
                    continue
            
            print(f"[Warning] 请求超时: {req.get('method', 'unknown')}")
            return None
            
        except Exception as e:
            print(f"[Warning] 发送请求失败：{e}")
            return None
    
    def init_ser(self, ser_name):
        # initialize MCP server
        
        init_req = {
            "jsonrpc": "2.0",
            "id": 1,
            "method": "initialize",
            "params": {
                "protocolVersion": "2024-11-05",  # 固定版本
                "clientInfo": {
                    "name": "mcp-client",
                    "version": "1.0.0"
                },
                "capabilities": {}  # 添加空的能力对象
            }
        }
        
        print(f"[Debug] 发送初始化请求...")
        resp = self.send_mcp_req(ser_name, init_req)
        
        if resp and 'result' in resp:
            print(f"[Debug] 初始化成功")
            
            # 发送initialized通知（这是通知，没有id）
            init_notif = {
                "jsonrpc": "2.0",
                "method": "notifications/initialized",
                "params": {}
            }
            
            print(f"[Debug] 发送initialized通知...")
            # 注意：通知没有响应，所以不要期待返回值
            self.send_mcp_req(ser_name, init_notif)
            
            # 等待一下，让服务器处理通知
            time.sleep(0.5)
            
            # 获取工具列表
            tools_req = {
                "jsonrpc": "2.0",
                "id": 2,
                "method": "tools/list",
                "params": {}
            }
            
            print(f"[Debug] 请求工具列表...")
            tools_resp = self.send_mcp_req(ser_name, tools_req)
            
            if tools_resp and 'result' in tools_resp:
                ser_tools = tools_resp['result'].get('tools', [])
                self.tools[ser_name] = ser_tools
                print(f"[Info] 服务器 {ser_name} 加载了 {len(ser_tools)} 个工具")
                return True
        else:
            print(f"[Debug] 初始化失败: {resp}")
        
        return False
    
    def call_tool(self, ser_name, tool_name, args):
        # call MCP tools
        call_req = {
            "jsonrpc": "2.0",
            "id": 3,
            "method": "tools/call",
            "params": {
                "name": tool_name,
                "arguments": args
            }
        }
        resp = self.send_mcp_req(ser_name, call_req)
        if resp and 'result' in resp:
            return resp['result']
        return {"error": "工具调用失败"}
    
    def stop(self):
        # 停止所有服务器
        for ser_name, process in self.processes.items():
            if process:
                # 设置停止标志
                if ser_name in self.stop_events:
                    self.stop_events[ser_name].set()
                
                # 等待读取线程结束
                if ser_name in self.read_threads:
                    self.read_threads[ser_name].join(timeout=1)
                
                # 终止进程
                process.terminate()
                try:
                    process.wait(timeout=3)
                    print(f"[Info] 停止服务器 '{ser_name}'")
                except:
                    process.kill()
                    print(f"[Warning] 强制停止服务器 '{ser_name}'")


def load_mcp_conf(path, manager):
    # load MCP config files and launch server
    
    try:
        with open(path, 'r') as f:
            conf = f.read()
        
        if manager.parse_config(conf):
            print(f"[Info] 正在加载MCP配置文件 {os.path.basename(path)}")
            
            # 用于存储工具函数
            funcs = {}
            
            for ser_name in manager.servers.keys():
                if manager.start_ser(ser_name):
                    if manager.init_ser(ser_name):
                        # 为每个工具创建函数
                        for tool in manager.tools.get(ser_name, []):
                            tool_name = tool.get('name', '')
                            if tool_name:
                                func_name = f"mcp_{ser_name}_{tool_name}"
                                desc = tool.get('description', '无描述')
                                
                                # 使用闭包捕获当前值
                                def create_tool_func(mgr, s_name, t_name, t_desc):
                                    def tool_func(**kwargs):
                                        res = mgr.call_tool(s_name, t_name, kwargs)
                                        return json.dumps(res, ensure_ascii=False, indent=2)
                                    tool_func.__name__ = t_name
                                    tool_func.__doc__ = t_desc
                                    return tool_func
                                
                                funcs[func_name] = create_tool_func(manager, ser_name, tool_name, desc)
            
            print(f"[Info] 加载了 {len(funcs)} 个MCP工具")
            return funcs
        else:
            return {}
    except Exception as e:
        print(f"[Warning] 加载MCP配置失败：{e}")
        return {}

def exec_mcp_tools(func_name, funcs, args):
    # execute MCP tools
    if func_name not in funcs:
        return f"错误：函数 '{func_name}' 不存在"
    try:
        # 对于MCP工具，参数需要是关键字参数
        if func_name.startswith('mcp_'):
            kwargs = {}
            for arg in args:
                if '=' in arg:
                    key, value = arg.split('=', 1)
                    kwargs[key.strip()] = value.strip()
                elif arg.strip():
                    kwargs['value'] = arg.strip()
            
            # 调用函数
            res = funcs[func_name](**kwargs)
        else:
            # 普通函数使用位置参数
            res = funcs[func_name](*args)
        
        return f"执行成功：{res}"
    except Exception as e:
        return f"执行失败：{e}"