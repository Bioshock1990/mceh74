#!/usr/bin/env python3
"""
Instagram Post Downloader
Скачивает изображения и описания из постов Instagram по списку ссылок

Требования:
- Python 3.7+
- instaloader

Установка:
pip install instaloader

Использование:
1. Создайте файл links.txt в той же директории
2. Добавьте ссылки на посты Instagram (одна ссылка на строку)
3. Запустите: python instagram_downloader.py
"""

import os
import re
import time
import instaloader
from pathlib import Path
from urllib.parse import urlparse
import argparse

class InstagramDownloader:
    def __init__(self, delay=2):
        """
        Инициализация загрузчика
        
        Args:
            delay (int): Задержка между запросами в секундах
        """
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
        self.session_file = "session"
        
    def extract_shortcode_from_url(self, url):
        """
        Извлекает shortcode из URL поста Instagram
        
        Args:
            url (str): URL поста Instagram
            
        Returns:
            str: shortcode поста или None если не найден
        """
        # Паттерны для различных форматов URL Instagram
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
    
    def sanitize_filename(self, filename):
        """
        Очищает имя файла от недопустимых символов
        
        Args:
            filename (str): Исходное имя файла
            
        Returns:
            str: Очищенное имя файла
        """
        # Удаляем или заменяем недопустимые символы для Windows
        invalid_chars = r'[<>:"/\\|?*]'
        filename = re.sub(invalid_chars, '_', filename)
        # Ограничиваем длину имени
        if len(filename) > 100:
            filename = filename[:100]
        return filename
    
    def create_post_folder(self, post_index, shortcode):
        """
        Создает папку для поста
        
        Args:
            post_index (int): Порядковый номер поста
            shortcode (str): ID поста
            
        Returns:
            str: Путь к созданной папке
        """
        folder_name = f"post_{post_index:03d}_{shortcode[:8]}"
        folder_path = Path(folder_name)
        folder_path.mkdir(exist_ok=True)
        return folder_path
    
    def download_post_images(self, post, folder_path):
        """
        Скачивает изображения из поста
        
        Args:
            post: Объект поста instaloader
            folder_path (Path): Путь к папке поста
            
        Returns:
            list: Список путей к скачанным изображениям
        """
        downloaded_images = []
        
        try:
            # Скачиваем пост с помощью instaloader
            self.loader.download_post(post, target=str(folder_path))
            
            # Ищем скачанные изображения
            for file_path in folder_path.iterdir():
                if file_path.suffix.lower() in ['.jpg', '.jpeg', '.png']:
                    # Переименовываем в формат image_N.jpg
                    image_number = len(downloaded_images) + 1
                    new_name = f"image_{image_number}{file_path.suffix}"
                    new_path = folder_path / new_name
                    
                    # Переименовываем файл
                    file_path.rename(new_path)
                    downloaded_images.append(str(new_path))
                    
        except Exception as e:
            print(f"Ошибка при скачивании изображений: {e}")
            
        return downloaded_images
    
    def save_description(self, post, folder_path):
        """
        Сохраняет описание поста в файл
        
        Args:
            post: Объект поста instaloader
            folder_path (Path): Путь к папке поста
            
        Returns:
            str: Путь к файлу с описанием
        """
        description_path = folder_path / "description.txt"
        
        try:
            # Получаем текст поста
            caption = post.caption or ""
            
            # Формируем содержимое файла
            content = f"Автор: @{post.owner_username}\n"
            content += f"Дата: {post.date}\n"
            content += f"Лайков: {post.likes}\n"
            content += f"Комментариев: {post.comments}\n"
            content += f"URL: https://www.instagram.com/p/{post.shortcode}/\n"
            content += "\n" + "="*50 + "\n\n"
            content += caption
            
            # Сохраняем в файл
            with open(description_path, 'w', encoding='utf-8') as f:
                f.write(content)
                
            return str(description_path)
            
        except Exception as e:
            print(f"Ошибка при сохранении описания: {e}")
            return None
    
    def process_post(self, url, post_index):
        """
        Обрабатывает один пост
        
        Args:
            url (str): URL поста Instagram
            post_index (int): Порядковый номер поста
            
        Returns:
            bool: True если пост успешно обработан, False в противном случае
        """
        try:
            print(f"\n[{post_index}] Обработка поста: {url}")
            
            # Извлекаем shortcode
            shortcode = self.extract_shortcode_from_url(url)
            if not shortcode:
                print(f"❌ Не удалось извлечь ID поста из URL: {url}")
                return False
            
            print(f"📝 ID поста: {shortcode}")
            
            # Получаем объект поста
            post = instaloader.Post.from_shortcode(self.loader.context, shortcode)
            
            # Создаем папку для поста
            folder_path = self.create_post_folder(post_index, shortcode)
            print(f"📁 Создана папка: {folder_path}")
            
            # Скачиваем изображения
            print("📸 Скачивание изображений...")
            downloaded_images = self.download_post_images(post, folder_path)
            print(f"✅ Скачано изображений: {len(downloaded_images)}")
            
            # Сохраняем описание
            print("📄 Сохранение описания...")
            description_path = self.save_description(post, folder_path)
            if description_path:
                print(f"✅ Описание сохранено: {description_path}")
            
            print(f"✅ Пост {post_index} успешно обработан")
            return True
            
        except instaloader.exceptions.ProfileNotExistsException:
            print(f"❌ Профиль не существует: {url}")
        except instaloader.exceptions.PostNotFoundException:
            print(f"❌ Пост не найден (удален или приватный): {url}")
        except instaloader.exceptions.PrivateProfileNotFollowedException:
            print(f"❌ Приватный профиль (требуется подписка): {url}")
        except instaloader.exceptions.LoginRequiredException:
            print(f"❌ Требуется вход в аккаунт: {url}")
        except Exception as e:
            print(f"❌ Ошибка при обработке поста {url}: {e}")
            
        return False
    
    def load_links_from_file(self, filename="links.txt"):
        """
        Загружает ссылки из файла
        
        Args:
            filename (str): Имя файла с ссылками
            
        Returns:
            list: Список ссылок
        """
        try:
            with open(filename, 'r', encoding='utf-8') as f:
                links = [line.strip() for line in f if line.strip()]
            return links
        except FileNotFoundError:
            print(f"❌ Файл {filename} не найден!")
            print(f"Создайте файл {filename} и добавьте ссылки на посты Instagram (одна на строку)")
            return []
        except Exception as e:
            print(f"❌ Ошибка при чтении файла {filename}: {e}")
            return []
    
    def run(self, links_file="links.txt"):
        """
        Запускает процесс скачивания
        
        Args:
            links_file (str): Имя файла с ссылками
        """
        print("🚀 Запуск Instagram Downloader")
        print("="*50)
        
        # Загружаем ссылки
        links = self.load_links_from_file(links_file)
        if not links:
            return
        
        print(f"📋 Найдено ссылок: {len(links)}")
        
        successful_downloads = 0
        failed_downloads = 0
        
        # Обрабатываем каждый пост
        for i, url in enumerate(links, 1):
            print(f"\n{'='*50}")
            print(f"Пост {i}/{len(links)}")
            
            if self.process_post(url, i):
                successful_downloads += 1
            else:
                failed_downloads += 1
            
            # Задержка между запросами
            if i < len(links):
                print(f"⏳ Пауза {self.delay} секунд...")
                time.sleep(self.delay)
        
        # Вывод статистики
        print(f"\n{'='*50}")
        print("📊 СТАТИСТИКА")
        print(f"✅ Успешно скачано: {successful_downloads}")
        print(f"❌ Ошибок: {failed_downloads}")
        print(f"📁 Всего обработано: {len(links)} постов")
        print("🎉 Работа завершена!")


def main():
    """Главная функция"""
    parser = argparse.ArgumentParser(description='Instagram Post Downloader')
    parser.add_argument(
        '--delay', 
        type=int, 
        default=2, 
        help='Задержка между запросами в секундах (по умолчанию: 2)'
    )
    parser.add_argument(
        '--file', 
        type=str, 
        default='links.txt', 
        help='Имя файла с ссылками (по умолчанию: links.txt)'
    )
    
    args = parser.parse_args()
    
    # Создаем и запускаем загрузчик
    downloader = InstagramDownloader(delay=args.delay)
    downloader.run(links_file=args.file)


if __name__ == "__main__":
    main()
