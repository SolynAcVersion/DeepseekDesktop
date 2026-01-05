import subprocess
import json
import time
import threading
import queue
import sys

def test_mcp_simple():
    """简单的MCP服务器测试 - Windows兼容版"""
    print("MCP服务器测试 (Windows兼容版)")
    print("=" * 60)
    
    # 1. 启动服务器
    print("1. 启动MCP时间服务器...")
    proc = subprocess.Popen(
        ['uvx', 'mcp-server-time', '--local-timezone=Asia/Shanghai'],
        stdin=subprocess.PIPE,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True,
        bufsize=1
    )
    
    # 创建队列用于存储服务器输出
    output_queue = queue.Queue()
    stop_event = threading.Event()
    
    def read_output():
        """读取服务器标准输出"""
        while not stop_event.is_set():
            try:
                line = proc.stdout.readline()
                if line:
                    line = line.strip()
                    output_queue.put(("stdout", line))
                else:
                    time.sleep(0.1)
            except:
                break
    
    def read_stderr():
        """读取服务器标准错误"""
        while not stop_event.is_set():
            try:
                line = proc.stderr.readline()
                if line:
                    line = line.strip()
                    output_queue.put(("stderr", line))
                else:
                    time.sleep(0.1)
            except:
                break
    
    # 启动读取线程
    stdout_thread = threading.Thread(target=read_output, daemon=True)
    stderr_thread = threading.Thread(target=read_stderr, daemon=True)
    stdout_thread.start()
    stderr_thread.start()
    
    # 等待服务器启动
    print("等待服务器启动...")
    time.sleep(2)
    
    def get_response(timeout=3):
        """从队列获取响应"""
        responses = []
        start_time = time.time()
        
        while time.time() - start_time < timeout:
            try:
                source, line = output_queue.get(timeout=0.1)
                if source == "stdout" and line:
                    responses.append(line)
            except queue.Empty:
                continue
        
        # 返回最后一个有效的JSON响应
        for line in reversed(responses):
            if line and line.startswith('{'):
                try:
                    return json.loads(line)
                except:
                    pass
        return None
    
    def send_and_wait(request, is_notification=False):
        """发送请求并等待响应"""
        request_json = json.dumps(request)
        print(f"\n发送: {request_json}")
        
        # 发送请求
        proc.stdin.write(request_json + '\n')
        proc.stdin.flush()
        
        # 如果是通知，不等待响应
        if is_notification:
            print("(这是通知，不等待响应)")
            return None
        
        # 如果是请求，等待响应
        print("等待响应...")
        response = get_response(timeout=3)
        
        if response:
            print(f"收到响应: {json.dumps(response, indent=2)}")
        else:
            print("未收到响应")
        
        return response
    
    try:
        # 2. 发送初始化请求
        print("\n2. 发送初始化请求...")
        init_request = {
            "jsonrpc": "2.0",
            "id": 1,
            "method": "initialize",
            "params": {
                "protocolVersion": "2024-11-05",
                "clientInfo": {
                    "name": "mcp-test-client",
                    "version": "1.0.0"
                },
                "capabilities": {}
            }
        }
        
        init_response = send_and_wait(init_request, is_notification=False)
        
        if init_response and 'result' in init_response:
            print("✅ 初始化成功!")
            
            # 3. 发送initialized通知
            print("\n3. 发送initialized通知...")
            init_notification = {
                "jsonrpc": "2.0",
                "method": "notifications/initialized",
                "params": {}
            }
            send_and_wait(init_notification, is_notification=True)
            
            # 等待一下，让服务器处理通知
            time.sleep(0.5)
            
            # 4. 获取工具列表
            print("\n4. 获取工具列表...")
            tools_request = {
                "jsonrpc": "2.0",
                "id": 2,
                "method": "tools/list",
                "params": {}
            }
            
            tools_response = send_and_wait(tools_request, is_notification=False)
            
            if tools_response and 'result' in tools_response:
                tools = tools_response['result'].get('tools', [])
                print(f"✅ 获取到 {len(tools)} 个工具:")
                for tool in tools:
                    print(f"  - {tool['name']}: {tool.get('description', '无描述')}")
                
                # 5. 测试工具调用
                if tools:
                    print("\n5. 测试工具调用...")
                    tool_call_request = {
                        "jsonrpc": "2.0",
                        "id": 3,
                        "method": "tools/call",
                        "params": {
                            "name": "get_current_time",
                            "arguments": {
                                "timezone": "Asia/Shanghai"
                            }
                        }
                    }
                    
                    tool_response = send_and_wait(tool_call_request, is_notification=False)
                    if tool_response and 'result' in tool_response:
                        print(f"✅ 工具调用成功!")
                        result = tool_response['result']
                        if 'content' in result:
                            for content in result['content']:
                                if content.get('type') == 'text':
                                    print(f"结果: {content.get('text', '')}")
                        else:
                            print(f"结果: {json.dumps(result, indent=2)}")
                    else:
                        print("❌ 工具调用失败")
            else:
                print("❌ 获取工具列表失败")
        else:
            print("❌ 初始化失败")
            
    except KeyboardInterrupt:
        print("\n用户中断测试")
    except Exception as e:
        print(f"\n测试出错: {e}")
        import traceback
        traceback.print_exc()
    finally:
        # 清理
        print("\n6. 清理进程...")
        stop_event.set()
        time.sleep(0.5)
        
        # 确保所有读取线程停止
        stdout_thread.join(timeout=1)
        stderr_thread.join(timeout=1)
        
        # 终止进程
        proc.terminate()
        try:
            proc.wait(timeout=5)
            print("✅ 进程已终止")
        except:
            proc.kill()
            print("⚠️  进程被强制终止")
    
    print("\n测试完成")

if __name__ == "__main__":
    test_mcp_simple()