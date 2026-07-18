"""Command-line interface for webpage2pdf."""

import argparse
import datetime
import re
import sys
from urllib.parse import urlparse

from . import __version__
from .core import (
    PAGE_SIZES,
    capture_full_page,
    launch_browser,
    log,
    paginate,
    save_pdf,
    trigger_lazy_load,
    wait_for_page,
)


def default_output(url):
    """Derive a filesystem-friendly filename from the URL."""
    parsed = urlparse(url)
    slug = parsed.netloc.replace(".", "-")
    if parsed.path.strip("/"):
        slug += "_" + parsed.path.strip("/").replace("/", "_")
    slug = re.sub(r"[^\w\-.]", "_", slug)[:120]
    return f"{slug or 'page'}.pdf"


def build_parser():
    parser = argparse.ArgumentParser(
        prog="webpage2pdf",
        description="把网页导出为像素级还原的分页 PDF（基于 Chrome 截图），"
                    "自动添加含标题/日期/URL/页码的页眉页脚。",
        formatter_class=argparse.ArgumentDefaultsHelpFormatter,
    )
    parser.add_argument("url", help="要导出的网页地址（可省略 https:// 前缀）")
    parser.add_argument("output", nargs="?", default=None,
                        help="输出 PDF 路径（默认根据 URL 自动生成）")
    parser.add_argument("-o", "--output", dest="output_opt", metavar="PATH",
                        help="输出 PDF 路径，等价于第二个位置参数")
    parser.add_argument("--login", action="store_true",
                        help="打开可见浏览器窗口，登录完成后回终端按回车再导出")
    parser.add_argument("--headed", action="store_true",
                        help="显示浏览器窗口（默认无头模式；部分反爬网站需要此选项）")
    parser.add_argument("--wait", type=float, default=3.0, metavar="SECONDS",
                        help="页面加载完成后的额外等待秒数")
    parser.add_argument("--no-scroll", action="store_true",
                        help="跳过截图前的全页滚动（滚动用于触发懒加载图片）")
    parser.add_argument("--width", type=int, default=1400, metavar="PX",
                        help="浏览器视口宽度")
    parser.add_argument("--scale", type=int, default=2, choices=[1, 2, 3],
                        help="截图缩放倍数（2 = Retina 高清）")
    parser.add_argument("--page-size", default="a4", choices=sorted(PAGE_SIZES),
                        help="纸张尺寸")
    parser.add_argument("--title", default=None,
                        help="覆盖页眉标题（默认取网页 <title>）")
    parser.add_argument("--no-header", action="store_true", help="不绘制页眉")
    parser.add_argument("--no-footer", action="store_true", help="不绘制页脚")
    parser.add_argument("--chrome-binary", default=None, metavar="PATH",
                        help="Chrome 可执行文件路径（默认自动探测）")
    parser.add_argument("--user-data-dir", default=None, metavar="DIR",
                        help="Chrome 用户数据目录，可复用已登录的会话")
    parser.add_argument("--version", action="version", version=f"%(prog)s {__version__}")
    return parser


def main(argv=None):
    args = build_parser().parse_args(argv)

    url = args.url
    if "://" not in url:
        url = "https://" + url
    out_path = args.output_opt or args.output or default_output(url)
    headless = not (args.login or args.headed)

    log(f"启动 Chrome（{'无头' if headless else '有窗口'}模式）...")
    try:
        driver = launch_browser(
            width=args.width,
            headless=headless,
            chrome_binary=args.chrome_binary,
            user_data_dir=args.user_data_dir,
        )
    except Exception as e:
        log(f"错误: 无法启动 Chrome: {e}")
        log("请确认已安装 Google Chrome，或用 --chrome-binary 指定路径。")
        return 1

    try:
        log(f"打开页面: {url}")
        driver.get(url)

        if args.login:
            print("请在 Chrome 窗口中完成登录，完成后回到终端按回车继续...")
            input()
        wait_for_page(driver, extra_wait=args.wait)

        if not args.no_scroll:
            log("滚动页面以触发懒加载...")
            trigger_lazy_load(driver)

        title = args.title or driver.title or url
        log(f"  标题: {title}")

        full_img = capture_full_page(driver, width=args.width, scale=args.scale)
        pages = paginate(
            full_img,
            title=title,
            url=url,
            date_str=datetime.date.today().strftime("%Y/%m/%d"),
            page_size=args.page_size,
            with_header=not args.no_header,
            with_footer=not args.no_footer,
        )
        save_pdf(pages, out_path, page_size=args.page_size)
        log(f"已保存: {out_path}（{len(pages)} 页）")
        return 0
    except KeyboardInterrupt:
        log("已取消")
        return 130
    finally:
        driver.quit()


if __name__ == "__main__":
    sys.exit(main())
