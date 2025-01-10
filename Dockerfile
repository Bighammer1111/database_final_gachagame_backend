# 使用Python官方鏡像作為基礎鏡像
FROM python:3.9

# 設置工作目錄
WORKDIR /app

# 更新软件包列表，并安装git
RUN apt-get update && apt-get install -y git

# 将当前目录下的文件复制到容器中的/app
COPY . /app


# COPY mydatabase.db /data/mydatabase.db

# 克隆yolov5仓库到指定的目录



RUN apt-get update && apt-get install -y libglib2.0-0

RUN apt-get update && apt-get install -y gcc python3-dev

# 更新apt包索引并安装libgl1-mesa-glx
RUN apt-get update && apt-get install -y libgl1-mesa-glx

# 安装依赖
RUN pip install --no-cache-dir -r requirements.txt

# 暴露端口
EXPOSE 6000

# 运行Flask应用
CMD ["python", "run.py"]
