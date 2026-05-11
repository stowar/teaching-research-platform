# teaching-research-platform
虚拟教研社区系统 | FastAPI + 原生 SQL+Streamlit+RAG

# 虚拟教研社区 - 运行说明
> 前后端分离项目：FastAPI 后端 + Streamlit 前端，以下是一键运行的完整步骤。

## 一、环境准备
1.  确保已安装 Python 3.10+（推荐使用 Anaconda 管理虚拟环境）
2.  创建并激活虚拟环境（终端执行）：
    ```bash
    # 创建虚拟环境
    conda create -n teaching-research python=3.10 -y
    # 激活虚拟环境
    conda activate teaching-research
    ```

---

## 二、安装依赖（前后端分离）
项目根目录结构：
```
teaching-research-platform/
├── backend/          # FastAPI 后端服务
└── frontend/         # Streamlit 前端页面
```

### 1. 安装后端依赖
```bash
# 进入后端目录
cd backend
# 安装依赖（清华源加速）
pip install -r requirements.txt -i https://pypi.tuna.tsinghua.edu.cn/simple
```

### 2. 安装前端依赖
```bash
# 进入前端目录
cd ../frontend
# 安装依赖（清华源加速）
pip install -r requirements.txt -i https://pypi.tuna.tsinghua.edu.cn/simple
```

---

## 三、启动项目（需同时打开 2 个终端）
### 终端 1：启动后端服务
```bash
# 进入后端目录
cd ../backend
# 启动 FastAPI 服务
uvicorn main:app --reload --host localhost --port 8000
```
- 后端启动成功提示：`Uvicorn running on http://localhost:8000`
- 后端 API 文档地址：`http://localhost:8000/docs`

### 终端 2：启动前端页面
```bash
# 进入前端目录
cd ../frontend
# 启动 Streamlit 应用
streamlit run app.py
```
- 前端启动成功后，会自动打开浏览器访问 `http://localhost:8501`

---

## 四、常见问题
1.  **依赖安装失败**：执行命令时加上 `-i https://pypi.tuna.tsinghua.edu.cn/simple` 换源加速
2.  **端口被占用**：启动命令中添加 `--port 自定义端口号` 更换端口（如 `uvicorn main:app --port 8001`）
3.  **模块导入错误**：确保已激活正确的虚拟环境，且在项目根目录下执行启动命令

---