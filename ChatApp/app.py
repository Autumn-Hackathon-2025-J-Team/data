from flask import Flask, session, render_template, redirect, url_for, request, flash
from datetime import timedelta, datetime
import uuid
import os
import re
import hashlib

from models import User, Message, Histories

# 定数定義
EMAIL_PATTERN = r"^[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+$"
# メールアドレスの形式が正しいか判定するための正規表現
# ^（文字列の先頭）と$（文字列の末尾）で、指定する形式を囲む
SESSION_DAYS = 30

app = Flask(__name__)
app.secret_key = os.getenv('SECRET_KEY', uuid.uuid4().hex)
# secret_keyはセッション情報（Cookie）を暗号化する際に使用する秘密鍵
# 第二引数は環境変数が存在しないときに返すデフォルト値で、uuid4はuuidモジュールのバージョン4で、16バイト(hex)の乱数を生成してくれる
app.permanent_session_lifetime = timedelta(days=SESSION_DAYS)


# トップページの処理
@app.route('/', methods=['GET'])
def index():
  user_id = session.get('user_id')
  family_id = session.get('family_id')

#   if user_id is None: 
  return render_template('index.html')
#   return redirect(url_for('messages_view', family_id=family_id))
# ↑開発中のみmessages_viewへのリダイレクトをコメントアウト！


# サインアップページの表示：管理者ユーザ
@app.route('/signup', methods=['GET'])
def signup_view():
   return render_template('signup.html')


# サインアップ処理：管理者ユーザ
@app.route('/signup', methods=['POST'])
def signup_process():
    user_name = request.form.get('user_name')
    email = request.form.get('email')
    password = request.form.get('password')
    family_name = request.form.get('family_name')

    if user_name == '' or email == '' or password == '' or family_name == '':
        flash('空のフォームがあります')
    elif re.match(EMAIL_PATTERN, email)is None:
        flash('メールアドレスの形式が正しくありません')
        # reはPython標準ライブラリの正規表現モジュールで、文字列の検索や置換などを行う
        # match関数は文字列の先頭からパターンに一致する部分を検索して、一致すればマッチオブジェクト（情報）を、しなければNoneを返す
        # つまり入力されたメールアドレスが正規表現に一致するかを確認し、None（不一致）ならフラッシュメッセージを表示する
    else:
        user_id = uuid.uuid4()
        family_id = uuid.uuid4()
        password = hashlib.sha256(password.encode('utf-8')).hexdigest()
        # hashlibはPython標準ライブラリのハッシュ関数を扱うためのモジュール
        # sha256というハッシュアルゴリズムを利用して、入力値をutf-8エンコードして、16進数の文字列を取得するのがhexdigest
        # つまりユーザ入力値のパスワードをハッシュ化してpassword変数に格納する
        # ログイン時はpassword変数のハッシュ値と照合するため、ログイン処理も同じ方法でパスワードをハッシュ化する必要がある
        registered_user = User.find_by_email(email)
        # email値がDBにすでにあるかチェックする

        if registered_user != None:
           flash('そのメールアドレスは既に登録されています')
        else:
            User.create(user_id, user_name, email, password, True, family_id, family_name)
            UserID = str(user_id)
            FamilyID = str(family_id)
            # idをstring型にしてからセッションに保持
            session['user_id'] = UserID
            session['family_id'] = FamilyID
            session['family_name'] = family_name
            session['user_name'] = user_name
            session['is_admin'] = True
            return redirect(url_for('signup_complete_view'))
    return redirect(url_for('signup_process'))


# サインアップページの表示：家族ユーザ
@app.route('/signup/family',methods=['GET'] )
def signup_family_view():
    user_id = session.get('user_id')
    is_admin = session.get('is_admin')
    family_id =session.get('family_id')

    if user_id is None:
        flash('ログインしてください')
        return redirect(url_for('login_view'))

    if not is_admin:
        # flash('管理者ユーザーのみ利用可能な機能です')
        return redirect(url_for('messages_view', family_id=family_id))
    return render_template('signup_family.html')


# サインアップ処理：家族ユーザ
@app.route('/signup/family', methods=['POST'])
def signup_family_process():
    user_name = request.form.get('user_name')
    email = request.form.get('email')
    password = request.form.get('password')
    family_id = session.get('family_id') # 管理者ユーザのfamily_idを取得する
    family_name = session.get('family_name') # 管理者ユーザのfamily_nameを取得する

    if user_name == '' or email == '' or password == '':
        flash('空のフォームがあります')
    elif re.match(EMAIL_PATTERN, email)is None:
        flash('メールアドレスの形式が正しくありません')
    else:
        user_id = uuid.uuid4()
        password = hashlib.sha256(password.encode('utf-8')).hexdigest()
        registered_user = User.find_by_email(email)

        if registered_user != None:
           flash('そのメールアドレスは既に登録されています')
        else:
            User.create(user_id, user_name, email, password, False, family_id, family_name)

            return redirect(url_for('signup_complete_view', family_id=family_id))
    return redirect(url_for('signup_family_process'))


# サインアップ完了画面
@app.route('/signup/complete', methods=['GET'])
def signup_complete_view():
    user_id = session.get('user_id')
    family_id = session.get('family_id')

    if user_id is None:
        flash('ログインしてください')
        return redirect(url_for('login_view')) 
    return render_template('signup_complete.html', family_id=family_id)


# ログインページの表示
@app.route('/login', methods=['GET'])
def login_view():
    return render_template('login.html')

# ログイン処理
@app.route('/login',methods=['POST'])
def login_process():
    email = request.form.get('email')
    password = request.form.get('password')
    
    if email == '' or password == '':
        flash('空のフォームがあるようです')
    else:
        user = User.find_by_email(email)
        if user is None:
            flash('このユーザーは存在しません')
        else:
            hashPassword = hashlib.sha256(password.encode('utf-8')).hexdigest()
            if hashPassword != user["password"]:
                flash('パスワードが間違っています！')
            else:
                session['user_id'] = user["id"]
                session['user_name'] = user["user_name"]
                session['family_id'] = user["family_id"]
                session['family_name'] = user["family_name"]
                session['is_admin'] = bool(user["is_admin"])
                family_id = session.get('family_id')

                return redirect(url_for('messages_view', family_id=family_id))
#                return redirect('/{family_id}/messages'.format(family_id = family_id))
#                return redirect('/{family_id}/messages'.format(family_id = family_id))
#                return render_template('chat_top.html', family_id=family_id)
#                return redirect(url_for('messages_view', family_id=family_id))
                          
    return redirect(url_for('login_view'))

# ログアウト
@app.route('/logout')
def logout():
    session.clear()
    flash ('ログアウトしました')
    return redirect(url_for('login_view'))

# メッセージの投稿
@app.route('/<family_id>/messages', methods=['POST'])
def create_message(family_id):
    use_id = session.get('user_id')

    # ユーザーidが取得できない場合はログイン画面へ遷移
    if use_id is None:
        return redirect(url_for('login_view'))
    
    message = request.form.get('message')

    if message:
        Message.create(use_id, message)

    return redirect('/{family_id}/messages'.format(family_id = family_id))

# チャットルーム内（同じ家族idの人が投稿したメッセージをすべて表示）
@app.route('/<family_id>/messages', methods=['GET'])
def messages_view(family_id):
    user_id = session.get('user_id')

    # ユーザーidが取得できない場合はログイン画面へ遷移
    if user_id is None:
        flash('ログインしてください')
        return redirect(url_for('login_view'))

    #セッション情報をすべてuserへ入れる
#   user = dict(session)

    user_id = session.get('user_id')
    user_name = session.get('user_name')
    family_name = session.get('family_name')
    is_admin = session.get('is_admin')


    #チャットルームに表示するメッセージをすべて取得    
    messages = Message.get_all(family_id)

    return render_template('chat_top.html',family_id=family_id, family_name=family_name, user_id=user_id, user_name=user_name, messages=messages, is_admin=is_admin)
    
# ごはん決定画面の表示
@app.route('/<family_id>/messages/decide', methods=['GET'])
def decide_view(family_id):
    is_admin = session.get('is_admin')

    # 権限がない場合はメッセージ一覧画面に遷移
    if not is_admin:
        return redirect('{family_id}/messages'.format(family_id = family_id))

    return render_template('decide.html',family_id=family_id)

# ごはん決定処理
"""
@app.route('/<family_id>/decide', method=['POST'])
def decide_menu(family_id):
    is_admin = session.get('is_admin')
    
    # 権限がない場合はメッセージ一覧画面に遷移
    if not is_admin:
        return redirect('{family_id}/messages'.format(family_id = family_id))
    menu = request.form.get('menu')
    user_id = session.get('user_id')
    family_name = session.get('family_name')
    messages = f'今日のご飯は{menu}に決定！'
    Message.create(user_id, messages)
    Histories.create(user_id, menu)

    return render_template('chat_top.html', family_id = family_id, family_name = family_name)

"""


# ごはん履歴画面の表示
@app.route('/<family_id>/messages/history', methods=['GET'])
def history_view(family_id):
    user_id = session.get('user_id')
    family_name = session.get('family_name')
    session_family_id = session.get('family_id')

    if user_id is None:
        flash('ログインしてください')
        return redirect(url_for('login_view'))
    
    if family_id != session_family_id:
        return redirect(url_for('messages_view', family_id=family_id))
    
    histories = Histories.get_all(session_family_id)
    WEEKDAYS = ["月","火","水","木","金","土","日"]

    return render_template('history.html', family_id=family_id, histories=histories, family_name=family_name, WEEKDAYS=WEEKDAYS)


# ごはんルーレット画面の表示
"""
@app.route('/<family_id>/messages/roulette', methods=['GET'])
def roulette_view(family_id):
    user_id = session.get('user_id')
    family_id = session.get('family_id')

    if user_id is None:
        return redirect(url_for('login_view'))
    return render_template('roulette.html', family_id=family_id)

"""
    

if __name__ == '__main__':
    app.run(host="0.0.0.0", debug=True)
# if __name__ == '__main__'という条件式は、他モジュールからのimportではなく、ファイルがスクリプトとして直接実行された場合にのみTrueとなる
# trueの場合にだけ実行したいコードをこの条件式の中に記述する
# ここではapp.run()、つまりアプリを立ち上げてFlask開発用サーバーを起動することを指定している