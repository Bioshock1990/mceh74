#!/usr/bin/env python3
"""
Instagram Post Downloader - Simple Version
Минимальный вывод в консоль, полная функциональность
"""

import os
import re
import time
import instaloader
from pathlib import Path

class SimpleInstagramDownloader:
    def __init__(self, delay=2):
        self.delay = delay
        self.loader = instaloader.Instaloader(
            download_pictures=True,
            download_videos=True,
            download_geotags=False,
            download_comments=False,
            save_metadata=False,
            compress_json=False,
            post_metadata_txt_pattern='',
            max_connection_attempts=3
        )
        
    def extract_shortcode_from_url(self, url):
        patterns = [
            r'instagram\.com/p/([A-Za-z0-9_-]+)',
            r'instagram\.com/reel/([A-Za-z0-9_-]+)',
            r'instagr\.am/p/([A-Za-z0-9_-]+)'
        ]
        
        for pattern in patterns:
            match = re.search(pattern, url)
            if match:
                return match.group(1)
        return None
    
    def create_post_folder(self, post_index, shortcode):
        folder_name = f"post_{post_index:03d}_{shortcode[:8]}"
        folder_path = Path(folder_name)
        folder_path.mkdir(exist_ok=True)
        return folder_path
    
    def download_post_images(self, post, folder_path):
        downloaded_images = []
        
        try:
            self.loader.download_post(post, target=str(folder_path))
            
            for file_path in folder_path.iterdir():
                if file_path.suffix.lower() in ['.jpg', '.jpeg', '.png']:
                    image_number = len(downloaded_images) + 1
                    new_name = f"image_{image_number}{file_path.suffix}"
                    new_path = folder_path / new_name
                    file_path.rename(new_path)
                    downloaded_images.append(str(new_path))
                    
        except Exception:
            pass
            
        return downloaded_images
    
    def save_description(self, post, folder_path):
        description_path = folder_path / "description.txt"
        
        try:
            caption = post.caption or ""
            
            content = f"Автор: @{post.owner_username}\n"
            content += f"Дата: {post.date}\n"
            content += f"Лайков: {post.likes}\n"
            content += f"Комментариев: {post.comments}\n"
            content += f"URL: https://www.instagram.com/p/{post.shortcode}/\n"
            content += "\n" + "="*50 + "\n\n"
            content += caption
            
            with open(description_path, 'w', encoding='utf-8') as f:
                f.write(content)
                
            return str(description_path)
            
        except Exception:
            return None
    
    def process_post(self, url, post_index):
        try:
            shortcode = self.extract_shortcode_from_url(url)
            if not shortcode:
                return False
            
            post = instaloader.Post.from_shortcode(self.loader.context, shortcode)
            
            folder_path = self.create_post_folder(post_index, shortcode)
            downloaded_images = self.download_post_images(post, folder_path)
            description_path = self.save_description(post, folder_path)
            
            return True
            
        except Exception:
            return False
    
    def load_links_from_file(self, filename="links.txt"):
        try:
            with open(filename, 'r', encoding='utf-8') as f:
                links = [line.strip() for line in f if line.strip()]
            return links
        except FileNotFoundError:
            return []
        except Exception:
            return []
    
    def run(self, links_file="links.txt"):
        links = self.load_links_from_file(links_file)
        if not links:
            return
        
        successful_downloads = 0
        failed_downloads = 0
        
        for i, url in enumerate(links, 1):
            print(f"[{i}/{len(links)}] ", end="", flush=True)
            
            if self.process_post(url, i):
                successful_downloads += 1
                print(f"✅ Скачано")
            else:
                failed_downloads += 1
                print(f"❌ Ошибка")
            
            if i < len(links):
                time.sleep(self.delay)
        
        print(f"\nГотово: ✅{successful_downloads} ❌{failed_downloads} Всего: {len(links)}")


if __name__ == "__main__":
    downloader = SimpleInstagramDownloader(delay=2)
    downloader.run()
