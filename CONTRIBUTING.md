# 参与贡献

感谢你愿意改进水墨玄镜。下面是本地开发和提交改动的基本约定。

## 开发环境

1. Fork 本仓库，再克隆到本地。
2. 使用 Python 3.9+ 创建虚拟环境并安装依赖：

```bash
python -m venv .venv
# Windows
.venv\Scripts\activate
# macOS / Linux
source .venv/bin/activate

pip install -r requirements.txt
```

3. 启动开发服务：

```bash
python app.py
```

4. 浏览器打开 `http://127.0.0.1:5000`，确认相关页面和接口可用。

## 分支与提交

- 从 `main` 拉出功能分支，例如 `feat/hehun-copy` 或 `fix/bazi-range`。
- 一次提交只做一件事，说明写清楚「为什么改」，而不是只写「改了什么」。
- 不要提交虚拟环境、缓存、密钥或本机配置。
- 新增依赖时，请同步更新 `requirements.txt`。

## 代码约定

- 源文件使用 UTF-8。
- Python 尽量遵循 [PEP 8](https://peps.python.org/pep-0008/)，4 空格缩进。
- 命理文案保持克制、尊重，避免绝对化判断或歧视性表述。
- 前端改动后，请同时检查中文和英文界面。
- 涉及测算逻辑时，优先补充或核对对应接口的输入输出，而不是只改文案。

## 提交 Pull Request

1. 确认本地可以正常启动，主要功能没有明显回退。
2. 按模板填写改动说明、验证步骤和关联 Issue。
3. 保持 diff 聚焦：不要顺手格式化无关文件。

## 问题反馈

提交 Issue 时请尽量写清：

- 复现步骤
- 期望结果与实际结果
- 操作系统、Python 版本和浏览器

安全相关问题请优先私下联系仓库维护者，不要在公开 Issue 中贴出可被利用的细节。
