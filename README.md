# Sacloud Dynamic Inventory Plugin for Ansible

このAnsible Collectionは、さくらのクラウド（Sacloud）用のダイナミックインベントリプラグインを提供します。

## 特長

- さくらのクラウドAPIを利用した動的なインベントリ取得
- Ansible Collection形式で管理・配布
- Ansible GalaxyやGitHubから直接インストール可能

## インストール方法

requirements.yml に以下のように記述します｡

```yaml
collections:
  - name: https://github.com/tokuhirom/ansible-collection-inventory-sacloud/releases/download/v0.0.5/tokuhirom-sacloud-0.0.5.tar.gz
```

以下のコマンドを実行してインストールします｡

```shell
ansible-galaxy collection install -r requirements.yml
```

## 使い方

インベントリファイルを以下のように記述します｡`inventory.sacloud.yml` のように､`sacloud.yml` でファイル名は終わる必要があります｡

```yaml
plugin: tokuhirom.sacloud.sacloud
api_token: <your_sacloud_api_token>
api_secret: <your_sacloud_api_secret>
zones:
  - tk1b
```

YAML ファイルで設定されていない場合､トークンは環境変数 `SAKURA_ACCESS_TOKEN` と `SAKURA_ACCESS_TOKEN_SECRET` から取得されます｡

通常のAnsibleコマンドで利用できます。

```sh
ansible-inventory -i inventory.yml --list -y
ansible-playbook -i inventory.sacloud.yml ping.yml
```

## 設定オプション

### 必須パラメータ

#### `access_token`
- さくらのクラウドAPIのアクセストークン
- 環境変数 `SAKURA_ACCESS_TOKEN` でも指定可能

#### `access_token_secret`
- さくらのクラウドAPIのアクセストークンシークレット
- 環境変数 `SAKURA_ACCESS_TOKEN_SECRET` でも指定可能

#### `zones`
- インベントリを取得するゾーンのリスト
- 例: `["tk1b", "is1a"]`

### オプションパラメータ

#### `url`
- さくらのクラウドAPIのベースURL
- デフォルト: `https://secure.sakura.ad.jp/cloud/zone`
- 環境変数 `SAKURA_API_ROOT_URL` でも指定可能

#### `skip_group_tags`
- グループを作成しないタグのリスト
- デフォルト: `["@auto-reboot", "__with_sacloud_inventory"]`
- サーバーに付与されているタグは自動的にAnsibleのグループとして作成されますが、このリストに含まれるタグはグループ化されません

### Constructed機能

Ansibleの[Constructed Inventory機能](https://docs.ansible.com/ansible/latest/inventory_guide/intro_dynamic_inventory.html#constructed-inventory)を利用できます。

#### `compose`
ホスト変数を動的に生成します。例えば、`ansible_host` を上書きして接続先IPアドレスを制御できます。

```yaml
plugin: tokuhirom.sacloud.sacloud
zones:
  - tk1b
compose:
  # ホスト名が 'fumidai.' で始まる場合は1番目のIPアドレスを使用、それ以外は2番目を使用
  ansible_host: user_ip_address[0] if inventory_hostname.startswith('fumidai.') else user_ip_address[1]
```

利用可能なホスト変数:
- `ip_address`: インターフェースのIPアドレスのリスト
- `user_ip_address`: ユーザーIPアドレスのリスト
- `zone`: サーバーが存在するゾーン（例: "tk1b", "is1a"）
- `inventory_hostname`: ホスト名（サーバー名）

#### `groups`
条件に基づいてホストをグループに追加します。

```yaml
plugin: tokuhirom.sacloud.sacloud
zones:
  - tk1b
groups:
  # user_ip_address が存在するホストを 'has_user_ip' グループに追加
  has_user_ip: user_ip_address | length > 0
```

#### `keyed_groups`
変数の値に基づいてグループを作成します。

```yaml
plugin: tokuhirom.sacloud.sacloud
zones:
  - tk1b
keyed_groups:
  # ゾーンごとにグループを作成
  - key: zone
    prefix: zone
```

### 設定例

完全な設定例:

```yaml
plugin: tokuhirom.sacloud.sacloud
access_token: your_access_token
access_token_secret: your_access_token_secret
zones:
  - tk1b
  - is1a
skip_group_tags:
  - "@auto-reboot"
  - "__with_sacloud_inventory"
  - "internal-use-only"
compose:
  ansible_host: user_ip_address[0] if user_ip_address else ip_address[0]
groups:
  production: inventory_hostname.endswith('.prod')
  staging: inventory_hostname.endswith('.stg')
```

## 必要条件
- Python 3.13+
- Ansible 2.9以上
- さくらのクラウドAPIキー

## ライセンス
MIT

## 作者
Tokuhiro Matsuno <tokuhirom@gmail.com>

