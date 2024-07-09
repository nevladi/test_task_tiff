import requests
import os
import zipfile

from urllib.parse import urlencode
from PIL import Image

class CollageCreator:
    def __init__(
            self, base_url, public_key, local_folder, extracted_folder,
            output_file, img_size=(800, 800), padding=10, cols=4
        ):
        self.base_url = base_url
        self.public_key = public_key
        self.local_folder = local_folder
        self.extracted_folder = extracted_folder
        self.output_file = output_file
        self.img_width, self.img_height = img_size
        self.padding = padding
        self.cols = cols
        self.files = []

    def download_and_extract(self):
        final_url = self.base_url + urlencode(
            dict(public_key=self.public_key)
        )
        response = requests.get(final_url)
        
        if response.status_code == 200:
            data = response.json()
            href = data["href"]
            response = requests.get(href, stream=True)
            
            if not os.path.exists(self.local_folder):
                os.makedirs(self.local_folder)
            
            local_path = os.path.join(
                self.local_folder, "archive.zip"
            )
            with open(local_path, "wb") as f:
                for chunk in response.iter_content(1024):
                    f.write(chunk)
            print(f"Архив загружен в {local_path}")

            with zipfile.ZipFile(local_path, "r") as zip_ref:
                zip_ref.extractall(path=self.extracted_folder)
            print(f"Архив распакован в {self.extracted_folder}")
        else:
            print(
                f"Ошибка при получении списка файлов: {response.status_code}"
            )

    def collect_files(self):
        for root, dirs, filenames in os.walk(self.extracted_folder):
            for filename in filenames:
                if filename.endswith(".png"):
                    self.files.append(os.path.join(root, filename))
        print(f"Найдено {len(self.files)} изображений")

    def create_collage(self):
        rows = (len(self.files) + self.cols - 1) // self.cols
        collage_width = self.cols * (
            self.img_width + self.padding
        ) + self.padding
        collage_height = rows * (
            self.img_height + self.padding
        ) + self.padding
        collage_image = Image.new('RGB', (
            collage_width, collage_height
        ), 'white')

        for idx, file in enumerate(self.files):
            img = Image.open(file)
            resized_img = img.resize(
                (self.img_width, self.img_height)
            )
            x = (idx % self.cols) * (
                self.img_width + self.padding
            ) + self.padding
            y = (idx // self.cols) * (
                self.img_height + self.padding
            ) + self.padding
            collage_image.paste(resized_img, (x, y))

        collage_image.save(self.output_file)
        print(f"Коллаж сохранен в {self.output_file}")


if __name__ == "__main__":
    api_url = "https://cloud-api.yandex.net/v1/disk/public/resources/download?"
    url = "https://disk.yandex.ru/d/V47MEP5hZ3U1kg"
    local_folder = "download"
    extracted_folder = "all_files"
    output_file = "collage_final.tif"

    collage_creator = CollageCreator(
        api_url, url, local_folder, extracted_folder, output_file
    )
    collage_creator.download_and_extract()
    collage_creator.collect_files()
    collage_creator.create_collage()
