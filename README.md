# 小红书用户动态监控

一个基于 Python 的小红书用户动态监控工具，支持实时监控指定用户的笔记更新，并通过企业微信应用消息推送通知。

## 功能特点

- 支持监控指定用户的小红书动态
- 通过企业微信应用消息推送通知
- 使用 SQLite 数据库存储笔记数据
- 自动与新笔记互动（点赞、评论）
- 基于 LLM（需要 OpenAI 兼容的 API 格式）生成评论
- 异常告警机制
- 详细的日志记录系统

## 使用方法

1. 克隆项目
```bash
git clone https://github.com/your-username/xhs-monitor.git
cd xhs-monitor
```

2. 安装依赖
```bash
pip install -r requirements.txt
playwright install chromium  # 安装 Playwright 浏览器
```

3. 配置 config.example.py 文件
```bash
cp config.example.py config.py
```

4. 修改配置文件
打开 `config.py` 并设置以下必要配置：
- `XHS_CONFIG`: 设置小红书 Cookie（必须包含 a1、web_session 和 webId 字段）
- `WECOM_CONFIG`: 设置企业微信应用配置（企业ID、应用ID、Secret）
- `MONITOR_CONFIG`: 设置监控配置
  - `USER_ID`: 要监控的用户ID
  - `CHECK_INTERVAL`: 检查间隔（建议至少5秒）
  - `AUTO_INTERACT`: 是否开启自动互动
- `LLM_CONFIG`: 配置 LLM（如果需要智能评论功能）

5. 运行 monitor.py 文件
```bash
python monitor.py
```

## 配置说明

### XHS_CONFIG
```python
XHS_CONFIG = {
    "COOKIE": "你的小红书Cookie",  # 必需包含 a1、web_session 和 webId 字段
}
```

### MONITOR_CONFIG
```python
MONITOR_CONFIG = {
    "USER_ID": "要监控的用户ID",
    "CHECK_INTERVAL": 5,  # 建议至少5秒以上
    "ERROR_COUNT": 10,  # 连续错误次数阈值
    "AUTO_INTERACT": True,  # 是否开启自动互动
    "LIKE_DELAY": 2,  # 点赞延迟(秒)
    "COMMENT_DELAY": 5,  # 评论延迟(秒)
}
```

## 教程

[追女神必备！使用 Python 构建小红书用户动态监控系统](https://mp.weixin.qq.com/s/2Y2mIPuofTUAdkOsdGmTGA)  

[追女神必备！使用 Python 构建小红书用户动态监控系统（二）- 实现自动点赞和评论功能](https://mp.weixin.qq.com/s/cwIXvP6Fx2gv7l0L2GDs1A)

## 常见问题

1. 签名获取失败
   - 确保已正确安装 Playwright 和 Chromium：`playwright install chromium`
   - 检查 Cookie 是否包含必需字段（a1、web_session、webId）
   - 检查网络连接是否正常

2. 自动互动失败
   - 确保 `AUTO_INTERACT` 设置为 `True`
   - 检查 Cookie 是否有效
   - 适当调整 `LIKE_DELAY` 和 `COMMENT_DELAY` 的值

## 贡献指南

欢迎提交 Issue 和 Pull Request 来帮助改进项目。

## License
MIT License

## 支持

如果你喜欢这个项目，欢迎给它一个 Star ⭐️
或者进行赞助
<br />
<br />
<img src="https://pic.otaku.ren/20240212/AQADPrgxGwoIWFZ-.jpg" style="width: 400px;"/>
<br />
<br />
<a href="https://www.buymeacoffee.com/beilunyang" target="_blank"><img src="https://cdn.buymeacoffee.com/buttons/v2/default-blue.png" alt="Buy Me A Coffee" style="width: 400px;" ></a>
