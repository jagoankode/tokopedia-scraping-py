from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import time
import re
import csv
import datetime

# Setup Chrome Options (opsional, bisa untuk mode headless, dll.)
chrome_options = Options()
chrome_options.add_argument("--headless") # Jalankan tanpa membuka jendela browser
chrome_options.add_argument("--disable-gpu")
chrome_options.add_argument("--no-sandbox")
chrome_options.add_argument(
    "user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/90.0.4430.212 Safari/537.36")  # Contoh User Agent

# Path ke ChromeDriver Anda
# Pastikan versi ChromeDriver cocok dengan versi Google Chrome Anda
# Unduh dari: https://chromedriver.chromium.org/downloads
webdriver_service = Service('/opt/homebrew/bin/chromedriver')  # <-- GANTI DENGAN PATH ANDA

# Inisialisasi WebDriver
driver = webdriver.Chrome(service=webdriver_service, options=chrome_options)

# URL target (Contoh: halaman pencarian atau produk spesifik)
url_tokopedia = "https://www.tokopedia.com/search?q=kaos&source=universe&st=product"  # <-- Ganti nama_produk

all_data = []

try:
    driver.get(url_tokopedia)

    # Tunggu hingga elemen produk muncul (GANTI DENGAN SELECTOR YANG BENAR)
    # Ini bagian yang paling rapuh dan perlu diinspeksi manual via Developer Tools
    wait = WebDriverWait(driver, 10)  # Tunggu maksimal 20 detik

    # Contoh selector (INI SESUAI STRUKTUR TOKOPEDIA SAAT INI)
    product_selector_css = "div[class='css-5wh65g']"
    wait.until(EC.presence_of_all_elements_located((By.CSS_SELECTOR, product_selector_css)))

    # Temukan semua elemen produk di halaman
    products = driver.find_elements(By.CSS_SELECTOR, product_selector_css)

    limit = 0
    while limit < 10:
        for index, product in enumerate(products):
            try:
                class_a_wrapper = "a[class='oQ94Awb6LlTiGByQZo8Lyw== IM26HEnTb-krJayD-R0OHw==']"
                a_wrapper = product.find_element(By.CSS_SELECTOR, class_a_wrapper)

                # GET Image
                img_att = "div > div[class='FsRHU-HdyqHfg3GrIQNUWA=='] > div > div img"
                get_img = a_wrapper.find_element(By.CSS_SELECTOR, img_att)
                image = get_img.get_attribute('src')

                # GET Title
                title_att = "div > div[class='WABnq4pXOYQihv0hUfQwOg== '] > div > span"
                get_title = a_wrapper.find_element(By.CSS_SELECTOR, title_att)
                title = get_title.text

                # GET Price
                discount_price_selector = "div > div[class='WABnq4pXOYQihv0hUfQwOg== '] > div[class='XvaCkHiisn2EZFq0THwVug=='] > div[class='_67d6E1xDKIzw+i2D2L0tjw== t4jWW3NandT5hvCFAiotYg==']"
                price_selector = "div > div[class='WABnq4pXOYQihv0hUfQwOg== '] > div[class='XvaCkHiisn2EZFq0THwVug=='] > div"
                get_price = a_wrapper.find_element(By.CSS_SELECTOR, price_selector) or a_wrapper.find_element(By.CSS_SELECTOR, price_selector)
                pattern = r"[Rr][Pp]|\."
                price = float(re.sub(pattern, "", get_price.text))

                all_data.append({
                    'product_name': title,
                    'price': price,
                    'image_uri': image
                })

                limit += 1
                print(f"{limit}: {title}")
                if limit > 9:
                    break
            except Exception as e_inner:
                print(f"Gagal mengekstrak data satu produk: {e_inner}")

            # Tambahkan jeda untuk menghindari dianggap bot
            time.sleep(1)


except Exception as e:
    print(f"Terjadi kesalahan: {e}")

finally:
    # Selalu tutup browser setelah selesai
    driver.quit()

csv_file_path = f"./data/{datetime.date.today().strftime('%d-%m-%Y')}-tokopedia-scrape.csv"
csv_columns = ['product_name', 'price', 'image_uri']
try:
    with open(csv_file_path, 'a', newline='', encoding='utf-8') as csvfile:
        writer = csv.DictWriter(csvfile, fieldnames=csv_columns)
        # Tulis header hanya jika file belum ada atau kosong
        if csvfile.tell() == 0:
            writer.writeheader()
        writer.writerows(all_data)
    print(f"Data berhasil ditambahkan ke {csv_file_path}")
except Exception as e:
    print(f"Terjadi kesalahan saat menulis ke CSV: {e}")