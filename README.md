# MDownloader

> A Termux-based Spotify music downloader for Android — search, preview, and save tracks directly to your device.

---

## Features

- **Search** Spotify tracks by name, artist, or album
- **Download** songs directly to `/storage/emulated/0/Music/MDownloader`
- **Live progress bar** during downloads
- **Multiple servers** — Spotify, SpotDL, Deezer, YouTube
- **Format support** — M4A, MP3, OGG
- **Animated loader** while fetching results

---

## Requirements

- [Termux](https://termux.dev/) on Android
- Python 3.8+
- Storage permission (`termux-setup-storage`)
- A valid [PaxSenix API key](https://api.paxsenix.org/)

---

## Installation

```bash
# Update packages
pkg update && pkg upgrade

# Install Python & git
pkg install python git

# Clone the repo
git clone https://github.com/yourusername/mdownloader.git
cd mdownloader

# Install dependencies
pip install requests

# Set your API key
export APIKEY="your_paxsenix_api_key_here"

# Run
python main.py
```

---

## Usage

```
============================================================
              SpotDL Spotify Downloader
------------------------------------------------------------
[1]. Search
[2]. Download
[3]. Exit
------------------------------------------------------------
```

### Search & Download
1. Choose **[1] Search** and enter a song name or artist
2. Browse results with track name, ID, duration, album, and artists
3. Enter the index of the song you want and confirm the download

### Direct Download by URL or ID
1. Choose **[2] Download**
2. Paste a Spotify track URL or bare track ID

```
# Example input
https://open.spotify.com/track/4uLU6hMCjMI75M1A2tKUQC

# or just the ID
4uLU6hMCjMI75M1A2tKUQC
```

---

## Configuration

You can modify these constants at the top of `main.py`:

| Variable | Default | Description |
|---|---|---|
| `DEFAULT_SERVER` | `"spotify"` | Download server to use |
| `SERVERS` | `["spotify", "spotdl", "deezer", "youtube"]` | Available servers |
| `EXTENSIONS` | `["m4a", "mp3"]` | Supported audio formats |
| `BASE_URL` | `https://api.paxsenix.org/` | API base URL |

---

## Output

Downloaded files are saved to:
```
/storage/emulated/0/Music/MDownloader/
```

File names follow the format:
```
{track_name}_{album}.{extension}
```

---

## How It Works

```
User Input
    │
    ├─► Search ──► GET /spotify/search ──► Display results
    │
    └─► Download
            │
            ├─► GET /dl/spotify?url=...&serv=...
            │
            └─► Stream directUrl → save to device
```

The app uses a background threading loader to keep the terminal interactive while waiting on API responses, and streams download chunks with a live percentage counter.

---

## API Key Setup

This project uses the [PaxSenix API](https://api.paxsenix.org/). Set your key as an environment variable:

```bash
# Temporary (current session)
export APIKEY="your_key_here"

# Permanent (add to ~/.bashrc or ~/.zshrc)
echo 'export APIKEY="your_key_here"' >> ~/.bashrc
source ~/.bashrc
```

---

## Notes

- This tool is intended for **personal use only**
- Downloading copyrighted music may violate Spotify's Terms of Service in your region
- Works best on Termux with storage permissions granted

---

## Contributing

Pull requests are welcome! For major changes, please open an issue first to discuss what you'd like to change.

---

## License

[MIT](LICENSE) © 2025 daemmonnn
