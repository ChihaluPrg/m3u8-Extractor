import tkinter as tk
from tkinter import filedialog
from plyer import notification  # plyer通知をインポート
import requests
from bs4 import BeautifulSoup
import subprocess
import threading  # スレッドを使用


# contentURLを取得する関数
def fetch_content_url():
    url = url_entry.get()  # 入力されたURLを取得
    if not url:
        messagebox.showerror("エラー", "URLを入力してください。")
        return

    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/104.0.0.0 Safari/537.36'
    }

    try:
        response = requests.get(url, headers=headers)
        if response.status_code == 200:
            soup = BeautifulSoup(response.content, 'html.parser')
            meta_tag = soup.find('meta', {'itemprop': 'contentURL'})
            if meta_tag and 'content' in meta_tag.attrs:
                content_url = meta_tag['content']
                result_label.config(text=f"contentURL: {content_url}")
                return content_url  # contentURLを返す
            else:
                messagebox.showerror("エラー", "指定されたmetaタグが見つかりませんでした。")
        else:
            messagebox.showerror("エラー", f"HTMLの取得に失敗しました。ステータスコード: {response.status_code}")
    except Exception as e:
        messagebox.showerror("エラー", f"エラーが発生しました: {e}")


# ダウンロードを開始する関数
def start_download():
    content_url = fetch_content_url()  # contentURLを取得
    if not content_url:
        return

    # 形式を選択
    file_format = format_var.get()  # 選択された形式を取得

    # 保存先とファイル名を指定するダイアログを開く
    save_path = filedialog.asksaveasfilename(defaultextension=f".{file_format}",
                                             filetypes=[(f"{file_format.upper()} files", f"*.{file_format}")])
    if not save_path:
        return  # 保存先が選ばれなかった場合

    # FFmpegコマンドを構築
    if file_format == 'mp3':
        command = [
            "ffmpeg",
            "-i", content_url,
            "-vn",  # 動画を無視
            "-acodec", "libmp3lame",  # MP3エンコード
            "-ab", "192k",  # ビットレート指定
            save_path
        ]
    elif file_format == 'mp4':
        command = [
            "ffmpeg",
            "-i", content_url,
            "-c", "copy",
            "-bsf:a", "aac_adtstoasc",
            save_path
        ]
    elif file_format == 'wav':
        command = [
            "ffmpeg",
            "-i", content_url,
            "-vn",  # 動画を無視
            "-acodec", "pcm_s16le",  # WAVエンコード
            save_path
        ]

    # ダウンロード開始の通知を表示
    notification.notify(
        title='ダウンロード開始',
        message='ダウンロードが開始されました。',
        timeout=5  # 5秒間表示
    )

    # ダウンロードをバックグラウンドスレッドで実行
    download_thread = threading.Thread(target=run_ffmpeg, args=(command, save_path))
    download_thread.start()


# FFmpegをバックグラウンドで実行する関数
def run_ffmpeg(command, save_path):
    try:
        # subprocessでFFmpegを実行
        subprocess.run(command, check=True)

        # ダウンロード完了の通知を表示
        notification.notify(
            title='ダウンロード完了',
            message=f'{save_path} へのダウンロードが完了しました。',
            timeout=5  # 5秒間表示
        )
    except subprocess.CalledProcessError as e:
        messagebox.showerror("エラー", f"FFmpegエラー: {e}")


# GUIのセットアップ
root = tk.Tk()
root.title("Video Source Extractor")

# URL入力ラベルとテキストボックス
url_label = tk.Label(root, text="対象のURLを入力:")
url_label.pack(padx=10, pady=5)

url_entry = tk.Entry(root, width=50)
url_entry.pack(padx=10, pady=5)

# 結果表示ラベル
result_label = tk.Label(root, text="結果がここに表示されます", wraplength=400)
result_label.pack(padx=10, pady=10)

# contentURLを取得ボタン
fetch_button = tk.Button(root, text="contentURLを取得", command=fetch_content_url)
fetch_button.pack(padx=10, pady=10)

# 形式選択ラベルとドロップダウンメニュー
format_label = tk.Label(root, text="保存形式を選択:")
format_label.pack(padx=10, pady=5)

format_var = tk.StringVar(root)
format_var.set("mp4")  # デフォルト形式
format_menu = tk.OptionMenu(root, format_var, "mp4", "mp3", "wav")
format_menu.pack(padx=10, pady=5)

# ダウンロード開始ボタン
download_button = tk.Button(root, text="ダウンロード開始", command=start_download)
download_button.pack(padx=10, pady=10)

# アプリケーションを開始
root.mainloop()
