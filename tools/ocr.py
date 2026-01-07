# 改编自 https://github.com/hiroi-sora/Umi-OCR/blob/main/docs/http/api_doc.md#/api/doc

import os
import json
import time
import requests
from urllib.request import urlopen

def ocr_process_pdf(file_path: str, download_dir: str):
    """
    将本地pdf文件识别文本，输出到指定目录并返回文件相对地址
    
    Args:
        file_path: 要上传的pdf 地址，必须是pdf文件！
        
        download_dir: 本地保存目录路径，不包括文件名，只是下载到的目录
        
        如果有“\\”符号，必须使用转义符号！！！
        "C:\\Users\\admin\\Desktop\\new.pdf"是正确的
        
    Returns:
        str: 下载成功的文件保存路径，包括文件名和拓展名，是相对路径。

    Raises:
        Exception: 服务器连接失败
    """
    
    base_url = "http://127.0.0.1:1224"
    try:
        resp = urlopen(base_url)
        code = resp.getcode()
        if code != 200:
            raise Exception(f"no Umi-OCR running or port not correct! run .\\tools\\addition\\Umi-OCR\\Umi-OCR.exe")
    except Exception as e:
        raise Exception(f'访问本地 Umi-OCR 失败: {str(e)}')
    

    url = "{}/api/doc/upload".format(base_url)

    if not file_path.endswith(".pdf"):
        file_path += '.pdf'
    
    # Task parameters
    options_json = json.dumps(
        {
            "doc.extractionMode": "mixed",
        }
    )
    with open(file_path, "rb") as file:
        response = requests.post(url, files={"file": file}, data={"json": options_json})
    response.raise_for_status()
    res_data = json.loads(response.text)
    if res_data["code"] == 101:
        # If code == 101, it indicates that the server did not receive the uploaded file.
        # On some Linux systems, if file_name contains non-ASCII characters, this error might occur.
        # In this case, we can specify a temp_name containing only ASCII characters to construct the upload request.

        file_name = os.path.basename(file_path)
        file_prefix, file_suffix = os.path.splitext(file_name)
        temp_name = "temp" + file_suffix
        with open(file_path, "rb") as file:
            response = requests.post(
                url,
                # use temp_name to construct the upload request
                files={"file": (temp_name, file)},
                data={"json": options_json},
            )
        response.raise_for_status()
        res_data = json.loads(response.text)
    assert res_data["code"] == 100, "Task submission failed: {}".format(res_data)

    id = res_data["data"]

    url = "{}/api/doc/result".format(base_url)

    headers = {"Content-Type": "application/json"}
    data_str = json.dumps(
        {
            "id": id,
            "is_data": True,
            "format": "text",
            "is_unread": True,
        }
    )
    while True:
        time.sleep(1)
        response = requests.post(url, data=data_str, headers=headers)
        response.raise_for_status()
        res_data = json.loads(response.text)
        assert res_data["code"] == 100, "Failed to get task status: {}".format(res_data)


        if res_data["is_done"]:
            state = res_data["state"]
            assert state == "success", "Task execution failed: {}".format(
                res_data["message"]
            )
            break

    url = "{}/api/doc/download".format(base_url)


    download_options = {
        "file_types": [
            "txt",
        ],
        "ignore_blank": False,  # Do not ignore blank pages
    }
    download_options["id"] = id
    data_str = json.dumps(download_options)
    response = requests.post(url, data=data_str, headers=headers)
    response.raise_for_status()
    res_data = json.loads(response.text)
    assert res_data["code"] == 100, "Failed to get download URL: {}".format(res_data)

    url = res_data["data"]
    name = res_data["name"]


    if not os.path.exists(download_dir):
        os.makedirs(download_dir)
    download_path = os.path.join(download_dir, name)
    response = requests.get(url, stream=True)
    response.raise_for_status()
    # Download file size
    downloaded_size = 0
    log_size = 10485760  # Print progress every 10MB

    with open(download_path, "wb") as file:
        for chunk in response.iter_content(chunk_size=8192):
            if chunk:
                file.write(chunk)
                downloaded_size += len(chunk)
                if downloaded_size >= log_size:
                    log_size = downloaded_size + 10485760

    url = "{}/api/doc/clear/{}".format(base_url, id)

    response = requests.get(url)
    response.raise_for_status()
    res_data = json.loads(response.text)
    assert res_data["code"] == 100, "Task cleanup failed: {}".format(res_data)
    return download_path


    