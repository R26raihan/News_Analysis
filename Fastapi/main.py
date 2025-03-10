from fastapi import FastAPI, HTTPException
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
import time
import random
import json
import torch
from transformers import pipeline
from collections import Counter
from typing import Dict, List, Tuple
import uvicorn
import os
from contextlib import asynccontextmanager

# Inisialisasi FastAPI
app = FastAPI()

# Cek ketersediaan CUDA
if not torch.cuda.is_available():
    raise RuntimeError("CUDA tidak tersedia. Pastikan GPU dan driver terdeteksi.")
device = torch.device("cuda")
print(f"CUDA tersedia. Menggunakan perangkat: {torch.cuda.get_device_name(0)}")

# Path ke chromedriver
chrome_driver_path = os.getenv("CHROMEDRIVER_PATH", r"C:\laragon\www\sosialmedia-monitoring\chromedriver-win64\chromedriver.exe")
service = Service(executable_path=chrome_driver_path)
driver = webdriver.Chrome(service=service)

# Inisialisasi model NLP dengan CUDA
sentiment_analyzer = pipeline("sentiment-analysis", model="distilbert-base-multilingual-cased", device=0)

# Daftar sumber berita yang diperluas
news_sources = {
    "Detik": {
        "Terpopuler": "https://www.detik.com/terpopuler",
        "Otomotif": "https://oto.detik.com/",
        "Politik": "https://news.detik.com/politik",
        "Ekonomi": "https://finance.detik.com/",
        "Olahraga": "https://sport.detik.com/",
        "Teknologi": "https://inet.detik.com/",
        "Hiburan": "https://20.detik.com/"
    },
    "Kompas": {
        "Tren": "https://www.kompas.com/tren",
        "Otomotif": "https://otomotif.kompas.com/",
        "Politik": "https://nasional.kompas.com/politik",
        "Ekonomi": "https://money.kompas.com/",
        "Olahraga": "https://bola.kompas.com/",
        "Teknologi": "https://tekno.kompas.com/",
        "Hiburan": "https://www.kompas.com/hype"
    },
    "CNN Indonesia": {
        "Nasional": "https://www.cnnindonesia.com/nasional",
        "Otomotif": "https://www.cnnindonesia.com/otomotif",
        "Politik": "https://www.cnnindonesia.com/politik",
        "Ekonomi": "https://www.cnnindonesia.com/ekonomi",
        "Olahraga": "https://www.cnnindonesia.com/olahraga",
        "Teknologi": "https://www.cnnindonesia.com/teknologi",
        "Hiburan": "https://www.cnnindonesia.com/hiburan"
    },
    "Tempo": {
        "Terpopuler": "https://www.tempo.co/terpopuler",
        "Otomotif": "https://otomotif.tempo.co/",
        "Politik": "https://nasional.tempo.co/politik",
        "Ekonomi": "https://bisnis.tempo.co/",
        "Olahraga": "https://sport.tempo.co/",
        "Teknologi": "https://tekno.tempo.co/",
        "Hiburan": "https://cantik.tempo.co/"
    },
    "Tribunnews": {
        "Populer": "https://www.tribunnews.com/populer",
        "Otomotif": "https://www.tribunnews.com/otomotif",
        "Politik": "https://www.tribunnews.com/politik",
        "Ekonomi": "https://www.tribunnews.com/bisnis",
        "Olahraga": "https://www.tribunnews.com/sport",
        "Teknologi": "https://www.tribunnews.com/techno",
        "Hiburan": "https://www.tribunnews.com/seleb"
    },
    "Liputan6": {
        "News": "https://www.liputan6.com/news",
        "Otomotif": "https://www.liputan6.com/otomotif",
        "Politik": "https://www.liputan6.com/news/politik",
        "Ekonomi": "https://www.liputan6.com/bisnis",
        "Olahraga": "https://www.liputan6.com/bola",
        "Teknologi": "https://www.liputan6.com/tekno",
        "Hiburan": "https://www.liputan6.com/showbiz"
    },
    "Republika": {
        "Terpopuler": "https://www.republika.co.id/terpopuler",
        "Otomotif": "https://otomotif.republika.co.id/",
        "Politik": "https://nasional.republika.co.id/politik",
        "Ekonomi": "https://ekonomi.republika.co.id/",
        "Olahraga": "https://olahraga.republika.co.id/",
        "Teknologi": "https://tekno.republika.co.id/",
        "Islam": "https://islam.republika.co.id/"
    },
    "Okezone": {
        "Beranda": "https://www.okezone.com/",
        "Otomotif": "https://otomotif.okezone.com/",
        "Politik": "https://nasional.okezone.com/politik",
        "Ekonomi": "https://economy.okezone.com/",
        "Olahraga": "https://sports.okezone.com/",
        "Teknologi": "https://techno.okezone.com/",
        "Hiburan": "https://celebrity.okezone.com/"
    },
    "Suara": {
        "Terpopuler": "https://www.suara.com/terpopuler",
        "Otomotif": "https://www.suara.com/otomotif",
        "Politik": "https://www.suara.com/politik",
        "Ekonomi": "https://www.suara.com/bisnis",
        "Olahraga": "https://www.suara.com/sport",
        "Teknologi": "https://www.suara.com/tekno",
        "Hiburan": "https://www.suara.com/entertainment"
    },
    "Viva": {
        "Berita": "https://www.viva.co.id/berita",
        "Otomotif": "https://www.viva.co.id/otomotif",
        "Politik": "https://www.viva.co.id/berita/politik",
        "Ekonomi": "https://www.viva.co.id/berita/bisnis",
        "Olahraga": "https://www.viva.co.id/sport",
        "Teknologi": "https://www.viva.co.id/digital",
        "Hiburan": "https://www.viva.co.id/showbiz"
    },
    "Sindonews": {
        "Nasional": "https://nasional.sindonews.com/",
        "Otomotif": "https://otomotif.sindonews.com/",
        "Ekonomi": "https://ekonomi.sindonews.com/",
        "Olahraga": "https://sports.sindonews.com/",
        "Teknologi": "https://tekno.sindonews.com/",
        "Hiburan": "https://lifestyle.sindonews.com/"
    },
    "Antara News": {
        "Nasional": "https://www.antaranews.com/nasional",
        "Ekonomi": "https://www.antaranews.com/ekonomi",
        "Olahraga": "https://www.antaranews.com/olahraga",
        "Teknologi": "https://www.antaranews.com/teknologi",
        "Hiburan": "https://www.antaranews.com/hiburan"
    },
    "Bisnis.com": {
        "Ekonomi": "https://ekonomi.bisnis.com/",
        "Otomotif": "https://otomotif.bisnis.com/",
        "Teknologi": "https://teknologi.bisnis.com/",
        "Hiburan": "https://lifestyle.bisnis.com/"
    },
    "Jawa Pos": {
        "Nasional": "https://www.jawapos.com/nasional",
        "Ekonomi": "https://www.jawapos.com/ekonomi",
        "Olahraga": "https://www.jawapos.com/olahraga",
        "Teknologi": "https://www.jawapos.com/tekno",
        "Hiburan": "https://www.jawapos.com/entertainment"
    },
    "BBC Indonesia": {
        "Berita": "https://www.bbc.com/indonesia",
        "Internasional": "https://www.bbc.com/indonesia/internasional",
        "Teknologi": "https://www.bbc.com/indonesia/majalah"
    }
}

# Fungsi untuk scroll halaman
def scroll_to_bottom(max_scrolls=5):
    last_height = driver.execute_script("return document.body.scrollHeight")
    for _ in range(max_scrolls):
        driver.find_element(By.TAG_NAME, "body").send_keys(Keys.END)
        time.sleep(random.uniform(3, 7))
        new_height = driver.execute_script("return document.body.scrollHeight")
        if new_height == last_height:
            break
        last_height = new_height

# Fungsi untuk mengambil judul berita
def scrape_headlines(url: str, source_name: str, category: str) -> List[str]:
    driver.get(url)
    time.sleep(3)
    print(f"Memuat {source_name} - {category}...")
    scroll_to_bottom()

    selectors = {
    "Detik": ["media__title", "title", "h2", "article-title", "list-content__title", "media__link"],
    "Kompas": ["article__list__title", "title", "h3", "article-title", "headline__title", "kcm__title"],
    "CNN Indonesia": ["h2", "title", "article-title", "list__title", "nhd__title", "headline"],
    "Tempo": ["title", "h2", "h3", "article__title", "post-title", "judul"],
    "Tribunnews": ["txt-oev-2", "title", "h2", "article-title", "fbo2", "txt-oev-3"],
    "Liputan6": ["articles--iridescent-list--text-item__title", "title", "h2", "article-title", "headline", "list__title"],
    "Republika": ["h3", "title", "h2", "article-title", "headline", "post__title"],
    "Okezone": ["title", "h2", "h3", "article-title", "list-berita__title", "judul"],
    "Suara": ["inject-title", "title", "h2", "article-title", "headline", "post-title"],
    "Viva": ["title", "h2", "h3", "article-title", "headline", "news-title"],
    "Sindonews": ["title", "h2", "article-title", "headline"],
    "Antara News": ["title", "h2", "article-title", "post-title"],
    "Bisnis.com": ["title", "h2", "article-title", "headline"],
    "Jawa Pos": ["title", "h2", "article-title", "post-title"],
    "BBC Indonesia": ["title", "h2", "article-title", "headline"]
}


    headline_list = []
    for selector in selectors.get(source_name, ["title", "h2", "h3", "article-title"]):
        try:
            headlines = driver.find_elements(By.CLASS_NAME, selector)
            if not headlines:
                headlines = driver.find_elements(By.TAG_NAME, selector)
            headline_list = [headline.text.strip() for headline in headlines if headline.text.strip()]
            if headline_list:
                break
        except Exception as e:
            print(f"Gagal menggunakan selector '{selector}' untuk {source_name} - {category}: {e}")

    print(f"Ditemukan {len(headline_list)} judul dari {source_name} - {category}")
    return headline_list

# Fungsi untuk analisis sentimen dan mengembalikan data JSON
def analyze_data(all_headlines: Dict[str, Dict[str, List[str]]], keyword: str) -> Dict:
    keyword = keyword.lower()

    # Kumpulkan semua data yang relevan
    relevant_headlines: List[Tuple[str, str, str]] = [
        (source, category, headline)
        for source, categories in all_headlines.items()
        for category, headlines in categories.items()
        for headline in headlines
        if keyword in headline.lower()
    ]

    if not relevant_headlines:
        return {"message": f"Tidak ada data yang mengandung keyword '{keyword}'."}

    # Analisis sentimen dengan NLP (CUDA)
    sentiment_counts = {"Positif": 0, "Negatif": 0, "Netral": 0}
    examples = {"Positif": [], "Negatif": [], "Netral": []}
    source_counts = Counter([source for source, _, _ in relevant_headlines])
    category_counts = Counter([category for _, category, _ in relevant_headlines])

    print("Menganalisis sentimen dengan NLP (CUDA)...")
    texts = [text[:512] for _, _, text in relevant_headlines]  # Batch processing
    results = sentiment_analyzer(texts)

    detailed_results = []
    for (source, category, text), result in zip(relevant_headlines, results):
        label = result["label"]
        score = result["score"]

        if label == "POSITIVE" and score > 0.6:
            sentiment = "Positif"
        elif label == "NEGATIVE" and score > 0.6:
            sentiment = "Negatif"
        else:
            sentiment = "Netral"

        sentiment_counts[sentiment] += 1
        if len(examples[sentiment]) < 3:
            examples[sentiment].append({"source": source, "category": category, "text": text})

        detailed_results.append({
            "source": source,
            "category": category,
            "text": text,
            "sentiment": sentiment,
            "score": float(score)
        })

    total_relevant = len(relevant_headlines)
    sentiment_summary = {
        sentiment: {
            "count": count,
            "percentage": count / total_relevant * 100 if total_relevant > 0 else 0,
            "examples": examples[sentiment]
        }
        for sentiment, count in sentiment_counts.items()
    }

    # Struktur JSON untuk respons
    response = {
        "keyword": keyword,
        "total_items": total_relevant,
        "sentiment_summary": sentiment_summary,
        "source_distribution": dict(source_counts),
        "category_distribution": dict(category_counts),
        "detailed_results": detailed_results
    }

    # Simpan ke file JSON (opsional)
    with open(f"data_{keyword}_news_nlp_cuda.json", "w", encoding="utf-8") as f:
        json.dump(response, f, ensure_ascii=False, indent=4)
    print(f"Data disimpan ke 'data_{keyword}_news_nlp_cuda.json'")

    return response

# Endpoint FastAPI
@app.get("/analyze/{keyword}")
async def analyze_news(keyword: str):
    try:
        # Proses scraping berita
        all_headlines = {}
        for source_name, categories in news_sources.items():
            all_headlines[source_name] = {}
            for category, url in categories.items():
                try:
                    all_headlines[source_name][category] = scrape_headlines(url, source_name, category)
                except Exception as e:
                    print(f"Gagal mengambil {source_name} - {category}: {e}")

        # Hitung total judul berita yang diambil
        total_judul = sum(len(headlines) for source in all_headlines.values() for headlines in source.values())
        print(f"\nTotal judul berita yang diambil: {total_judul}")

        # Analisis data dan kembalikan JSON
        result = analyze_data(all_headlines, keyword)
        return result

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Terjadi kesalahan: {str(e)}")

# Tutup browser saat aplikasi berhenti
@app.on_event("shutdown")
def shutdown():
    driver.quit()

# Jalankan server (opsional, hanya untuk pengujian lokal)
if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)
