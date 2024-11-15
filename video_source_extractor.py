import os
import subprocess
import requests
from bs4 import BeautifulSoup
from plyer import notification
from pathlib import Path  # ダウンロードフォルダの取得に利用


# ダウンロードフォルダのパスを取得
def get_download_folder():
    return str(Path.home() / "Downloads")  # ユーザーディレクトリのダウンロードフォルダ


# contentURLを取得する関数
def fetch_content_url(url):
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/104.0.0.0 Safari/537.36'
    }
    try:
        response = requests.get(url, headers=headers)
        if response.status_code == 200:
            soup = BeautifulSoup(response.content, 'html.parser')
            meta_tag = soup.find('meta', {'itemprop': 'contentURL'})
            if meta_tag and 'content' in meta_tag.attrs:
                return meta_tag['content']
            else:
                print("エラー: 指定されたmetaタグが見つかりませんでした。")
                return None
        else:
            print(f"エラー: HTMLの取得に失敗しました。ステータスコード: {response.status_code}")
            return None
    except Exception as e:
        print(f"エラーが発生しました: {e}")
        return None


# FFmpegを実行する関数
def run_ffmpeg(input_url, save_path):
    command = [
        "ffmpeg",  # FFmpegの実行ファイル名（適宜修正）
        "-i", input_url,
        "-vn",  # 動画を無視
        "-acodec", "libmp3lame",  # MP3エンコード
        "-ab", "192k",  # ビットレート指定
        save_path
    ]
    try:
        subprocess.run(command, check=True)
        print(f"ダウンロード完了しました: {save_path}")
        notification.notify(
            title='ダウンロード完了',
            message=f'ダウンロードが完了しました: {save_path}',
            timeout=5
        )
    except subprocess.CalledProcessError as e:
        print(f"エラー: FFmpegエラー: {e}")
        notification.notify(
            title='エラー',
            message=f"FFmpegエラー: {e}",
            timeout=5
        )


# メイン関数
def main():
    download_folder = get_download_folder()
    print(f"デフォルトの保存先は: {download_folder}")

    while True:
        print("対象のURLを入力してください (空欄で終了):")
        url = input().strip()
        if not url:
            print("プログラムを終了します。")
            break

        # contentURL取得
        content_url = fetch_content_url(url)
        if not content_url:
            print("URLの取得に失敗しました。再度URLを入力してください。")
            continue

        # 保存先のファイル名を指定
        print("保存ファイル名を入力してください (例: output.mp3):")
        file_name = input().strip()
        if not file_name:
            print("エラー: ファイル名が指定されていません。")
            continue

        save_path = os.path.join(download_folder, file_name)

        # ダウンロード開始
        print(f"ダウンロードを開始します: {save_path}")
        run_ffmpeg(content_url, save_path)


if __name__ == "__main__":
    main()
