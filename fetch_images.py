import requests
from bs4 import BeautifulSoup
from concurrent.futures import ThreadPoolExecutor, as_completed
import os 

car_url = "https://www.dubizzle.com.lb/vehicles/cars-for-sale/"
main_url = "https://www.dubizzle.com.lb/"

def fetch_urls_from_page(base_url,page):
    print("starting page",page)
    urls = set()
    car_url = f"{base_url}?page={page}"
    try:
        response = requests.get(car_url, timeout=10)
        soup = BeautifulSoup(response.text, 'html.parser')
        listings = soup.find_all('a')
        for listing in listings:
            detail_url = listing.get('href')
            if detail_url and detail_url.startswith("/ad"):
                urls.add(detail_url)
    except Exception as e:
        print(f"Error fetching page {page}: {e}")
    print("ending page",page)

    return urls

def get_all_car_urls(base_url,initial_page=1, max_workers=10):
    all_urls = set()
    page = initial_page
    chunk_size = 10
    
    with ThreadPoolExecutor(max_workers=max_workers) as executor:
        while True:
            future_to_page = {executor.submit(fetch_urls_from_page,base_url, p): p for p in range(page, page + chunk_size)}
            page += chunk_size
            new_urls_found = False
            
            for future in as_completed(future_to_page):
                page_number = future_to_page[future]
                try:
                    urls = future.result()
                    if urls and not urls.issubset(all_urls):
                        all_urls.update(urls)
                        new_urls_found = True
                except Exception as exc:
                    print(f'Page {page_number} generated an exception: {exc}')
            
            if not new_urls_found:
                break  
            
    return list(all_urls)

def download_images(base_url, image_url, save_dir):
    if not os.path.exists(save_dir):
        os.makedirs(save_dir)

    url = f"{base_url}{image_url}"

    response = requests.get(url, timeout=10)
    soup = BeautifulSoup(response.text, "html.parser")
    
    images = [img['src'] for img in soup.find_all("img") if img.get('src') and img['src'].endswith("800x600.jpeg") and img['src'].startswith("https://images")]
    
    for img_url in images:
        image_name = img_url.split("/")[-1]
        image_path = os.path.join(save_dir, image_name)
        
        try:
            img_response = requests.get(img_url, stream=True)
            if img_response.status_code == 200:
                with open(image_path, 'wb') as f:
                    for chunk in img_response.iter_content(1024):
                        f.write(chunk)
                print(f"Downloaded {img_url} successfully.")
        except Exception as e:
            print(f"Error downloading {img_url}: {e}")
        
        
def download_all_images(base_url, image_urls, save_dir, max_workers=10):
    with ThreadPoolExecutor(max_workers=max_workers) as executor:
        future_to_url = {executor.submit(download_images, base_url, image_url, save_dir): image_url for image_url in image_urls}

        for future in as_completed(future_to_url):
            url = future_to_url[future]
            try:
                future.result()
                print(f"Finished downloading images for {url}.")
            except Exception as exc:
                print(f'{url} generated an exception: {exc}')



    
if __name__ == "__main__":
    car_urls = get_all_car_urls(car_url)
    print(f"Found {len(car_urls)} car URLs.")
    download_all_images(main_url, car_urls, "car_images")

    

