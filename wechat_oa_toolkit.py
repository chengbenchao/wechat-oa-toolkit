#!/usr/bin/env python3
"""
微信公众号草稿箱发布工具
支持：获取access_token、上传封面图、创建草稿
"""

import urllib.request
import urllib.parse
import json
import os
import sys
import hashlib
from pathlib import Path


class WeChatOAToolkit:
    """微信公众号API工具包"""

    def __init__(self, appid: str = None, secret: str = None):
        self.appid = appid or os.environ.get("WECHAT_APPID", "")
        self.secret = secret or os.environ.get("WECHAT_SECRET", "")
        self.access_token = None

        if not self.appid or not self.secret:
            raise ValueError(
                "请设置 WECHAT_APPID 和 WECHAT_SECRET 环境变量，\n"
                "或在初始化时传入 appid 和 secret 参数"
            )

    def get_access_token(self) -> str:
        """获取微信公众号 access_token"""
        url = (
            f"https://api.weixin.qq.com/cgi-bin/token?"
            f"grant_type=client_credential&appid={self.appid}&secret={self.secret}"
        )
        req = urllib.request.Request(url)
        with urllib.request.urlopen(req) as resp:
            data = json.loads(resp.read().decode("utf-8"))

        if "access_token" in data:
            self.access_token = data["access_token"]
            print(f"[OK] access_token 获取成功（有效期 7200 秒）")
            return self.access_token
        else:
            errcode = data.get("errcode", "unknown")
            errmsg = data.get("errmsg", "unknown")
            if errcode == 40164:
                # 提取白名单提示中的 IP
                print(f"[ERROR] IP 不在白名单中！请将当前服务器 IP 添加到微信公众平台 IP 白名单")
                print(f"  错误详情: {errmsg}")
            else:
                print(f"[ERROR] 获取 access_token 失败: errcode={errcode}, errmsg={errmsg}")
            raise RuntimeError(f"获取 access_token 失败: {data}")

    def upload_image(self, image_path: str) -> str:
        """
        上传图片到微信素材库（永久素材）
        返回 media_id，可用于文章封面
        """
        if not self.access_token:
            self.get_access_token()

        image_path = Path(image_path)
        if not image_path.exists():
            raise FileNotFoundError(f"图片文件不存在: {image_path}")

        url = (
            f"https://api.weixin.qq.com/cgi-bin/material/add_material?"
            f"access_token={self.access_token}&type=image"
        )

        # 构造 multipart/form-data 请求
        filename = image_path.name
        content_type = self._guess_content_type(filename)

        with open(image_path, "rb") as f:
            file_data = f.read()

        boundary = "----WebKitFormBoundary7MA4YWxkTrZu0gW"
        body = (
            f"--{boundary}\r\n"
            f'Content-Disposition: form-data; name="media"; filename="{filename}"\r\n'
            f"Content-Type: {content_type}\r\n\r\n"
        ).encode("utf-8") + file_data + f"\r\n--{boundary}--\r\n".encode("utf-8")

        req = urllib.request.Request(
            url,
            data=body,
            headers={
                "Content-Type": f"multipart/form-data; boundary={boundary}",
            },
        )

        with urllib.request.urlopen(req) as resp:
            data = json.loads(resp.read().decode("utf-8"))

        if "media_id" in data:
            print(f"[OK] 封面图上传成功，media_id: {data['media_id']}")
            return data["media_id"]
        else:
            errcode = data.get("errcode", "unknown")
            errmsg = data.get("errmsg", "unknown")
            print(f"[ERROR] 上传图片失败: errcode={errcode}, errmsg={errmsg}")
            raise RuntimeError(f"上传图片失败: {data}")

    def create_draft(
        self,
        title: str,
        content: str,
        thumb_media_id: str,
        digest: str = "",
        author: str = "",
        need_open_comment: int = 1,
        only_fans_can_comment: int = 0,
    ) -> str:
        """
        创建微信公众号草稿
        返回草稿的 media_id
        """
        if not self.access_token:
            self.get_access_token()

        url = f"https://api.weixin.qq.com/cgi-bin/draft/add?access_token={self.access_token}"

        payload = {
            "articles": [
                {
                    "title": title,
                    "author": author,
                    "digest": digest,
                    "content": content,
                    "thumb_media_id": thumb_media_id,
                    "need_open_comment": need_open_comment,
                    "only_fans_can_comment": only_fans_can_comment,
                }
            ]
        }

        body = json.dumps(payload, ensure_ascii=False).encode("utf-8")
        req = urllib.request.Request(
            url,
            data=body,
            headers={"Content-Type": "application/json; charset=utf-8"},
        )

        with urllib.request.urlopen(req) as resp:
            data = json.loads(resp.read().decode("utf-8"))

        if "media_id" in data:
            print(f"[OK] 草稿创建成功，media_id: {data['media_id']}")
            return data["media_id"]
        else:
            errcode = data.get("errcode", "unknown")
            errmsg = data.get("errmsg", "unknown")
            print(f"[ERROR] 创建草稿失败: errcode={errcode}, errmsg={errmsg}")
            raise RuntimeError(f"创建草稿失败: {data}")

    def publish_article(
        self,
        title: str,
        content: str,
        cover_image_path: str,
        digest: str = "",
        author: str = "",
    ) -> str:
        """
        一键发布：上传封面 → 创建草稿
        返回草稿 media_id
        """
        print(f"\n{'='*50}")
        print(f"  开始发布文章: {title}")
        print(f"{'='*50}\n")

        # Step 1: 获取 access_token
        print("[Step 1/3] 获取 access_token...")
        self.get_access_token()

        # Step 2: 上传封面图
        print(f"\n[Step 2/3] 上传封面图: {cover_image_path}")
        thumb_media_id = self.upload_image(cover_image_path)

        # Step 3: 创建草稿
        print(f"\n[Step 3/3] 创建草稿...")
        draft_media_id = self.create_draft(
            title=title,
            content=content,
            thumb_media_id=thumb_media_id,
            digest=digest,
            author=author,
        )

        print(f"\n{'='*50}")
        print(f"  发布完成！")
        print(f"  草稿 media_id: {draft_media_id}")
        print(f"  请登录 mp.weixin.qq.com → 草稿箱 查看")
        print(f"{'='*50}\n")

        return draft_media_id

    @staticmethod
    def _guess_content_type(filename: str) -> str:
        ext = Path(filename).suffix.lower()
        content_types = {
            ".png": "image/png",
            ".jpg": "image/jpeg",
            ".jpeg": "image/jpeg",
            ".gif": "image/gif",
            ".bmp": "image/bmp",
        }
        return content_types.get(ext, "application/octet-stream")


# ========== 命令行入口 ==========
if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description="微信公众号草稿箱发布工具")
    parser.add_argument("--appid", help="微信公众号 AppID（也可通过环境变量 WECHAT_APPID 设置）")
    parser.add_argument("--secret", help="微信公众号 AppSecret（也可通过环境变量 WECHAT_SECRET 设置）")
    parser.add_argument("--title", required=True, help="文章标题")
    parser.add_argument("--digest", default="", help="文章摘要")
    parser.add_argument("--author", default="", help="作者名")
    parser.add_argument("--content-file", help="文章正文 HTML 文件路径")
    parser.add_argument("--content", help="文章正文 HTML 内容（直接传入）")
    parser.add_argument("--cover-image", required=True, help="封面图文件路径")
    parser.add_argument("--token-only", action="store_true", help="仅获取 access_token")

    args = parser.parse_args()

    toolkit = WeChatOAToolkit(appid=args.appid, secret=args.secret)

    if args.token_only:
        print(toolkit.get_access_token())
        sys.exit(0)

    # 读取文章内容
    content = args.content or ""
    if args.content_file:
        with open(args.content_file, "r", encoding="utf-8") as f:
            content = f.read()

    if not content:
        print("[ERROR] 请通过 --content 或 --content-file 提供文章内容")
        sys.exit(1)

    toolkit.publish_article(
        title=args.title,
        content=content,
        cover_image_path=args.cover_image,
        digest=args.digest,
        author=args.author,
    )
