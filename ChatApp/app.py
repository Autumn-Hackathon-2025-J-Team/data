from flask import Flask, session, redirect, render_template, url_for
import uuid
import os
from models import User

app = Flask(__name__)
app.secret_key = os.getenv('SECRET_KEY', uuid.uuid4().hex)
# uuid4はuuidモジュールのバージョン4で、16バイト(hex)の乱数のUUIDを生成してくれる

# トップページの処理
@app.route('/', methods=['GET'])
def index():
  user_id = session.get('user_id')
  if user_id is None:
    return render_template('index.html')
  return redirect(url_for(messages_view))


if __name__ == '__main__':
    app.run(host="0.0.0.0", debug=True)
# if __name__ == '__main__'という条件式は、他モジュールからのimportではなく、ファイルがスクリプトとして直接実行された場合にのみTrueとなる
# trueの場合にだけ実行したいコードをこの条件式の中に記述する
# ここではapp.run()、つまりアプリを立ち上げてFlask開発用サーバーを起動することを指定している