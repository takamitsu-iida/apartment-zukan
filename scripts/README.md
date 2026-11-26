# 実装メモ

オリジナルのサンプル画像は `images/samples` に格納しています。

長辺最大1000px、Exif除去済み画像を生成して `images/samples/optimized/` に同じ名前で格納しています。

`data.json` の `image` キーにはoptimizedの方を指定しています。


## 写真の緯度・経度を取得する

PythonのPillowモジュールを使い、元画像のExif GPS情報を読み取ります。

リポジトリのルートで実行してください。

```bash
# 初回のみ
python3 -m venv .venv
.venv/bin/python -m pip install -r scripts/requirements.txt

# 画像から座標を取得
.venv/bin/python scripts/extract_gps.py images/samples/IMG_0637.jpeg
```

出力例：

```json
{
  "lat": 35.407486,
  "lng": 139.587647
}
```

出力された値を `data.json` の該当物件に記載します。スクリプトは `data.json` を変更しません。

GPS情報のない画像やExif除去済みの公開用画像からは取得できません。

## 写真を縮小してExifを除去する

上記の初回準備後、リポジトリのルートで実行してください。

```bash
.venv/bin/python scripts/optimize_image.py images/samples/IMG_0637.jpeg \
  --output images/samples/optimized/IMG_0637_new.jpeg
```

`--output` を省略すると、元画像のあるフォルダー内の `optimized/` に同じファイル名で保存します。元画像や既存のファイルは上書きしません。

長辺が1000pxを超える画像は縦横比を保って縮小し、小さい画像は拡大しません。

Exifの向きを反映したうえでExifを除去します。

JPEG、PNG、WebPの静止画像に対応し、MPO形式は先頭の画像をJPEGとして保存します。
