# 番组计划更新推送
[![pdm-managed](https://img.shields.io/badge/pdm-managed-blueviolet)](https://pdm.fming.dev)

## 简介

使用非常简单和及其不规范的语法开发的推送服务，基于PushDeer实现推送

## 依赖

- [PDM](https://github.com/pdm-project/pdm)

## 食用方法

到 [番组计划开发者平台](https://bgm.tv/dev/app) 创建一个应用   
创建一个config.py文件
```python
SERVER_URL = "你服务器的地址/callback" # 例如https://foo.bar/callback
PUSH_KEY = "PushDeer的Push Key"
CLIENT_ID = "APP ID"
CLIENT_SECRET = "APP Secret"
```
在你的命令行里面执行下面的命令吧！
```bash
pdm install
pdm run uvicorn main:app --host 0.0.0.0 --port 8000
```
接下来等待第一次推送的到来吧