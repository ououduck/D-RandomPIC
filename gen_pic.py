import os
import shutil
from pathlib import Path
from itertools import cycle

# 配置
SOURCE_DIR = Path("pic")
OUTPUT_DIR = Path("dist")

# ---------------------------------------------------------
# 核心配置：HASH 长度
# 2 => 16^2 = 256 个文件
# 3 => 16^3 = 4096 个文件 (对应 Cloudflare 规则 substring(..., 0, 3))
# ---------------------------------------------------------
HASH_LENGTH = 3
NUM_FILES = 16 ** HASH_LENGTH

# 输出文件后缀 (如果你的规则是 .json，这里依然建议生成 .jpg，
# 除非你真的是想生成包含图片信息的 json 文本文件。
# 这里默认生成 .jpg，请确保 CF 规则也是 .jpg)
OUTPUT_EXT = ".jpg" 

def ensure_dir(path: Path):
    if not path.exists():
        path.mkdir(parents=True)

def process_category(category_name: str, source_files: list):
    """处理单个分类"""
    category_output_dir = OUTPUT_DIR / category_name
    ensure_dir(category_output_dir)
    
    # 清空该分类目录
    for item in category_output_dir.iterdir():
        if item.is_file():
            item.unlink()

    num_source_imgs = len(source_files)
    if num_source_imgs == 0:
        return

    # 计算重复次数
    avg_copies = NUM_FILES / num_source_imgs
    print(f"  [{category_name}] Found {num_source_imgs} images. Generating {NUM_FILES} files...")

    img_cycle = cycle(source_files)
    count = 0
    
    for i in range(NUM_FILES):
        src_img = next(img_cycle)
        
        # 生成十六进制文件名: 000.jpg ... fff.jpg
        file_name = f"{i:0{HASH_LENGTH}x}{OUTPUT_EXT}"
        dest_path = category_output_dir / file_name
        
        shutil.copy(src_img, dest_path)
        count += 1
        
    print(f"  [{category_name}] Done. {count} files generated.")

def main():
    if not SOURCE_DIR.exists():
        print(f"Error: Source directory '{SOURCE_DIR}' does not exist.")
        return

    # 1. 准备输出根目录
    if OUTPUT_DIR.exists():
        # 这里选择不直接删除整个 dist，而是清理其中的文件，防止误删其他东西
        # 但为了保证干净，还是建议删除重建，或者由子任务处理覆盖
        pass
    else:
        ensure_dir(OUTPUT_DIR)

    # 2. 扫描一级子目录（作为分类）
    # 如果直接有图片，视为 "default" 分类或者报错？
    # 根据用户需求，应该是处理 "子文件夹"
    
    subdirs = [d for d in SOURCE_DIR.iterdir() if d.is_dir()]
    
    # 同时也支持根目录下的图片（可选，视作无分类或根分类）
    # 但为了逻辑清晰，我们优先处理子目录。如果根目录下有图片，可以放入 'default' 或忽略。
    # 这里我们只处理子目录。
    
    if not subdirs:
        print(f"No subdirectories found in {SOURCE_DIR}. Please create category folders (e.g. {SOURCE_DIR}/pc).")
        # 兼容旧模式：如果只有图片没有子目录，就当做根目录处理？
        # 还是严格按照新需求？用户说“将这个文件夹中的所有子文件夹放到 ./dist”
        # 假设必须有子文件夹。
        return

    print(f"Found {len(subdirs)} categories: {[d.name for d in subdirs]}")

    extensions = {".jpg", ".jpeg", ".png", ".gif", ".webp"}

    for subdir in subdirs:
        category = subdir.name
        images = sorted([
            f for f in subdir.iterdir() 
            if f.is_file() and f.suffix.lower() in extensions
        ])
        
        if images:
            process_category(category, images)
        else:
            print(f"  [{category}] No images found, skipping.")

    print(f"\nAll done. Check '{OUTPUT_DIR}' directory.")

if __name__ == "__main__":
    main()