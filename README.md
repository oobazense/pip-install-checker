# pip-license-checker

pip 拡張機能でライセンスチェックを行うツールです。パッケージをインストールする前に、そのライセンスが許可リストに含まれているかを確認します。

## 特徴

- パッケージのインストール前にライセンスを確認
- 許可されていないライセンスの場合は警告と確認を表示
- 確認時に許可リストに新しいライセンスを追加可能
- プロジェクトフォルダに `requirements_license.txt` ファイルを自動生成
- 許可するライセンスのリストを `allowed_licenses.json` として保存
- ライセンス名の表記揺れを吸収する正規化機能（大文字小文字やハイフン/アンダースコアなどを無視）
- パッケージとその依存関係の区別（直接インストールか依存パッケージか）
- ライセンスステータスの自動更新と修正機能

## プロジェクト構成

```
pip-install-checker/
├── pip_license_checker.py  # メインのプログラムコード
├── setup.py                # インストール設定ファイル
├── README.md               # このドキュメント
├── .gitignore              # Git管理対象外ファイル設定
└── LICENSE                 # ライセンスファイル
```

インストール後に自動生成されるファイル:

```
プロジェクトディレクトリ/
├── allowed_licenses.json   # 許可されたライセンスのリスト
└── requirements_license.txt # パッケージとそのライセンス情報
```

キャッシュファイル（Git で管理しない）:

```
pip-install-checker/
├── __pycache__/           # Pythonコンパイルキャッシュ（自動生成）
└── *.egg-info/            # パッケージメタデータ（インストール時に生成）
```

## インストール方法

```bash
# GitHubからインストール
[git clone https://github.com/yourusername/pip-license-checker.git](https://github.com/oobazense/pip-install-checker)
cd pip-install-checker
pip install -e .
```

## 使い方の流れ

### 1. 初期設定

最初にプロジェクトを初期化します：

```bash
pip license init
```

これにより、以下のファイルが作成されます：

- `allowed_licenses.json` - 許可されたライセンスリスト（初期値として一般的なオープンソースライセンスが設定されます）
- `requirements_license.txt` - インストールされたパッケージとそのライセンス情報

また、既存の環境にインストール済みのパッケージをスキャンして記録します。許可リストに含まれていないライセンスが見つかった場合は、自動的に追加するかどうかを確認されます。

初期化の最後にはステータスの最終確認が自動的に実行され、すべてのパッケージが正しいステータスマーク（✅/❓）で表示されていることを確認します。

### 2. ライセンスチェック付きでパッケージをインストール

```bash
pip license install パッケージ名
```

処理の流れ：

1. パッケージのライセンスを確認
2. 許可リストにあれば、自動的にインストール
3. 許可リストにない場合：
   - 警告表示
   - インストールを続行するかを確認
   - 許可リストにライセンスを追加するか確認
4. インストール情報を `requirements_license.txt` に記録
5. 依存パッケージの情報も自動的に記録（依存パッケージとして明示）
6. **インストール後に全パッケージのライセンスステータスを自動更新**

### 3. 許可ライセンスの管理

許可リストを確認：

```bash
pip license list
```

ライセンスを許可リストに追加：

```bash
pip license add "ライセンス名"
```

ライセンスを許可リストから削除：

```bash
pip license remove "ライセンス名"
```

ライセンスを追加・削除した後は自動的に `requirements_license.txt` のステータスが更新されます。

### 4. 既存環境のスキャン

インストール済みのパッケージをスキャンして記録：

```bash
pip license scan
```

このコマンドを実行すると、現在の環境にインストールされている全パッケージのライセンス情報を取得し、`requirements_license.txt` に記録します。自動的に許可リストに追加するかどうかも選択できます。

スキャン後は自動的にステータスが確認され、必要に応じて更新されます。

### 5. ライセンスステータスの更新

```bash
pip license update
```

このコマンドは `requirements_license.txt` に記録されているパッケージのライセンスステータス（✅/❓）を最新の許可リストに基づいて更新します。ライセンスリストを編集した後や、ステータスが正しくない場合に使用します。

ライセンス名の表記揺れ（大文字小文字の違いや、スペース、ハイフン、アンダースコアなど）は正規化されて比較されるため、実質的に同じライセンスであれば異なる表記でも適切に認識されます。

### 6. ライセンスチェックのみ実行（インストールなし）

```bash
pip license check パッケージ名 [パッケージ名2 ...]
```

## 具体的な使用例

### 新しいプロジェクトでの使用例

```bash
# 1. プロジェクトディレクトリに移動
cd myproject

# 2. 初期化（既存パッケージのスキャンも行われます）
pip license init

# 3. 必要なパッケージをインストール（ライセンスチェック付き）
pip license install pandas
pip license install requests numpy

# 4. 特定のライセンスを手動で許可リストに追加
pip license add "GPL-3.0"

# 5. 許可されたライセンスの一覧を確認
pip license list

# 6. ライセンスステータスの更新（必要に応じて）
pip license update
```

### 既存プロジェクトへの導入例

```bash
# 1. プロジェクトディレクトリに移動
cd existing_project

# 2. 初期化して既存パッケージをスキャン
pip license init

# 3. requirements.txtからインストールする代わりに
# pip license installを使用してライセンスチェックを行いながらインストール
cat requirements.txt | xargs -n 1 pip license install
```

### トラブルシューティング

ライセンスステータスが正しく表示されない場合：

```bash
# ステータスの再確認と修正
pip license update
```

## ファイル形式

### requirements_license.txt

```
# このファイルにはインストールされたパッケージとそのライセンスが記録されます
# format: [ステータス] package_name==version [license] [インストールタイプ]
# ステータス: ✅=許可済み, ❓=未確認
✅ pandas==2.2.3 [MIT + file LICENSE] [直接インストール]
✅ numpy==2.2.4 [Copyright (c) 2005-2024, NumPy Developers.] [依存パッケージ]
❓ requests==2.32.3 [Apache-2.0] [直接インストール]
```

### allowed_licenses.json

```json
{
  "allowed_licenses": [
    "MIT",
    "BSD",
    "BSD-3-Clause",
    "Apache 2.0",
    "Apache Software License",
    "Apache License, Version 2.0"
  ]
}
```

## 内部動作の説明

1. **ライセンス正規化機能**：

   - ライセンス名の比較時、`normalize_license_name`関数を使用
   - 大文字小文字、スペース、ハイフン、アンダースコアなどの違いを無視
   - 例：`MIT License`と`mit-license`は同じライセンスとして扱われる

2. **自動ステータス更新**：

   - ライセンスの追加/削除後、自動的にステータスを更新
   - `init`コマンドや`scan`コマンドの最後にも実行
   - 誤ったステータスを検出して修正

3. **ライセンス情報取得方法**：
   - pip show コマンドの結果から取得
   - メタデータ（importlib.metadata または pkg_resources）からも取得を試行
   - 複数の方法を組み合わせて取得精度を向上

## ライセンス

このプロジェクトは [MIT License](LICENSE) の下で公開されています。
