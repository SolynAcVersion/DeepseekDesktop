// ==UserScript==
// @name         Cookie 查看与复制工具
// @namespace    http://tampermonkey.net/
// @version      1.0
// @description  显示页面所有Cookie并提供一键复制功能
// @author       yLDeveloper
// @match        *://*/*
// @grant        none
// ==/UserScript==

(function() {
    'use strict';

    // 创建样式
    const style = document.createElement('style');
    style.textContent = `
        #cookie-panel {
            position: fixed;
            bottom: 20px;
            right: 20px;
            width: 500px;
            max-height: 400px;
            background: white;
            border: 2px solid #4CAF50;
            border-radius: 8px;
            box-shadow: 0 4px 15px rgba(0,0,0,0.2);
            z-index: 999999;
            font-family: Arial, sans-serif;
            display: none;
        }

        #cookie-panel.visible {
            display: block;
        }

        .cookie-header {
            background: #4CAF50;
            color: white;
            padding: 12px;
            border-radius: 6px 6px 0 0;
            display: flex;
            justify-content: space-between;
            align-items: center;
            cursor: move;
            user-select: none;
        }

        .cookie-title {
            font-weight: bold;
            font-size: 16px;
        }

        .cookie-count {
            background: white;
            color: #4CAF50;
            padding: 2px 8px;
            border-radius: 10px;
            font-size: 12px;
            font-weight: bold;
        }

        .close-btn {
            background: transparent;
            border: none;
            color: white;
            font-size: 20px;
            cursor: pointer;
            padding: 0 5px;
        }

        .close-btn:hover {
            color: #ffeb3b;
        }

        .cookie-content {
            padding: 15px;
            max-height: 300px;
            overflow-y: auto;
        }

        .cookie-table {
            width: 100%;
            border-collapse: collapse;
            font-size: 12px;
        }

        .cookie-table th {
            background: #f5f5f5;
            padding: 8px;
            text-align: left;
            border-bottom: 2px solid #ddd;
            font-weight: bold;
        }

        .cookie-table td {
            padding: 8px;
            border-bottom: 1px solid #eee;
            vertical-align: top;
            word-break: break-all;
        }

        .cookie-name {
            color: #2196F3;
            font-weight: bold;
        }

        .cookie-value {
            color: #666;
            max-width: 150px;
            overflow: hidden;
            text-overflow: ellipsis;
            white-space: nowrap;
        }

        .copy-btn {
            background: #2196F3;
            color: white;
            border: none;
            padding: 4px 8px;
            border-radius: 4px;
            cursor: pointer;
            font-size: 11px;
            transition: background 0.3s;
        }

        .copy-btn:hover {
            background: #1976D2;
        }

        .copy-btn.copied {
            background: #4CAF50;
        }

        .toggle-btn {
            position: fixed;
            bottom: 20px;
            right: 20px;
            background: #4CAF50;
            color: white;
            border: none;
            padding: 10px 20px;
            border-radius: 20px;
            cursor: pointer;
            font-weight: bold;
            box-shadow: 0 2px 10px rgba(0,0,0,0.2);
            z-index: 999998;
        }

        .toggle-btn:hover {
            background: #45a049;
        }
    `;
    document.head.appendChild(style);

    // 获取所有Cookie
    function getAllCookies() {
        const cookies = document.cookie.split(';');
        const cookieList = [];

        cookies.forEach(cookie => {
            const trimmed = cookie.trim();
            if (trimmed) {
                const eqIndex = trimmed.indexOf('=');
                const name = eqIndex > -1 ? trimmed.substring(0, eqIndex) : trimmed;
                const value = eqIndex > -1 ? trimmed.substring(eqIndex + 1) : '';
                cookieList.push({ name, value });
            }
        });

        return cookieList;
    }

    // 复制到剪贴板
    function copyToClipboard(text) {
        const textarea = document.createElement('textarea');
        textarea.value = text;
        textarea.style.position = 'fixed';
        textarea.style.opacity = '0';
        document.body.appendChild(textarea);
        textarea.select();

        try {
            document.execCommand('copy');
            return true;
        } catch (err) {
            console.error('复制失败:', err);
            return false;
        } finally {
            document.body.removeChild(textarea);
        }
    }

    // 创建界面
    function createCookiePanel() {
        const panel = document.createElement('div');
        panel.id = 'cookie-panel';

        // 面板头部
        const header = document.createElement('div');
        header.className = 'cookie-header';

        const title = document.createElement('div');
        title.className = 'cookie-title';
        title.innerHTML = 'Cookie列表 <span class="cookie-count">0</span>';

        const closeBtn = document.createElement('button');
        closeBtn.className = 'close-btn';
        closeBtn.innerHTML = '×';
        closeBtn.title = '关闭';

        header.appendChild(title);
        header.appendChild(closeBtn);

        // 内容区域
        const content = document.createElement('div');
        content.className = 'cookie-content';

        const table = document.createElement('table');
        table.className = 'cookie-table';
        table.innerHTML = `
            <thead>
                <tr>
                    <th width="30%">名称</th>
                    <th width="50%">值</th>
                    <th width="20%">操作</th>
                </tr>
            </thead>
            <tbody></tbody>
        `;

        content.appendChild(table);
        panel.appendChild(header);
        panel.appendChild(content);

        // 切换按钮
        const toggleBtn = document.createElement('button');
        toggleBtn.className = 'toggle-btn';
        toggleBtn.textContent = '显示Cookie';
        toggleBtn.title = '显示/隐藏Cookie列表';

        // 添加到页面
        document.body.appendChild(panel);
        document.body.appendChild(toggleBtn);

        // 事件监听
        closeBtn.addEventListener('click', () => {
            panel.classList.remove('visible');
        });

        toggleBtn.addEventListener('click', () => {
            if (panel.classList.contains('visible')) {
                panel.classList.remove('visible');
                toggleBtn.textContent = '显示Cookie';
            } else {
                refreshCookieList();
                panel.classList.add('visible');
                toggleBtn.textContent = '隐藏Cookie';
            }
        });

        // 拖动功能
        let isDragging = false;
        let dragOffset = { x: 0, y: 0 };

        header.addEventListener('mousedown', (e) => {
            isDragging = true;
            dragOffset.x = e.clientX - panel.offsetLeft;
            dragOffset.y = e.clientY - panel.offsetTop;
            panel.style.cursor = 'grabbing';
        });

        document.addEventListener('mousemove', (e) => {
            if (!isDragging) return;

            panel.style.left = (e.clientX - dragOffset.x) + 'px';
            panel.style.top = (e.clientY - dragOffset.y) + 'px';
            panel.style.right = 'auto';
            panel.style.bottom = 'auto';
        });

        document.addEventListener('mouseup', () => {
            isDragging = false;
            panel.style.cursor = '';
        });

        return { panel, table, title };
    }

    // 刷新Cookie列表
    function refreshCookieList() {
        const cookies = getAllCookies();
        const tbody = cookieTable.querySelector('tbody');
        const countSpan = cookiePanel.querySelector('.cookie-count');

        // 更新计数
        countSpan.textContent = cookies.length;

        // 清空表格
        tbody.innerHTML = '';

        // 填充表格
        cookies.forEach(cookie => {
            const row = document.createElement('tr');

            const nameCell = document.createElement('td');
            nameCell.className = 'cookie-name';
            nameCell.textContent = cookie.name;

            const valueCell = document.createElement('td');
            valueCell.className = 'cookie-value';
            valueCell.textContent = cookie.value;
            valueCell.title = cookie.value; // 鼠标悬停显示完整值

            const actionCell = document.createElement('td');
            const copyBtn = document.createElement('button');
            copyBtn.className = 'copy-btn';
            copyBtn.textContent = '复制';
            copyBtn.title = `复制 ${cookie.name}=${cookie.value}`;

            copyBtn.addEventListener('click', () => {
                const text = `${cookie.name}=${cookie.value}`;
                if (copyToClipboard(text)) {
                    copyBtn.textContent = '已复制!';
                    copyBtn.classList.add('copied');

                    setTimeout(() => {
                        copyBtn.textContent = '复制';
                        copyBtn.classList.remove('copied');
                    }, 1500);
                }
            });

            actionCell.appendChild(copyBtn);
            row.appendChild(nameCell);
            row.appendChild(valueCell);
            row.appendChild(actionCell);
            tbody.appendChild(row);
        });

        // 如果没有Cookie
        if (cookies.length === 0) {
            const row = document.createElement('tr');
            const cell = document.createElement('td');
            cell.colSpan = 3;
            cell.textContent = '没有找到Cookie';
            cell.style.textAlign = 'center';
            cell.style.color = '#999';
            row.appendChild(cell);
            tbody.appendChild(row);
        }
    }

    // 初始化
    const { panel: cookiePanel, table: cookieTable } = createCookiePanel();

    // 初始刷新一次
    refreshCookieList();

    console.log('Cookie查看器已加载，点击右下角按钮显示列表');

})();