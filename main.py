import os
import requests
import time
import sys
import threading
from pathlib import Path
from urllib.parse import urlparse, parse_qs
import re

BASE_URL = "https://api.paxsenix.org/"

HEADERS = [
    ("Content-Type", "application/json"),
    ("Authorization", os.getenv("APIKEY"))
]

LOADING = ['|', '/', '-', '\\']

SERVERS = ["spotify","spotdl","deezer","youtube"]
EXTENSIONS = ["m4a","mp3"]

DEFAULT_SERVER = SERVERS[0]

def hasStorage() -> bool:
    storage_path = Path.home() / "storage"
    return storage_path.exists() and os.access(storage_path, os.R_OK)


def show_loader(stop_event) -> None:
    i = 0
    while not stop_event.is_set():
        sys.stdout.write(f"\rLoading... {LOADING[i % 4]}")
        sys.stdout.flush()
        i += 1
        time.sleep(0.1)
    sys.stdout.write("\r" + " " * 20 + "\r")

def search(q) -> list:
    results = []
    params = [("q", q)]

    stop_event = threading.Event()
    loader_thread = threading.Thread(target=show_loader, args=(stop_event,))
    loader_thread.start()

    time_start = time.time()

    try:
        req = requests.get(BASE_URL + "spotify/search", params=params, headers=dict(HEADERS))
    finally:
        stop_event.set()
        loader_thread.join()
        load_time = time.time() - time_start

    if not req.ok:
        print("Error code:", req.status_code)
        return []

    json_data = req.json()
    if json_data.get("ok"):
        for item in json_data["tracks"]["items"]:
            track_info = [
                item["name"],
                item["id"],
                int(item["duration_ms"]),
                item["album"]["name"],
                ", ".join(artist["name"] for artist in item["artists"]),
                f"{load_time:.3f}"
            ]
            results.append(track_info)
    return results

def download(track_id: str) -> None:
    stop_event = threading.Event()
    loader_thread = threading.Thread(target=show_loader, args=(stop_event,))
    loader_thread.start()

    try:
        params = {
            "url": f"https://open.spotify.com/track/{track_id.split('_')[0]}",
            "serv": DEFAULT_SERVER,
        }
        req = requests.get(
            BASE_URL + "dl/spotify",
            headers=dict(HEADERS),
            params=params,
            timeout=30,
        )
    finally:
        stop_event.set()
        loader_thread.join()

    if not req.ok:
        print(f"Error code: {req.status_code}")
        return

    data = req.json()

    if not data.get("ok"):
        print("API Error:", data.get("message", "Unknown error"))
        return

    direct_url = data.get("directUrl")
    if not direct_url:
        print("No download URL found.")
        return

    os.makedirs("/storage/emulated/0/Music/MDownloader", exist_ok=True)
    extension = "wav"
    if DEFAULT_SERVER == SERVERS[0]:
        extension = EXTENSIONS[0]
    elif DEFAULT_SERVER == SERVERS[1]:
        extension = EXTENSIONS[1]
    else:
        extension = "ogg"


    filename = f"{track_id.split("_")[1]}.{extension}"

    file_path = os.path.join("/storage/emulated/0/Music/MDownloader", filename)

    
    try:
        print("Please wait a moment...")
        with requests.get(direct_url, stream=True, timeout=60) as r:
            r.raise_for_status()
            total_size = int(r.headers.get("Content-Length", 0))
            downloaded = 0
            chunk_size = 8192

            with open(file_path, "wb") as f:
                for chunk in r.iter_content(chunk_size=chunk_size):
                    if chunk:
                        f.write(chunk)
                        downloaded += len(chunk)

                    if total_size:
                        percent = downloaded / total_size * 100
                        sys.stdout.write(f"\rDownloaded: {percent:.4f}%")
                        sys.stdout.flush()

        print("\nDownload complete!")
        print("file path : ", file_path)
        ret = str(input("Return to main menu?? (yes/exit) : ")).strip().lower()
        if ret == "y" or ret == "yes":
            main()
    except requests.RequestException as e:
        print(f"Download failed: {e}")


def main() -> None:
    if not hasStorage():
        os.system("termux-setup-storage")
        main()
    os.system("clear")
    print("SpotDL Spotify Downloader".center(76))
    print('-' * 76)
    print("[1]. Search")
    print("[2]. Download")
    print("[3]. Exit")
    print('-' * 76)

    try:
        choice = int(input("Enter your choice : "))
    except ValueError:
        print("Invalid input. Please enter a number.")
        time.sleep(2)
        main()
        return

    if choice == 1:
        query = input("Search songs : ")
        print('-' * 76)
        result = search(query)
        if result:
            os.system("clear")
            print('-' * 76)
            print(f"Results : {len(result)}")
            print(f"Response time: ", result[0][5], "secs")
            print('-' * 76)
            for i, track in enumerate(result, 1):
            
                minutes = track[2] // 60000
                seconds = (track[2] % 60000) // 1000
                print(f"Index   : {i}")
                print(f"Name    : {track[0]}")
                print(f"ID      : {track[1]}")
                print(f"Duration: {minutes}:{seconds:02}")
                print(f"Album   : {track[3]}")
                print(f"Artists : {track[4]}")
                print("-" * 76)
            ch = str(input("Do you want to download? (yes/no) : ")).strip().lower()
            if ch == "yes" or ch == "y":
                try:
                    index = int(input("Enter song Index you want to download : "))
                    if index <= len(result) and index > 0:
                        download(f"{result[index-1][1]}_{result[index-1][0]}_{result[index-1][3]}")
                except ValueError:
                    print("Invalid input. Please enter song Index only")
                    time.sleep(2)
                    main()
            else:
                time.sleep(2)
                main()
        else:
            print("No results found.")

    elif choice == 2:
        inp = input("Enter song Id/Url from spotify only : ")
        if inp.startswith('https:'):
            pattern = r"https://open\.spotify\.com/track/([A-Za-z0-9]+)"
            match = re.search(pattern, inp)
            if match:
                inp = match.group(1)
        download(inp)
    else:
        return

if __name__ == "__main__":
    main()
