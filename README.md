# 水墨玄镜

[![Python](https://img.shields.io/badge/Python-3.9+-3776AB?logo=python&logoColor=white)](https://www.python.org/)
[![Flask](https://img.shields.io/badge/Flask-2.3-000000?logo=flask&logoColor=white)](https://flask.palletsprojects.com/)
[![License: MIT](https://img.shields.io/badge/License-MIT-green.svg)](LICENSE)

水墨风传统命理文化展示站。输入出生信息后，可查看八字排盘、称骨批命、周易六爻、八字合婚与当日黄历。界面支持中英切换，以及「八卦星图 / 水墨山水」两套背景。

> 内容仅供文化娱乐与算法学习，请勿用于实际决策。

## 功能

| 模块 | 说明 |
| --- | --- |
| 八字排盘 | 由公历年月日时排出四柱，并给出十神、五行旺弱与地支藏干 |
| 称骨算命 | 按袁天罡称骨法估算年、月、日、时骨重，并配对应批语 |
| 周易六爻 | 以三枚铜钱法起卦，返回本卦、变卦与爻辞 |
| 八字合婚 | 综合生肖合冲、日干五合、日支六合与五行生克给出参考评分 |
| 每日黄历 | 展示当日农历、节气、宜忌与冲煞 |

## 技术栈

- 后端：[Flask](https://flask.palletsprojects.com/) 2.3
- 历法：[lunar-python](https://github.com/6tail/lunar-python)
- 前端：Jinja2 模板 + Tailwind CSS（CDN）+ Font Awesome

## 环境要求

- Python 3.9 或更高版本
- 可访问外网（前端样式与字体通过 CDN 加载）

## 快速开始

```bash
git clone https://github.com/yunsanyuan/ink-mystic-mirror.git
cd ink-mystic-mirror
```

创建虚拟环境并安装依赖：

```bash
# Windows
python -m venv .venv
.venv\Scripts\activate
pip install -r requirements.txt

# macOS / Linux
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

启动开发服务：

```bash
python app.py
```

浏览器打开 [http://127.0.0.1:5000](http://127.0.0.1:5000)。

当前 `app.py` 以 `debug=True`、`host=0.0.0.0` 启动，只适合本机开发。对外部署时请关闭调试模式，并改用 gunicorn / waitress 等 WSGI 服务器。

## 项目结构

```text
.
├── app.py                      # Flask 应用与测算接口
├── requirements.txt            # Python 依赖
├── templates/
│   ├── index.html              # 当前前端页面
│   └── 版本更迭/               # 历史页面与资料
├── LICENSE
├── CONTRIBUTING.md
└── README.md
```

## 接口概览

| 方法 | 路径 | 说明 |
| --- | --- | --- |
| `GET` | `/` | 主页面 |
| `POST` | `/api/bazi` | 八字排盘 |
| `POST` | `/api/chenggu` | 称骨算命 |
| `POST` | `/api/yaogua` | 周易六爻 |
| `POST` | `/api/hehun` | 八字合婚 |
| `GET` | `/api/huangli` | 每日黄历 |

排盘与合婚接口接收 JSON，字段为公历 `year` / `month` / `day` / `hour`。合婚接口需同时提供男方、女方四组时间（`man_*`、`woman_*`）。年份建议范围：`1900–2100`。

## 参与贡献

欢迎提交 Issue 和 Pull Request。开发约定见 [CONTRIBUTING.md](CONTRIBUTING.md)。

## 许可证

本项目使用 [MIT License](LICENSE)。
