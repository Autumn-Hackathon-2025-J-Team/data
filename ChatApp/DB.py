import os
# OS機能を操作するための標準ライブラリ　環境変数を取得するために使う
import pymysql
# MySQLに接続するためのライブラリ　
from pymysqlpool.pool import Pool
# コネクションプール(あらかじめ作る接続)でDB接続を効率的に管理するためのクラス


class DB:
# DB接続関連の処理をまとめる、DBというクラスをつくる
   @classmethod
   # @classmethodはメソッドをクラスメソッドとして定義するためのデコレータ（特別な仕組み）
   # クラスメソッドは、インスタンス化せずにクラス全体で共通の処理や設定を扱うためのメソッド
   # 第一引数にはインスタンス(self)ではなくクラス自身(cls)が渡される
   def init_db_pool(cls):
   # DB接続プールを作成するクラスメソッド
       pool = Pool(
       # Poolクラスをインスタンス化して、接続条件をまとめて指定する
           # os.getenv() は環境変数の値を取得する関数
           # メリット① パスワード等をコードに直書きせずに済み、セキュリティ性が向上する
           # メリット② 環境ごとに設定を切り替えやすくなる
           # 実際の値は .env に記述するが .gitignore によってリポジトリには含まれない
           # Docker compose が.envを読み込み、環境変数として扱われる
           
           host=os.getenv('DB_HOST'),
           # データベースサーバーホスト
           user=os.getenv('DB_USER'),
           # データベースユーザー
           password=os.getenv('DB_PASSWORD'),
           # データベースパスワード  
           database=os.getenv('DB_DATABASE'),
           # データベース名
           max_size=5,
           # 最大コネクション数
           charset="utf8mb4",
           # 文字コード
           cursorclass=pymysql.cursors.DictCursor
           # カーソルクラス（辞書型でフェッチ）
           # 引数cursorclassにDictCursorを指定すると、結果を辞書形式で返す
           # カーソルとは、DBにSQLを渡して結果を受け取るオブジェクトで、DictCursorは辞書形式で結果を返すカーソル
           # 辞書型にすることでキー(カラム名)と値がセットになり、可読性向上とテーブル変更に強くなる
       )
       pool.init()
       # コネクションプールの初期化
       # init()を呼ぶことでプールを準備して使える状態にする
       return pool
       # 準備したプールオブジェクトを呼び出し元(アプリ側)に返し、DB接続で使えるようにする