from flask import abort
# エラー時にユーザへhttpステータスを返すための関数
import pymysql
# MySQLに接続するためのライブラリ　
from DB import DB
# DB.pyモジュール内のDBクラスをインポート

db_pool = DB.init_db_pool()
# 初期起動時にコネクションプールを作成し接続を確立


# ユーザークラス
class User:
  @classmethod
  def create(cls, user_id, user_name, email, password, is_admin, family_id, family_name):
    # app.pyでUser.createを呼び出すことでサインアップに必要な情報をDBに登録できる
    # クラスメソッドとしてインスタンス化せずにクラス全体に関わる処理を扱う
    # clsは第一引数に渡す、クラス自身を指す特別な引数
    conn = db_pool.get_conn()
    # get_conn関数でconn（connention)をDB接続プールから取得する
    try:
      # try-except文はプログラムの実行を止めずにエラーハンドリングを行うもの
      # tryブロックにはエラー発生の可能性がある処理を記述する
        with conn.cursor() as cur:
            # コネクションからカーソル（操作用のオブジェクト）を取得する
            # cursor()メソッドで作成したカーソルをインターフェースとしてDBとやり取りを行い、SQL文を実行したり結果を取得したりする
            # withは処理の終了時にclose()と同様に閉じてくれるもので、SQL実行中にエラーが起きてもcursorを開放してconnをプールに返却する
            sql = "INSERT INTO users (user_id, user_name, email, password, is_admin, family_id, family_name) VALUES (%s, %s, %s, %s, %s, %s, %s);"
            # SQLを実行し、パラメータ(user_id, etc…)を埋め込む
            cur.execute(sql, (user_id, user_name, email, password, is_admin, family_id, family_name,))
            # データベースに変更を反映（保存）する
            conn.commit()
            # ここでデータが確定される
    except pymysql.Error as e:
      # exceptブロックにはエラー時の処理を記述する
      print(f'エラーが発生しています：{e}')
      abort(500)
      # pymysqlにエラーが起こったときに表示する内容
      # abortは冒頭のimport文にあるライブラリで、これによってによって500エラーレスポンスを返す
    finally:
      db_pool.release(conn)
      # finallyブロックにはエラー発生有無にかかわらず最後に必ず行う処理を記述する
      # releaseで使用済みのDB接続（conn）をプールに返却して、他のリクエストがその接続を再利用できるようにする

  @classmethod
  def find_by_email(cls, email):
      # app.pyでこれを呼び出すことで受け取ったemailがDBにあるかを確認してユーザ登録済みかを判断する
      conn = db_pool.get_conn()
      try:
          with conn.cursor() as cur:
              sql = "SELECT * FROM users WHERE email=%s;"
              cur.execute(sql, (email,))
              # 末尾にカンマを入れることで要素が1つでもタプルとして渡すことができる
              # SQLインジェクションを防ぐためにタプルで渡すというPythonの決まりに従ったpymysqlの仕様
              user = cur.fetchone()
              # fetchoneはSQLの実行結果からデータを1行だけ持ってくる
          return user
      except pymysql.Error as e:
         print(f'エラーが発生しています：{e}')
         abort(500)
      finally:
         db_pool.release(conn)