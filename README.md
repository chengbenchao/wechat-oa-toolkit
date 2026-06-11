# WeChat OA Toolkit 📱

> 微信公众号文章一键发布工具包 —— 从内容创作到草稿箱推送的完整方案

一套完整的微信公众号运营工具包，包含 Python SDK、排版模板和踩坑攻略。帮你把"写文章 → 排版 → 上传封面 → 推送草稿箱"的整个流程自动化。

## ✨ 特性

- 🐍 **Python SDK** —— 纯 Python 实现，零外部依赖，一行命令发布文章
- 🎨 **卡片式排版模板** —— 精心设计的 inline CSS 模板，直接套用
- 📖 **完整攻略** —— 从零配置到成功推送，所有踩过的坑都记录在案
- 🤖 **去AI味指南** —— 让 AI 生成的内容读起来像人写的
- 🔒 **安全设计** —— 敏感信息走环境变量，不入代码仓库

## 🚀 快速开始

### 1. 安装

```bash
git clone https://github.com/YOUR_USERNAME/wechat-oa-toolkit.git
cd wechat-oa-toolkit
```

无需 pip install，`wechat_oa_toolkit.py` 是纯标准库实现，直接用。

### 2. 配置环境变量

```bash
# 复制模板
cp .env.example .env

# 编辑填入你的公众号凭证
# WECHAT_APPID=你的AppID
# WECHAT_SECRET=你的AppSecret

# 或者直接 export（推荐）
export WECHAT_APPID="wx你的AppID"
export WECHAT_SECRET="你的AppSecret"
```

### 3. 添加 IP 白名单

⚠️ **这一步不做，API 调不通！**

1. 登录 [微信公众平台](https://mp.weixin.qq.com)
2. 进入「设置与开发」→「基本配置」
3. 找到「IP白名单」→ 点击「修改」
4. 添加你服务器的公网 IP

**查看当前 IP：**

```bash
curl -s https://httpbin.org/ip | python3 -c "import sys,json; print(json.load(sys.stdin)['origin'])"
```

### 4. 发布文章

```bash
# 一键发布（封面图 + 创建草稿）
python3 wechat_oa_toolkit.py \
  --title "文章标题" \
  --digest "文章摘要" \
  --author "作者名" \
  --content-file article.html \
  --cover-image cover.png

# 仅获取 access_token（调试用）
python3 wechat_oa_toolkit.py --token-only
```

### 5. 在 Python 中调用

```python
from wechat_oa_toolkit import WeChatOAToolkit

tk = WeChatOAToolkit()

# 读取文章 HTML
with open("article.html", "r", encoding="utf-8") as f:
    content = f.read()

# 一键发布
tk.publish_article(
    title="伊朗封锁霍尔木兹海峡，油价破95美元",
    content=content,
    cover_image_path="cover.png",
    digest="布伦特原油突破95美元创年内新高",
    author="你的名字",
)
```

## 📐 排版模板

`templates/card-style.html` 提供了一套**卡片式排版模板**，包含以下组件：

| 组件 | 用途 | 视觉效果 |
|------|------|----------|
| 🔴 开头声明框 | 重大事件、重要通知 | 红色左边框 + 浅红底 |
| ⬜ 时间线框 | 事件回顾、发展脉络 | 圆角灰框 + 细边框 |
| 📊 数据速览框 | 关键数据展示 | 渐变背景 + 红色标题 |
| 🟢 受益板块卡片 | 利好、推荐、正面内容 | 绿色左边框 + 浅绿底 |
| 🟠 承压板块卡片 | 利空、风险、负面内容 | 橙色左边框 + 浅橙底 |
| 🔵 结尾建议框 | 总结、核心观点 | 蓝色左边框 + 蓝底 |
| 📋 观察分析卡片 | 多条并列内容 | 带左边缩进的引用样式 |

**使用方式**：复制 HTML 片段，替换文字内容即可。公众号不支持外链 CSS，所有样式都是 inline style。

## 📖 完整攻略

### 微信公众号 API 调用全流程

```
┌─────────────┐    ┌─────────────┐    ┌─────────────┐    ┌─────────────┐
│  获取 Token  │───>│  上传封面图  │───>│  创建草稿   │───>│  登录后台   │
│  /token      │    │  /material   │    │  /draft/add  │    │  手动发布   │
└─────────────┘    └─────────────┘    └─────────────┘    └─────────────┘
```

#### Step 1: 获取 access_token

```bash
curl -s "https://api.weixin.qq.com/cgi-bin/token?\
grant_type=client_credential&\
appid=YOUR_APPID&\
secret=YOUR_SECRET"
```

返回：
```json
{"access_token": "104_xxx...", "expires_in": 7200}
```

#### Step 2: 上传封面图（永久素材）

```bash
# ⚠️ Windows 上必须用 curl.exe，不能用 bash 的 curl
# ⚠️ 图片路径如果是中文，建议先 cp 到纯英文路径

curl.exe -X POST "https://api.weixin.qq.com/cgi-bin/material/add_material?\
access_token=TOKEN&type=image" \
  -F "media=@/path/to/cover.png"
```

返回：
```json
{"media_id": "Zbz2Yeer_xxx...", "url": "https://mmbiz.qpic.cn/..."}
```

#### Step 3: 创建草稿

```bash
# 推荐用 PowerShell 发送（UTF-8 编码更可靠）
# 或者用 Python SDK
python3 wechat_oa_toolkit.py --title "标题" --content-file article.html --cover-image cover.png
```

### ⚠️ 踩坑记录

| 坑 | 症状 | 解决方案 |
|----|------|----------|
| **IP 白名单** | `errcode: 40164, invalid ip ... not in whitelist` | 去微信公众平台添加当前服务器 IP 到白名单 |
| **中文路径上传失败** | bash 的 curl 读不到中文路径的文件 | `cp` 到纯英文路径，或使用 Windows 原生 `curl.exe` |
| **curl vs curl.exe** | Git Bash 的 curl 上传文件失败 | Windows 上用 `curl.exe` 而不是 `curl` |
| **UTF-8 编码乱码** | 中文标题/摘要变成问号 | PowerShell 用 `[System.Text.Encoding]::UTF8.GetBytes()` 发送 |
| **封面图必填** | `errcode: 40007, invalid media_id` | `thumb_media_id` 是必填字段，必须先上传封面图 |
| **Token 过期** | 之前能用的 token 突然报错 | access_token 有效期 7200 秒，过期需重新获取 |

### 🤖 去 AI 味指南

AI 生成的文章有明显的"机器感"，以下是识别和去除方法：

#### 识别 AI 味的信号

| AI 味特征 | 举例 | 替换方案 |
|-----------|------|----------|
| 过度使用 emoji | ✅📊🔥🔹🔴🔵 | 用排版样式（色块、边框）替代 |
| 空洞的高级词 | "标志性""至关重要""彰显了""体现了" | 直接说事，不拔高 |
| 公式化结尾 | "让我们共同期待…""写在最后" | 口语化收束："最后说几句实在的" |
| 过度加粗 | 每段都有 `<strong>` | 只在真正需要强调时加粗 |
| 第三人称客观 | "值得注意的是""可以看出" | 加入第一人称："我翻了翻数据""说实话" |
| 句式均匀 | 每段长度差不多 | 长短交替，有急促有舒缓 |
| 完美结构 | 完全对称的并列 | 适当打破，有主有次 |

#### 改写前后对比

**AI 味版：**
> 📊 布伦特原油突破95美元/桶，单日涨幅近4%，创年内新高！这标志着全球能源市场进入了一个新的紧张周期，凸显了地缘政治风险对大宗商品价格的深远影响。

**人味版：**
> 布伦特原油在消息出来后直接突破95美元一桶，单日涨了接近4%，创了年内新高。但奇怪的是，涨得没有想象中那么疯。我翻了翻数据，发现了三个缓冲因素。

**核心原则：**
- 加入**个人视角**和**不确定性**（"说实话我不确定""我是有疑虑的"）
- 敢说**反直觉的话**（"按说应该涨才对，结果跌了"）
- 保持**口语节奏**，像跟朋友聊天
- 少用**总结性语句**，多用**具体细节**

## 🛠️ API 参考

### `WeChatOAToolkit`

```python
from wechat_oa_toolkit import WeChatOAToolkit

# 初始化（自动读取环境变量）
tk = WeChatOAToolkit()

# 或手动传入
tk = WeChatOAToolkit(appid="wx...", secret="...")
```

#### 方法

| 方法 | 参数 | 返回值 | 说明 |
|------|------|--------|------|
| `get_access_token()` | 无 | `str` | 获取 access_token |
| `upload_image(image_path)` | 图片路径 | `str` (media_id) | 上传图片到永久素材库 |
| `create_draft(title, content, thumb_media_id, ...)` | 文章信息 | `str` (media_id) | 创建草稿 |
| `publish_article(title, content, cover_image_path, ...)` | 一键发布 | `str` (media_id) | 上传封面+创建草稿 |

### 微信公众号 API 端点

| 端点 | 方法 | 用途 |
|------|------|------|
| `/cgi-bin/token` | GET | 获取 access_token |
| `/cgi-bin/material/add_material` | POST (multipart) | 上传永久素材（封面图） |
| `/cgi-bin/draft/add` | POST (JSON) | 创建草稿 |

## 🔒 安全提示

- **AppSecret 是敏感信息**，永远不要硬编码在代码里或提交到 Git
- 使用 `.env` 文件管理凭证，已加入 `.gitignore`
- 定期在微信公众平台**重置 AppSecret**
- IP 白名单只添加必要的服务器 IP
- access_token 有效期 7200 秒，不要长期存储

## 📋 前置条件

- Python 3.7+（无额外依赖）
- 微信公众号（订阅号/服务号均可）
- 已获取 AppID 和 AppSecret
- 服务器 IP 已加入白名单

## 🤝 配合 WorkBuddy 使用

本工具包最初为 [WorkBuddy](https://workbuddy.ai) AI 助手开发，配合以下 skill 效果更佳：

- **mp-draft-push**：WorkBuddy 内置的公众号推送 skill
- **humanizer**：去 AI 味技能
- **wechat-article-search**：搜索微信公众号文章

但你完全可以独立使用 `wechat_oa_toolkit.py`，不依赖 WorkBuddy。

---

## 🖥️ 另一台机器快速复现（自动安装）

### 方案一：全自动（推荐，需 WorkBuddy）

在新机器上打开 WorkBuddy，对 AI 说：

```
安装 wechat-official-account-expert 专家包，
然后配置环境变量 WECHAT_APPID=xxx 和 WECHAT_SECRET=xxx
```

WorkBuddy 会：
1. 自动安装专家包（含所有 skill）
2. 引导你配置环境变量
3. 提示你添加 IP 白名单

> ⚠️ 如果专家包已发布到推荐市场，可直接用 `/install-skill wechat-official-account-expert` 一键安装。

### 方案二：半自动（专家包已导出）

如果你有专家包的导出文件（`.skill` 格式）：

```bash
# 在 WorkBuddy 中执行
/import-expert /path/to/wechat-official-account-expert.skill
```

导入后重启 WorkBuddy 即可生效。

### 方案三：纯手动（无 WorkBuddy）

```bash
# 1. 克隆仓库
git clone https://github.com/chengbenchao/wechat-oa-toolkit.git
cd wechat-oa-toolkit

# 2. 配置环境变量
cp .env.example .env
# 编辑 .env 填入 WECHAT_APPID 和 WECHAT_SECRET

# 3. 在微信公众平台添加本机 IP 到白名单
# mp.weixin.qq.com → 设置与开发 → 基本配置 → IP白名单

# 4. 直接运行（无需安装任何依赖）
python3 wechat_oa_toolkit.py \
  --title "文章标题" \
  --digest "文章摘要" \
  --content-file article.html \
  --cover-image cover.png
```

---

## 📦 导出专家包（供方案二使用）

在已安装好专家包的机器上，让 WorkBuddy 执行：

```
用 expert-manager 导出 wechat-official-account-expert 专家包
```

导出文件可拷贝到另一台机器导入，实现完全离线安装。

## 📄 License

MIT License - 自由使用、修改和分发

---

⭐ 觉得有用？给个 Star！有问题？开个 Issue！
