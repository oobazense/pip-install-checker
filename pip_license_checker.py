# pip_license_checker.py
import json
import os
import sys
import argparse
import subprocess
from pathlib import Path
from pip._internal.commands import create_command

# 現在のプロジェクトディレクトリを取得
CURRENT_DIR = os.getcwd()
REQUIREMENTS_LICENSE_PATH = os.path.join(CURRENT_DIR, "requirements_license.txt")
LICENSE_CONFIG_PATH = os.path.join(CURRENT_DIR, "allowed_licenses.json")

def ensure_config_exists():
    """設定ファイルが存在することを確認し、存在しない場合は作成します"""
    # デフォルトの許可ライセンスリスト
    default_allowed_licenses = [
        "MIT", 
        "BSD", 
        "Apache-2.0", 
        "Apache Software License",
        "Apache License, Version 2.0",
        "Python Software Foundation License",
        "Copyright (c) 2005-2024, NumPy Developers.",
        "Dual License"
    ]
    
    # ファイルが存在しない場合は作成
    if not os.path.exists(LICENSE_CONFIG_PATH):
        with open(LICENSE_CONFIG_PATH, 'w') as f:
            json.dump({"allowed_licenses": default_allowed_licenses}, f, indent=2)
        print(f"✅ 許可ライセンス設定ファイルを作成しました: {LICENSE_CONFIG_PATH}")
        return
    
    # ファイルは存在するが、内容を確認する
    try:
        with open(LICENSE_CONFIG_PATH, 'r') as f:
            config = json.load(f)
            
        # 許可リストが空または存在しない場合はデフォルト値を設定
        if "allowed_licenses" not in config or not config["allowed_licenses"]:
            print("✅ 空の許可リストを検出したためデフォルト値を設定します")
            config["allowed_licenses"] = default_allowed_licenses
            
            with open(LICENSE_CONFIG_PATH, 'w') as f:
                json.dump(config, f, indent=2)
                f.flush()
                os.fsync(f.fileno())
            print(f"✅ 空の許可リストにデフォルト値を設定しました: {LICENSE_CONFIG_PATH}")
            
    except (json.JSONDecodeError, FileNotFoundError, IOError) as e:
        # 破損したJSONを修復
        print(f"⚠️ 許可リストファイルの読み込みエラー: {e}")
        with open(LICENSE_CONFIG_PATH, 'w') as f:
            json.dump({"allowed_licenses": default_allowed_licenses}, f, indent=2)
            f.flush()
            os.fsync(f.fileno())
        print(f"✅ 破損した許可ライセンス設定ファイルを修復しました: {LICENSE_CONFIG_PATH}")

def ensure_requirements_license_exists():
    """requirements_license.txtが存在することを確認し、存在しない場合は作成します"""
    if not os.path.exists(REQUIREMENTS_LICENSE_PATH):
        with open(REQUIREMENTS_LICENSE_PATH, 'w') as f:
            f.write("# このファイルにはインストールされたパッケージとそのライセンスが記録されます\n")
            f.write("# format: [ステータス] package_name==version [license] [インストールタイプ]\n")
            f.write("# ステータス: ✅=許可済み, ❓=未確認\n")
        print(f"✅ ライセンス要件ファイルを作成しました: {REQUIREMENTS_LICENSE_PATH}")

def load_allowed_licenses():
    """許可されたライセンスのリストを読み込みます"""
    # 設定ファイルの存在確認（空の場合はデフォルト値が設定される）
    ensure_config_exists()
    
    # デフォルトの許可リスト（フォールバック用）
    default_allowed_licenses = [
        "MIT", 
        "BSD", 
        "Apache-2.0", 
        "Apache Software License",
        "Apache License, Version 2.0",
        "Python Software Foundation License",
        "Copyright (c) 2005-2024, NumPy Developers.",
        "Dual License"
    ]
    
    try:
        with open(LICENSE_CONFIG_PATH, 'r') as f:
            config = json.load(f)
        
        # 許可リストを取得（空の場合はデフォルト値を使用）
        allowed_licenses = config.get("allowed_licenses", [])
        if not allowed_licenses:
            print("⚠️ 許可リストが空のため、デフォルト値を使用します")
            return default_allowed_licenses
        
        return allowed_licenses
    except Exception as e:
        print(f"⚠️ 許可リストの読み込み中にエラーが発生しました: {e}")
        print("⚠️ デフォルトの許可リストを使用します")
        return default_allowed_licenses

def save_allowed_licenses(allowed_licenses):
    """許可されたライセンスのリストを保存します"""
    # 空のリストが渡された場合は、デフォルト値を使用する
    if not allowed_licenses:
        print("⚠️ 警告: 空のライセンスリストが渡されました。デフォルト値を使用します。")
        allowed_licenses = [
            "MIT", 
            "BSD", 
            "Apache-2.0", 
            "Apache Software License",
            "Apache License, Version 2.0",
            "Python Software Foundation License",
            "Copyright (c) 2005-2024, NumPy Developers.",
            "Dual License"
        ]
    
    # 設定ファイルの存在を確認
    ensure_config_exists()
    
    # 保存前にライセンスリストからNoneや空の値を除外
    allowed_licenses = [lic for lic in allowed_licenses if lic and lic.strip()]
    
    # それでも空の場合はデフォルト値を使用
    if not allowed_licenses:
        print("⚠️ 警告: フィルタリング後も許可リストが空です。デフォルト値を使用します。")
        allowed_licenses = [
            "MIT", 
            "BSD", 
            "Apache-2.0", 
            "Apache Software License",
            "Apache License, Version 2.0",
            "Python Software Foundation License",
            "Copyright (c) 2005-2024, NumPy Developers.",
            "Dual License"
        ]
    
    # 重複を除去
    allowed_licenses = list(set(allowed_licenses))
    
    print(f"許可リストに保存されるライセンス: {allowed_licenses}")
    
    # 保存処理を実行
    try:
        # ファイルに書き込む
        with open(LICENSE_CONFIG_PATH, 'w') as f:
            json.dump({"allowed_licenses": allowed_licenses}, f, indent=2)
            f.flush()  # 確実にディスクに書き込む
            os.fsync(f.fileno())  # OSレベルでのフラッシュを確実に行う
        
        # 書き込み後に再度読み込んで確認
        with open(LICENSE_CONFIG_PATH, 'r') as f:
            saved_config = json.load(f)
        
        if saved_config.get("allowed_licenses") == allowed_licenses:
            print(f"✅ 許可リストを正常に更新しました: {len(allowed_licenses)}個のライセンス")
        else:
            print("❌ 許可リストの保存に問題がありました")
            # 問題があった場合は再度保存を試みる
            with open(LICENSE_CONFIG_PATH, 'w') as f:
                json.dump({"allowed_licenses": allowed_licenses}, f, indent=2)
                f.flush()
                os.fsync(f.fileno())
            print("✅ 2回目の試行で許可リストを保存しました")
    except Exception as e:
        print(f"❌ 許可リストの保存中にエラーが発生しました: {e}")
        # エラー時のフォールバック処理
        try:
            with open(LICENSE_CONFIG_PATH, 'w') as f:
                json.dump({"allowed_licenses": allowed_licenses}, f, indent=2)
            print("✅ フォールバック処理で許可リストを保存しました")
        except Exception as e2:
            print(f"❌ フォールバック処理でもエラーが発生しました: {e2}")

def normalize_license_name(license_name):
    """ライセンス名を正規化します（大文字小文字やハイフンなどの違いを無視）"""
    if not license_name:
        return ""
    
    # 特定のライセンス表記を標準化
    normalized = license_name.lower().strip()
    
    # 標準形式への変換マッピング
    license_mapping = {
        "mit": "MIT",
        "bsd": "BSD",
        "apache": "Apache",
        "apache2": "Apache-2.0",
        "apache-2.0": "Apache-2.0",
        "apache 2.0": "Apache-2.0",
        "apache license 2.0": "Apache-2.0",
        "apache software license": "Apache-2.0",
        "gnu gpl": "GPL",
        "gnu general public license": "GPL",
        "gnu lesser general public license": "LGPL",
        "gnu library or lesser general public license": "LGPL",
        "mozilla public license": "MPL",
        "python software foundation": "PSF",
        "python software foundation license": "PSF",
    }
    
    # 正規化された名前をライセンスマッピングで検索
    for key, value in license_mapping.items():
        if key in normalized.replace(" ", "").replace("-", "").replace("_", ""):
            return value
    
    # マッピングにない場合は元の値を返す（小文字や空白の処理などは行わない）
    return license_name

def update_requirements_license(package_name, version, license_info, requires=None, is_direct=True):
    """requirements_license.txtファイルを更新します"""
    ensure_requirements_license_exists()
    
    # 既存のファイルを読み込む
    lines = []
    if os.path.exists(REQUIREMENTS_LICENSE_PATH):
        with open(REQUIREMENTS_LICENSE_PATH, 'r') as f:
            lines = f.readlines()
    
    # 許可されたライセンスのリストを取得
    allowed_licenses = load_allowed_licenses()
    
    # ライセンスのステータスを設定（正規化して比較）
    normalized_license = normalize_license_name(license_info)
    is_allowed = False
    
    for allowed in allowed_licenses:
        if normalize_license_name(allowed) == normalized_license:
            is_allowed = True
            break
    
    status = "✅" if is_allowed else "❓"
    
    # パッケージがすでに存在するか確認
    install_type = "[直接インストール]" if is_direct else "[依存パッケージ]"
    package_entry = f"{status} {package_name}=={version} [{license_info}] {install_type}\n"
    package_found = False
    
    for i, line in enumerate(lines):
        if package_name + "==" in line and not line.startswith('#'):
            lines[i] = package_entry
            package_found = True
            break
    
    # パッケージが存在しない場合は追加
    if not package_found:
        lines.append(package_entry)
    
    # ファイルに書き込む
    with open(REQUIREMENTS_LICENSE_PATH, 'w') as f:
        f.writelines(lines)
    
    # 依存パッケージの情報も追加
    if requires and is_direct:
        for req in requires:
            req_version, req_license, req_deps = get_package_info(req)
            update_requirements_license(req, req_version, req_license, None, False)

def get_package_info(package_name):
    """パッケージの情報（バージョンとライセンス）を取得します"""
    try:
        # パッケージ情報を取得
        cmd = [sys.executable, "-m", "pip", "show", package_name]
        process = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        stdout, stderr = process.communicate()
        
        # 出力からライセンス情報とバージョンを抽出
        output = stdout.decode('utf-8')
        license_info = ""
        version = "Unknown"
        requires = []
        
        for line in output.split('\n'):
            if line.startswith('License:'):
                license_info = line.replace('License:', '').strip()
            elif line.startswith('Version:'):
                version = line.replace('Version:', '').strip()
            elif line.startswith('Requires:'):
                requires_text = line.replace('Requires:', '').strip()
                if requires_text:
                    requires = [r.strip() for r in requires_text.split(',')]
        
        # ライセンス情報が取得できなかった場合は、メタデータからの取得を試みる
        if not license_info:
            try:
                # pkg_resourcesを使用してメタデータから取得
                import importlib.metadata as metadata
                try:
                    dist = metadata.distribution(package_name)
                    if hasattr(dist, 'metadata') and 'License' in dist.metadata:
                        license_info = dist.metadata['License']
                    elif hasattr(dist, 'metadata') and 'Classifier' in dist.metadata:
                        # クラシファイアからライセンス情報を抽出
                        for classifier in dist.metadata.get_all('Classifier', []):
                            if classifier.startswith('License ::'):
                                license_info = classifier.split('::')[-1].strip()
                                break
                except:
                    pass
            except ImportError:
                # Python 3.8未満の場合のフォールバック
                try:
                    import pkg_resources
                    dist = pkg_resources.get_distribution(package_name)
                    if dist.has_metadata('METADATA'):
                        metadata_text = dist.get_metadata('METADATA')
                        for line in metadata_text.splitlines():
                            if line.startswith('License:'):
                                license_info = line.replace('License:', '').strip()
                                break
                    elif dist.has_metadata('PKG-INFO'):
                        metadata_text = dist.get_metadata('PKG-INFO')
                        for line in metadata_text.splitlines():
                            if line.startswith('License:'):
                                license_info = line.replace('License:', '').strip()
                                break
                except:
                    pass
            
            # それでも取得できない場合はセットアップファイルを解析する試み
            if not license_info:
                try:
                    # 代替方法: パッケージの場所を見つけてsetup.pyを探す
                    package_location = None
                    for line in output.split('\n'):
                        if line.startswith('Location:'):
                            package_location = line.replace('Location:', '').strip()
                            break
                    
                    if package_location:
                        setup_path = os.path.join(package_location, package_name, 'setup.py')
                        if os.path.exists(setup_path):
                            with open(setup_path, 'r') as f:
                                setup_content = f.read()
                                import re
                                license_match = re.search(r"license=['\"]([^'\"]+)['\"]", setup_content)
                                if license_match:
                                    license_info = license_match.group(1)
                except:
                    pass
        
        # 最終的にもライセンス情報がない場合は「Unknown」とする
        if not license_info:
            license_info = "Unknown"
        
        return version, license_info, requires
    except Exception as e:
        print(f"エラー: {e}")
        return "Unknown", "Unknown", []

def check_license(package_name):
    """パッケージのライセンスをチェックします"""
    # パッケージのインストール前にメタデータのみを取得して確認
    version, license_info, requires = get_package_info(package_name)
    allowed_licenses = load_allowed_licenses()
    
    # 正規化したライセンス名で比較
    normalized_license = normalize_license_name(license_info)
    is_allowed = False
    
    for allowed in allowed_licenses:
        if normalize_license_name(allowed) == normalized_license:
            is_allowed = True
            break
    
    # 依存パッケージの情報収集前にパッケージの情報を先に表示
    if is_allowed:
        print(f"✅ {package_name} ({version}): {license_info} - ライセンス許可")
    else:
        print(f"⚠️ 警告: {package_name} ({version}) のライセンス ({license_info}) は許可リストにありません")
    
    # 依存パッケージがある場合、情報を収集
    deps_info = []
    not_allowed_deps = []
    if requires:
        print(f"\n📦 {package_name}の依存パッケージの情報を収集しています...")
        for req in requires:
            # 依存パッケージの情報を取得
            dep_version, dep_license, _ = get_package_info(req)
            
            # ライセンスをチェック
            normalized_dep_license = normalize_license_name(dep_license)
            is_dep_allowed = False
            
            for allowed in allowed_licenses:
                if normalize_license_name(allowed) == normalized_dep_license:
                    is_dep_allowed = True
                    break
            
            status = "✅ 許可" if is_dep_allowed else "❌ 不許可"
            deps_info.append((req, dep_version, dep_license, status, is_dep_allowed))
            
            # 不許可のライセンスがある場合はリストに追加
            if not is_dep_allowed:
                not_allowed_deps.append((req, dep_version, dep_license))
        
        # 依存パッケージの情報を表示
        if deps_info:
            print(f"\n📦 {package_name}の依存パッケージとそのライセンス:")
            for dep_name, dep_version, dep_license, status, _ in deps_info:
                print(f"  - {dep_name} ({dep_version}): {dep_license} - {status}")
            
            # ライセンス不許可の依存パッケージがあるかチェック
            if not_allowed_deps:
                print("\n⚠️ 以下の依存パッケージのライセンスが許可されていません:")
                for dep_name, dep_version, dep_license in not_allowed_deps:
                    print(f"  - {dep_name} ({dep_version}): {dep_license}")
    
    # メインパッケージのライセンスが許可されていない場合は確認
    if not is_allowed:
        while True:
            user_input = input("\nインストールを続行しますか？ (y/n): ").lower()
            if user_input == 'y':
                add_to_list = input("このライセンスを許可リストに追加しますか？ (y/n): ").lower()
                if add_to_list == 'y':
                    allowed_licenses.append(license_info)
                    save_allowed_licenses(allowed_licenses)
                    print(f"ライセンス '{license_info}' を許可リストに追加しました")
                break
            elif user_input == 'n':
                print("インストールをキャンセルしました")
                return False, None, None, None
            else:
                print("'y' または 'n' を入力してください")
    
    # 依存パッケージのライセンスが不許可の場合、メインパッケージが許可されていても確認
    if not_allowed_deps:
        while True:
            continue_install = input(f"\n{package_name}と全ての依存パッケージをインストールしますか？ (y/n): ").lower()
            if continue_install == 'y':
                # 依存パッケージのライセンスも許可リストに追加するか確認
                add_deps = input("依存パッケージのライセンスも許可リストに追加しますか？ (y/n): ").lower()
                if add_deps == 'y':
                    added_count = 0
                    added_licenses = []
                    
                    # デバッグ情報：現在の許可リスト
                    print(f"現在の許可リスト: {allowed_licenses}")
                    print(f"追加対象の依存パッケージ: {len(not_allowed_deps)}個")
                    
                    # 最新の許可リストを取得
                    try:
                        # 許可リストを読み込み直す
                        current_allowed = load_allowed_licenses()
                        print(f"ファイルから読み込まれた現在の許可リスト: {current_allowed}")
                    except Exception as e:
                        print(f"現在の許可リスト読み込みエラー: {e}")
                        current_allowed = allowed_licenses.copy()
                    
                    # 依存パッケージのライセンスを直接リストに追加
                    for dep_name, dep_version, dep_license in not_allowed_deps:
                        print(f"処理中: {dep_name} - {dep_license}")
                        # まだ許可されていないライセンスのみ追加
                        if dep_license and dep_license != "Unknown":
                            if dep_license not in current_allowed and dep_license not in added_licenses:
                                added_licenses.append(dep_license)
                                added_count += 1
                                print(f"- {dep_license} を追加します（{dep_name}から）")
                    
                    # デバッグ情報：追加するライセンス
                    print(f"追加予定のライセンス: {added_licenses}")
                    
                    if added_count > 0:
                        # 新しいライセンスリストを作成
                        updated_licenses = current_allowed.copy()
                        # 未知のライセンスは追加しない
                        updated_licenses.extend([lic for lic in added_licenses if lic != "Unknown"])
                        
                        # 重複を除去
                        updated_licenses = list(set(updated_licenses))
                        
                        print(f"最終的な許可リスト: {updated_licenses}")
                        
                        # 直接save_allowed_licensesを呼び出す
                        try:
                            save_allowed_licenses(updated_licenses)
                            print(f"✅ {added_count}個の依存パッケージのライセンスを許可リストに追加しました")
                            
                            # メモリ上の変数も更新
                            allowed_licenses = updated_licenses
                        except Exception as e:
                            print(f"❌ 許可リスト更新エラー: {e}")
                    else:
                        print("追加するライセンスがありませんでした")
                break
            elif continue_install == 'n':
                print("インストールをキャンセルしました")
                return False, None, None, None
            else:
                print("'y' または 'n' を入力してください")
    
    return True, version, license_info, requires

def license_command():
    """ライセンスコマンドの実装"""
    parser = argparse.ArgumentParser(description='pip ライセンスチェッカー')
    subparsers = parser.add_subparsers(dest='command', help='コマンド')
    
    # install サブコマンド
    install_parser = subparsers.add_parser('install', help='パッケージのインストールとライセンスチェック')
    install_parser.add_argument('packages', nargs='+', help='インストールするパッケージ')
    
    # list サブコマンド
    list_parser = subparsers.add_parser('list', help='許可されたライセンスの一覧を表示')
    
    # add サブコマンド
    add_parser = subparsers.add_parser('add', help='ライセンスを許可リストに追加')
    add_parser.add_argument('license', help='追加するライセンス')
    
    # remove サブコマンド
    remove_parser = subparsers.add_parser('remove', help='ライセンスを許可リストから削除')
    remove_parser.add_argument('license', help='削除するライセンス')
    
    # check サブコマンド
    check_parser = subparsers.add_parser('check', help='指定したパッケージのライセンスをチェック')
    check_parser.add_argument('packages', nargs='+', help='チェックするパッケージ')

    # init サブコマンド
    init_parser = subparsers.add_parser('init', help='プロジェクトの初期化')
    
    # scan サブコマンド
    scan_parser = subparsers.add_parser('scan', help='既存のインストール済みパッケージをスキャンして記録')
    
    # update サブコマンド
    update_parser = subparsers.add_parser('update', help='requirements_license.txtのステータスを更新')
    
    args = parser.parse_args(sys.argv[2:])
    
    if not args.command:
        parser.print_help()
        return
    
    if args.command == 'install':
        for package in args.packages:
            print(f"📝 {package}のライセンス確認を開始します（依存パッケージも含む）")
            proceed, version, license_info, requires = check_license(package)
            if proceed:
                # 実際のインストールを実行
                print(f"🔄 {package}とその依存パッケージをインストールしています...")
                pip_install = create_command('install')
                pip_install.main([package])
                # requirements_license.txtを更新
                update_requirements_license(package, version, license_info, requires)
                print(f"📝 {package} をrequirements_license.txtに追加しました")
            else:
                print(f"⚠️ {package} のインストールをキャンセルしました")
    
        # インストール後に全パッケージのライセンスステータスを更新
        print("\n🔄 全パッケージのライセンスステータスを確認しています...")
        update_license_status()
        print("✅ ライセンスステータスを更新しました")
    elif args.command == 'list':
        allowed_licenses = load_allowed_licenses()
        if allowed_licenses:
            print("許可されたライセンス:")
            for license in allowed_licenses:
                print(f"- {license}")
        else:
            print("許可されたライセンスはありません")
    
    elif args.command == 'add':
        allowed_licenses = load_allowed_licenses()
        if args.license not in allowed_licenses:
            allowed_licenses.append(args.license)
            save_allowed_licenses(allowed_licenses)
            print(f"ライセンス '{args.license}' を許可リストに追加しました")
            # ライセンスを追加した後、requirements_license.txtを更新
            update_license_status()
        else:
            print(f"ライセンス '{args.license}' は既に許可リストに存在します")
    
    elif args.command == 'remove':
        allowed_licenses = load_allowed_licenses()
        if args.license in allowed_licenses:
            allowed_licenses.remove(args.license)
            save_allowed_licenses(allowed_licenses)
            print(f"ライセンス '{args.license}' を許可リストから削除しました")
            # ライセンスを削除した後、requirements_license.txtを更新
            update_license_status()
        else:
            print(f"ライセンス '{args.license}' は許可リストに存在しません")
    
    elif args.command == 'check':
        for package in args.packages:
            check_license(package)
    
    elif args.command == 'init':
        ensure_config_exists()
        ensure_requirements_license_exists()
        scan_installed_packages()
        
        # 最後にすべてのパッケージのライセンスステータスを確認して更新
        print("\n🔄 全パッケージのライセンスステータスを最終確認しています...")
        update_license_status()
        print("✅ プロジェクトを初期化しました")
    
    elif args.command == 'scan':
        scan_installed_packages()
        
        # スキャン後にすべてのパッケージのライセンスステータスを確認して更新
        print("\n🔄 全パッケージのライセンスステータスを確認しています...")
        update_license_status()
        print("✅ インストール済みのパッケージをスキャンしました")
    
    elif args.command == 'update':
        update_license_status()
        print("✅ ライセンスステータスを更新しました")

def scan_installed_packages():
    """インストール済みのパッケージをスキャンしてrequirements_license.txtに追加します"""
    print("インストール済みのパッケージをスキャンしています...")
    
    # 既存のrequirements_license.txtファイルがあれば読み込み、許可リストを更新
    if os.path.exists(REQUIREMENTS_LICENSE_PATH):
        with open(REQUIREMENTS_LICENSE_PATH, 'r') as f:
            lines = f.readlines()
            
        allowed_licenses = load_allowed_licenses()
        modified = False
        
        for line in lines:
            if not line.startswith('#') and '[' in line and ']' in line:
                try:
                    # ライセンス情報を抽出
                    license_start = line.find('[') + 1
                    license_end = line.find(']', license_start)
                    license_info = line[license_start:license_end].strip()
                    
                    # 許可リストに存在しない場合は追加（正規化して比較）
                    normalized_license = normalize_license_name(license_info)
                    exists = False
                    
                    for allowed in allowed_licenses:
                        if normalize_license_name(allowed) == normalized_license:
                            exists = True
                            break
                    
                    if license_info and license_info != "Unknown" and not exists:
                        allowed_licenses.append(license_info)
                        modified = True
                except:
                    pass
        
        # 許可リストが更新された場合は保存
        if modified:
            save_allowed_licenses(allowed_licenses)
            print("✅ 既存のrequirements_license.txtからライセンス情報を更新しました")
    
    # pipでインストール済みのパッケージ一覧を取得
    cmd = [sys.executable, "-m", "pip", "list", "--format=json"]
    process = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    stdout, stderr = process.communicate()
    
    try:
        installed_packages = json.loads(stdout.decode('utf-8'))
        
        # 自動的に許可リストに追加するかどうかを確認
        auto_add = input("許可リストにないライセンスを自動的に追加しますか？ (y/n): ").lower() == 'y'
        
        # 各パッケージの情報を取得して記録
        for package_info in installed_packages:
            package_name = package_info["name"]
            if package_name != "pip-license-checker":  # 自分自身は除外
                version, license_info, requires = get_package_info(package_name)
                
                # ライセンスをチェック
                allowed_licenses = load_allowed_licenses()
                if license_info not in allowed_licenses:
                    print(f"⚠️ 警告: {package_name} のライセンス ({license_info}) は許可リストにありません")
                    if auto_add:
                        allowed_licenses.append(license_info)
                        save_allowed_licenses(allowed_licenses)
                        print(f"ライセンス '{license_info}' を許可リストに追加しました")
                
                # requirements_license.txtに追加
                update_requirements_license(package_name, version, license_info, requires, True)
                print(f"📝 {package_name} をrequirements_license.txtに追加しました")
        
        print(f"✅ 合計 {len(installed_packages)-1} 個のパッケージをスキャンしました")
    
    except Exception as e:
        print(f"エラー: {e}")

def update_license_status():
    """requirements_license.txtのすべてのパッケージのライセンスステータスを再チェックして更新します"""
    if not os.path.exists(REQUIREMENTS_LICENSE_PATH):
        print("❌ requirements_license.txtが見つかりません")
        return
    
    with open(REQUIREMENTS_LICENSE_PATH, 'r') as f:
        lines = f.readlines()
    
    modified = False
    allowed_licenses = load_allowed_licenses()
    updated_lines = []
    wrong_status_count = 0
    
    for line in lines:
        if line.startswith('#') or not ('[' in line and ']' in line):
            updated_lines.append(line)
            continue
        
        try:
            # 現在のステータスを取得
            current_status = "✅" if line.startswith("✅") else "❓"
            
            # パッケージ名とライセンス情報を抽出
            parts = line.strip().split(' ', 1)
            if len(parts) < 2:
                updated_lines.append(line)
                continue
            
            rest = parts[1]
            package_info = rest.split(' [', 1)
            if len(package_info) < 2:
                updated_lines.append(line)
                continue
            
            license_part = '[' + package_info[1]
            license_end = license_part.find(']')
            if license_end == -1:
                updated_lines.append(line)
                continue
            
            license_info = license_part[1:license_end]
            
            # ライセンスが許可リストに含まれているか正規化して確認
            normalized_license = normalize_license_name(license_info)
            is_allowed = False
            
            for allowed in allowed_licenses:
                if normalize_license_name(allowed) == normalized_license:
                    is_allowed = True
                    break
            
            correct_status = "✅" if is_allowed else "❓"
            
            # ステータスが間違っている場合は修正
            if current_status != correct_status:
                new_line = line.replace(current_status, correct_status, 1)
                updated_lines.append(new_line)
                wrong_status_count += 1
                modified = True
                print(f"🔄 {package_info[0]}のステータスを{current_status}から{correct_status}に更新しました")
            else:
                updated_lines.append(line)
        
        except Exception as e:
            # 解析エラーが発生した場合は元の行をそのまま保持
            updated_lines.append(line)
    
    # 変更があった場合のみファイルを更新
    if modified:
        with open(REQUIREMENTS_LICENSE_PATH, 'w') as f:
            f.writelines(updated_lines)
        print(f"✅ {wrong_status_count}個のパッケージのステータスを更新しました")
    else:
        print("✅ すべてのパッケージのステータスは正確です")

def main():
    if len(sys.argv) > 1:
        if sys.argv[1] == 'license':
            license_command()
        elif sys.argv[1] == 'install' and len(sys.argv) > 2:
            # installコマンドを直接インターセプト
            print(f"📝 パッケージのライセンス確認を開始します（依存パッケージを含む）")
            # 引数をライセンスコマンドのinstallに渡す
            packages = sys.argv[2:]
            # sys.argvを変更
            old_argv = sys.argv.copy()
            sys.argv = [sys.argv[0], 'license', 'install'] + packages
            try:
                license_command()
            finally:
                # 元のargvを復元
                sys.argv = old_argv
        else:
            # 標準のpipコマンドにフォールバック
            from pip._internal.cli.main import main as pip_main
            return pip_main()
    else:
        # 引数なしの場合は標準のpipコマンドを実行
        from pip._internal.cli.main import main as pip_main
        return pip_main()

if __name__ == '__main__':
    main()
