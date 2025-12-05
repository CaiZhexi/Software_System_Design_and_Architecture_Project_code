# K12智慧教育平台

基于LLM的K12教育辅导平台，提供拍照解题、作文批改、智能聊天助手等功能。

## 功能特性

- **🔐 用户系统**: 注册、登录、个人信息管理
- **📸 拍照解题**: 支持图片上传或文字输入，AI智能解答，分步骤解析
- **✍️ 作文批改**: 从结构、语法、词汇多维度评价，给出修改建议
- **💬 聊天助手**: 学习生活问题咨询，支持多轮对话
- **📕 错题本**: 自动收集错题，支持练习和标记掌握
- **📊 学习统计**: 做题数量、正确率、薄弱知识点分析
- **🎯 智能推荐**: 根据薄弱知识点推荐练习题

## 技术栈

- **后端**: Python 3.10 + FastAPI
- **前端**: HTML + CSS + JavaScript (Jinja2模板)
- **数据库**: SQLite + SQLAlchemy
- **AI**: OpenAI API (支持标准接口)

## 快速开始

### 1. 创建虚拟环境

```bash
cd k12_platform
python3.10 -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate
```

### 2. 安装依赖

```bash
pip install -r requirements.txt
```

### 3. 配置环境变量

编辑 `.env` 文件，填入你的API配置：

```env
OPENAI_API_KEY=sk-your-api-key-here
OPENAI_BASE_URL=https://api.openai.com/v1
OPENAI_MODEL=gpt-4o
SECRET_KEY=your-secret-key-change-this
```

### 4. 启动服务

```bash
python main.py
```

或使用uvicorn：

```bash
uvicorn main:app --reload --host 0.0.0.0 --port 8000
```

### 5. 访问应用

打开浏览器访问: http://localhost:8000

## 项目结构

```
k12_platform/
├── main.py              # 主应用入口
├── config.py            # 配置文件
├── requirements.txt     # 依赖列表
├── .env                 # 环境变量（需自行配置）
├── models/
│   └── database.py      # 数据库模型
├── services/
│   ├── llm_service.py   # LLM服务封装
│   └── auth_service.py  # 认证服务
├── templates/           # HTML模板
│   ├── base.html
│   ├── layout.html
│   ├── login.html
│   ├── register.html
│   ├── index.html
│   ├── question.html
│   ├── essay.html
│   ├── chat.html
│   ├── wrong_book.html
│   ├── statistics.html
│   └── profile.html
└── static/
    └── css/
        └── style.css    # 样式文件
```

## API接口

| 接口 | 方法 | 说明 |
|------|------|------|
| `/api/register` | POST | 用户注册 |
| `/api/login` | POST | 用户登录 |
| `/api/logout` | POST | 退出登录 |
| `/api/question` | POST | 提交问题解答 |
| `/api/essay` | POST | 提交作文批改 |
| `/api/chat` | POST | 聊天对话 |
| `/api/wrong-book` | GET | 获取错题本 |
| `/api/wrong-book/add` | POST | 添加到错题本 |
| `/api/statistics` | GET | 获取学习统计 |
| `/api/recommend` | GET | 获取推荐练习 |
| `/api/profile` | GET/POST | 用户信息 |

## 小组成员

- 姚少龙 - 需求文档
- 蔡哲熙 - 后端开发
- 陈星任 - 前端开发
- 李熠 - 测试交付

## License

MIT
