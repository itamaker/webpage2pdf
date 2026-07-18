# webpage2pdf

**像素级还原的网页 → 分页 PDF**，基于无头 Chrome 截图。

[English](README.md) · [许可证: MIT](LICENSE)

`webpage2pdf` 会对网页做一次全长、高分辨率截图——和 Chrome 里看到的一模一样——然后切分成规整的 A4/Letter 页面，并自动加上专业的页眉页脚：

- **页眉**：网页标题 + 抓取日期
- **页脚**：来源 URL + 页码（`3 / 12`）

适合归档文章、留存网页快照证据、把内容分享给不方便打开链接的人，或者搭建个人阅读资料库。

```
┌────────────────────────────────────────────┐
│ Delta Serving 深度解析          2026/07/18 │  ← 页眉：标题 + 日期
├────────────────────────────────────────────┤
│                                            │
│          （页面内容，与 Chrome              │
│            渲染完全一致，                   │
│            Retina 2 倍分辨率）              │
│                                            │
├────────────────────────────────────────────┤
│ https://example.com/blog/delta      3 / 12 │  ← 页脚：URL + 页码
└────────────────────────────────────────────┘
```

## 为什么用截图方案？

大多数 HTML 转 PDF 工具（`wkhtmltopdf`、Chrome 自带的「打印为 PDF」、`weasyprint`）走的是浏览器的**打印**渲染管线。打印 CSS 经常把现代网页排版弄坏：侧边栏塌陷、背景丢失、Web 字体失效、图表错乱。

`webpage2pdf` 直接捕获你在屏幕上**实际看到**的画面（Retina 2 倍分辨率），再对图像本身分页。所见即所得——深色主题、Canvas、图表、自定义字体全都原样保留。

代价是：输出为图像型 PDF，**文字不可选中/搜索**。如果需要可选中的文本，请改用 Chrome 自带的「打印为 PDF」。详见[局限性](#局限性)。

## 特性

- 🖼 **所见即所得** —— 捕获真实页面渲染，而非打印样式表
- 📄 **真正的分页** —— 支持 A4 / Letter / Legal，PDF 物理尺寸精确对应纸张
- 🏷 **自动页眉页脚** —— 每页都有标题、日期、URL 和页码
- 🔍 **Retina 画质** —— 默认 2 倍缩放（可调 1–3 倍）
- 🐢 **懒加载友好** —— 截图前自动滚动全页，确保懒加载图片渲染完成
- 🔐 **支持登录页面** —— `--login` 打开可见浏览器窗口，登录后再导出
- 👤 **会话复用** —— `--user-data-dir` 复用 Chrome 配置目录，免重复登录
- 🈶 **中日韩无乱码** —— 自动回退到苹方 / Noto Sans CJK / 微软雅黑，标题不会变成豆腐块（□□□）
- 🧳 **零驱动配置** —— Selenium ≥ 4.6 自动下载匹配的 chromedriver

## 环境要求

- Python ≥ 3.9
- Google Chrome（任意较新版本）

## 安装

```bash
# 从源码安装
git clone https://github.com/zhaoyangjia/webpage2pdf.git
cd webpage2pdf
pip install .

# 或用 pipx（命令行工具推荐方式）
pipx install .
```

## 快速上手

```bash
# 最简用法：输入 URL，输出 PDF（文件名根据 URL 自动生成）
webpage2pdf https://en.wikipedia.org/wiki/PDF

# 指定输出路径
webpage2pdf https://example.com -o example.pdf

# 需要登录的页面：会弹出浏览器窗口，登录完成后按回车
webpage2pdf https://mysite.com/dashboard --login

# 没装命令行入口？直接运行包
python3 -m webpage2pdf https://example.com
```

## 命令行参数

```
webpage2pdf [选项] URL [输出路径]
```

| 选项 | 默认值 | 说明 |
|---|---|---|
| `URL` | — | 要导出的网页（可省略 `https://`） |
| `OUTPUT` / `-o PATH` | 由 URL 生成 | 输出 PDF 路径 |
| `--login` | 关 | 打开可见浏览器，登录后按回车再导出 |
| `--headed` | 关 | 显示浏览器窗口（部分反爬网站需要） |
| `--wait 秒数` | `3` | 页面加载完成后的额外等待（重 JS 页面可调大） |
| `--no-scroll` | 关 | 跳过截图前的全页滚动（更快，但懒加载图可能缺失） |
| `--width 像素` | `1400` | 浏览器视口宽度 |
| `--scale {1,2,3}` | `2` | 截图缩放倍数（2 = Retina） |
| `--page-size {a4,letter,legal}` | `a4` | 纸张尺寸 |
| `--title 文本` | 网页 `<title>` | 覆盖页眉标题 |
| `--no-header` | 关 | 不绘制页眉 |
| `--no-footer` | 关 | 不绘制页脚 |
| `--chrome-binary 路径` | 自动探测 | Chrome 可执行文件路径 |
| `--user-data-dir 目录` | — | Chrome 用户数据目录（复用已登录会话） |
| `--version` | — | 显示版本号 |

## 常见用法

**加载慢的单页应用**

```bash
webpage2pdf https://app.example.com/report --wait 10
```

**用独立配置目录免去每次登录**

```bash
# 第一次：登录一次，会话保存在配置目录里
webpage2pdf https://mysite.com/dashboard --login --user-data-dir ~/.webpage2pdf-profile

# 之后：无头模式直接导出，已是登录状态
webpage2pdf https://mysite.com/dashboard --user-data-dir ~/.webpage2pdf-profile
```

> 注意：Chrome 不允许多个实例共用同一个用户数据目录——请像上面这样用专门的目录，
> 不要指向你日常浏览器的配置目录。

**Letter 纸张、无页眉页脚的干净页面**

```bash
webpage2pdf https://example.com --page-size letter --no-header --no-footer
```

**窄屏（近似移动端）渲染**

```bash
webpage2pdf https://example.com --width 800
```

## 工作原理

1. **启动** —— Selenium 启动 Chrome（默认无头）；Selenium Manager 自动下载匹配的 chromedriver。
2. **等待** —— 等待 `document.readyState === "complete"` 再加 `--wait` 秒，然后滚动整个页面触发懒加载，最后回到顶部。
3. **截图** —— 通过 Chrome DevTools 协议（`Page.captureScreenshot` + `captureBeyondViewport`）按 4000px 分段截图，再拼接成一张完整长图。
4. **分页** —— 按所选纸张的宽高比切分长图，用 Pillow 绘制页眉页脚。所有排版尺寸随 `--width`/`--scale` 等比缩放，任何分辨率下版式一致。
5. **保存** —— 输出多页 PDF，内嵌 DPI 使每页物理尺寸精确等于 A4/Letter/Legal。

## 疑难排查

**「无法启动 Chrome」**
请先安装 Google Chrome，或显式指定路径：
`webpage2pdf URL --chrome-binary "/Applications/Google Chrome.app/Contents/MacOS/Google Chrome"`

**页面渲染空白或只有一半**
调大 `--wait`（重 JS 页面），或尝试 `--headed`——少数网站对无头浏览器返回空壳页面。

**网站拦截截图 / 出现人机验证**
使用 `--headed`；或用 `--login` 手动通过验证；或用 `--user-data-dir` 指向已有 Cookie 的配置目录。

**中日韩标题显示为方块（□□□）**
内置字体列表已覆盖 macOS（苹方）、Linux（Noto Sans CJK）、Windows（微软雅黑）。精简版 Linux 请安装：`sudo apt install fonts-noto-cjk`。

**无限滚动的信息流导出的 PDF 特别长**
截图前的滚动最多约 200 步就会停止，但类似 Twitter 的信息流仍可能很长。可用 `--no-scroll` 只截取初始加载的内容。

## 局限性

- **文字不可选中、不可搜索** —— 页面被栅格化为图像，这是像素级还原的代价。
- 文件比文本型 PDF 大（2 倍缩放下每页约 0.5–2 MB；可用 `--scale 1` 减小体积）。
- 固定/吸顶元素（悬浮导航栏、Cookie 横幅）可能在每个截图分段中重复出现。
- 分页按固定高度切割，文字行可能恰好被页边切开。

## 参与贡献

欢迎提 Issue 和 PR。路线图上的想法：

- [ ] 智能分页（避免切开文字行）
- [ ] 截图前隐藏指定元素（`--hide "css,selectors"` 去掉 Cookie 横幅）
- [ ] 批量模式：从文件读取 URL 列表，逐个导出
- [ ] 通过 OCR 附加可搜索文本层

开发环境：

```bash
git clone https://github.com/zhaoyangjia/webpage2pdf.git
cd webpage2pdf
pip install -e .
python3 -m webpage2pdf https://example.com -o /tmp/smoke.pdf
```

## 许可证

[MIT](LICENSE) © 2026 Zhaoyang Jia
