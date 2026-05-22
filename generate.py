"""
扫描 architecture/ portrait/ work/ 三个专题文件夹，
自动更新 portfolio-v2.html 中的图片列表。

使用方法：
  1. 将照片按专题放入对应文件夹（architecture/ portrait/ work/）
  2. 运行: python generate.py
  3. 打开 portfolio-v2.html 查看

支持的格式: JPG, JPEG, PNG, WebP, GIF, BMP, TIFF, AVIF
"""

import os
import re
import json
from pathlib import Path

SCRIPT_DIR = Path(__file__).parent
HTML_FILE = SCRIPT_DIR / 'portfolio-v2.html'

SECTIONS = [
    {'id': 'architecture', 'folder': 'architecture', 'name': 'Architecture', 'nameCN': '建筑', 'type': 'capsule', 'photos_key': 'photos'},
    {'id': 'portrait',     'folder': 'portrait',     'name': 'Portrait',     'nameCN': '人像', 'type': 'capsule', 'photos_key': 'photos'},
    {'id': 'work',         'folder': 'work',         'name': 'Work',         'nameCN': '工作经历', 'type': 'summary', 'photos_key': 'morePhotos'},
]

IMAGE_EXTS = {'.jpg', '.jpeg', '.png', '.webp', '.gif', '.bmp', '.tiff', '.tif', '.avif'}


def scan_section(sec):
    folder = SCRIPT_DIR / sec['folder']
    if not folder.exists():
        folder.mkdir()
        print(f"  [+] 已创建文件夹: {sec['folder']}/")
        return []

    files = []
    for f in sorted(folder.iterdir()):
        if f.suffix.lower() in IMAGE_EXTS:
            files.append(f)

    print(f"  [{sec['nameCN']}] {sec['folder']}/ — {len(files)} 张")
    for f in files:
        print(f"      - {f.name}")
    return files


def filename_to_caption(filename):
    name = Path(filename).stem
    name = re.sub(r'^[\d]+[_\-\s]+', '', name)
    name = name.replace('_', ' ').replace('-', ' ')
    name = re.sub(r'\s+', ' ', name).strip()
    return name if name else 'Untitled'


def build_photos_js(files, folder):
    lines = []
    for f in files:
        cap = filename_to_caption(f.name)
        lines.append(f"      {{ src: '{folder}/{f.name}', caption: '{cap}' }},")
    return '\n'.join(lines)


def update_html():
    if not HTML_FILE.exists():
        print(f"[!] 未找到 {HTML_FILE}")
        return False

    html = HTML_FILE.read_text(encoding='utf-8')

    for sec in SECTIONS:
        files = scan_section(sec)
        photos_js = build_photos_js(files, sec['folder'])
        key = sec['photos_key']

        # Match: { id: 'xxx', ... key: [ ... ] }
        pattern = rf"(id:\s*'{sec['id']}'[\s\S]*?{key}:\s*\[)[\s\S]*?(\])"
        replacement = rf"\1\n{photos_js}\n    \2"

        if re.search(pattern, html):
            html = re.sub(pattern, replacement, html)
            print(f"  [+] 已更新 {sec['nameCN']} 专题图片列表")
        else:
            print(f"  [!] 未找到 {sec['nameCN']} 的 {key} 配置")

    HTML_FILE.write_text(html, encoding='utf-8')
    print(f"\n[OK] 完成！打开 portfolio-v2.html 查看。")
    return True


def main():
    print("=" * 50)
    print("  摄影作品集 · 专题图片扫描工具")
    print("=" * 50)
    print()
    print("扫描专题文件夹：")
    print()
    update_html()


if __name__ == '__main__':
    main()
