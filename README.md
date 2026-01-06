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

## 必要条件
- Python 3.13+
- Ansible 2.9以上
- さくらのクラウドAPIキー

## ライセンス
MIT

## 作者
Tokuhiro Matsuno <tokuhirom@gmail.com>

