# Sacloud Dynamic Inventory Plugin for Ansible

このAnsible Collectionは、さくらのクラウド（Sacloud）用のダイナミックインベントリプラグインを提供します。

## 特長
- さくらのクラウドAPIを利用した動的なインベントリ取得
- Ansible Collection形式で管理・配布
- Ansible GalaxyやGitHubから直接インストール可能

## インストール方法

### 1. GitHubから直接インストール
```sh
ansible-galaxy collection install git+https://github.com/tokuhirom/ansible-collection-inventory-sacloud.git
```

### 2. requirements.ymlで指定
```yaml
collections:
  - name: git+https://github.com/tokuhirom/ansible-collection-inventory-sacloud.git
    type: git
    version: main
```

## 使い方

1. `ansible.cfg` でプラグインパスを指定する必要はありません。
2. インベントリファイル例:

```yaml
plugin: tokuhirom.sacloud.sacloud
api_token: <your_sacloud_api_token>
api_secret: <your_sacloud_api_secret>
# その他必要なパラメータ
```

3. 通常のAnsibleコマンドで利用できます。

```sh
ansible-inventory -i inventory.yml --list
```

## 必要条件
- Python 3.13+
- Ansible 2.9以上
- さくらのクラウドAPIキー

## 開発・ビルド

```sh
ansible-galaxy collection build
```

## ライセンス
MIT

## 作者
Tokuhiro Matsuno <tokuhirom@gmail.com>

