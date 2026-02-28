import os
import requests
from flask import Flask, render_template, request, jsonify
from requests.auth import HTTPBasicAuth

app = Flask(__name__)

# ==========================================
# 取得したSpotify APIのキーをここに設定してください
# ==========================================
SPOTIFY_CLIENT_ID = os.getenv('SPOTIFY_CLIENT_ID')
SPOTIFY_CLIENT_SECRET = os.getenv('SPOTIFY_CLIENT_SECRET')

def get_spotify_token():
    """Spotify APIのアクセストークンを取得する"""
    url = "https://accounts.spotify.com/api/token"
    auth = HTTPBasicAuth(SPOTIFY_CLIENT_ID, SPOTIFY_CLIENT_SECRET)
    data = {"grant_type": "client_credentials"}
    response = requests.post(url, auth=auth, data=data)
    if response.status_code == 200:
        return response.json().get("access_token")
    return None

def search_popular_track_by_year(year, token):
    """指定された年の日本で人気の曲を検索する"""
    url = "https://api.spotify.com/v1/search"
    headers = {"Authorization": f"Bearer {token}"}
    
    # yearパラメータで年を指定し、日本のマーケットで検索
    params = {
        "q": f"year:{year}",
        "type": "track",
        "market": "JP",
        "limit": 10
    }
    response = requests.get(url, headers=headers, params=params)
    
    if response.status_code == 200:
        tracks = response.json().get("tracks", {}).get("items", [])
        if not tracks:
            return None
        
        # 取得した結果から、Spotifyのpopularity（人気度）が高い順にソートして1位を返す
        tracks.sort(key=lambda x: x.get('popularity', 0), reverse=True)
        return tracks[0]
    return None

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/api/get_track', methods=['POST'])
def get_track():
    data = request.json
    year = data.get('year')

    if not year:
        return jsonify({"error": "西暦が入力されていません"}), 400

    token = get_spotify_token()
    if not token:
        return jsonify({"error": "Spotify APIの認証に失敗しました。APIキーを確認してください。"}), 500

    track = search_popular_track_by_year(year, token)
    if not track:
        return jsonify({"error": f"{year}年の曲が見つかりませんでした。"}), 404

    # フロントエンドにはTrack IDと曲情報を返す
    return jsonify({
        "track_id": track["id"],
        "name": track["name"],
        "artist": track["artists"][0]["name"]
    })

if __name__ == '__main__':
    app.run(debug=True, port=5000)
