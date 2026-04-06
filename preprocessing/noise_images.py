import concurrent.futures
from bing_image_downloader import downloader

def download_images(query):
    try:
        # Downloading 320 images per query to hit your ~950 target
        downloader.download(query, limit=320, output_dir='simple_images', adult_filter_off=True, force_replace=False, timeout=60, verbose=True)
    except Exception as e:
        print(f"Error downloading {query}: {e}")

search_queries = ["football stadium crowd", "football pitch texture", "empty soccer field"]

# Using ThreadPoolExecutor downloads all 3 queries at once
with concurrent.futures.ThreadPoolExecutor() as executor:
    list(executor.map(download_images, search_queries))