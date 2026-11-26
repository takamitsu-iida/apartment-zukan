# 🏢✨ 珍名アパート・マンション図鑑 (Unusual Apartment Zukan)

> 「なんだこれ！？」街で見つけた面白すぎる・カッコよすぎる・謎すぎる名前のアパートやマンションを、写真と地図でひたすらコレクションしていく個人開発のWeb図鑑です。🕵️‍♂️🗺️

いずれスマホアプリにしようと思いますが、まずは静的なウェブページで動作を確認中です。

ライブでもはこちら（↓）のGithub Pagesから確認できます。

[ライブデモ](https://takamitsu-iida.github.io/apartment-zukan/)

<br>

## 🌟 このサイトについて (About)

お散歩中に出会う「ちょっと待て」と言いたくなるようなアパート名。
* なぜその名前になったのか？🤔
* どこの国の言葉が混ざっているのか？
* そもそもどういう意味なのか？

そんな疑問を、**現地の写真**と**Google/OpenStreetMapのマップ**、推測解説とともにまとめているお散歩マップです！👟💨

<br>

## 🗺️ サンプルではこんな物件を載せてます（一部ご紹介！）

| 物件名 | 雰囲気・由来の推測 |
| :--- | :--- |
| **アンシャンテ上大岡**[cite: 1] | フランス語で「はじめまして」！新生活のワクワクが詰まったお出迎え物件[cite: 1]。 |
| **上大岡 リリエンハイム**[cite: 2] | ドイツ語の「ユリ（Lilien）＋家（Heim）」[cite: 2]。銘板の百合の彫刻がエレガント✨ |
| **HERMIT CRAB HOUSE**[cite: 3] | 直訳：**「ヤドカリの家」**。賃貸の住み替えをヤドカリに見立てた天才的ネーミング[cite: 3]！ |
| **サン パピヨン カサハラ**[cite: 5] | 太陽（Sun）＋ 蝶（Papillon）＋ オーナーの苗字（笠原さん）の奇跡の合体[cite: 5]。 |

<br>

## 🛠️ 使っている技術 (Tech Stack)

このサイトはサーバー代0円・完全静的（Static）で動いています💡

* **Frontend:** HTML5, CSS3, JavaScript (Vanilla JS)
* **Map:** Leaflet.js + OpenStreetMap
* **Exif Reader:** exifr (写真からGPSを自動抽出)
* **Hosting:** GitHub Pages

サンプル画像は `images/samples/optimized/` の長辺最大1000px・Exif除去済み画像を表示し、元画像は `images/samples/` に残しています。`data.json` の `image` には公開用画像のパスを指定します。
