import tkinter as tk
import tkinter.ttk as ttk
import datetime as da
import calendar as ca
import pymysql
import csv
import sqlite3

WEEK = ['日', '月', '火', '水', '木', '金', '土']
WEEK_COLOUR = ['red', 'black', 'black', 'black','black', 'black', 'blue']
actions = ('学校','試験', '課題', '行事', '就活', 'アルバイト','旅行')
DB_NAME = 'user.db'

class Login:
  def __init__(self, root, main):
    root.title('ログイン画面')
    self.root = root
    self.main = main    # アプリ本体のクラスのインスタンスをセット
    self.widgets = []    # ログイン関連のウィジェットを管理するリスト
    self.create_widgets()

  #-----------------------------------------------------------------
  # ログイン画面を作成する
  #
  def create_widgets(self):
    # ユーザー名入力用のウィジェット
    self.name_label = tk.Label(self.root, text='ユーザー名')
    self.name_label.grid(row=0,column=0)
    self.widgets.append(self.name_label)
    self.name_entry = ttk.Entry(self.root)
    self.name_entry.grid(row=0, column=1)
    self.widgets.append(self.name_entry)
    # パスワード入力用のウィジェット
    self.pass_label = tk.Label(self.root, text='パスワード')
    self.pass_label.grid(row=1, column=0)
    self.widgets.append(self.pass_label)
    self.pass_entry = tk.Entry(self.root, show='*')
    self.pass_entry.grid(row=1, column=1)
    self.widgets.append(self.pass_entry)
    # ログインボタン
    self.login_button = tk.Button(self.root, text='ログイン', command=self.login)
    self.login_button.grid(row=2, column=0, columnspan=2)
    self.widgets.append(self.login_button)
    # 登録ボタン
    self.register_button = tk.Button(self.root, text='登録', command=self.register)
    self.register_button.grid(row=3, column=0, columnspan=2)
    self.widgets.append(self.register_button)
    # ウィジェット全てを中央寄せ
    self.root.grid_anchor(tk.CENTER)

  #-----------------------------------------------------------------
  # ログインを実行する
  #
  def login(self):
    # 入力された情報をEntryウィジェットから取得
    username = self.name_entry.get()
    password = self.pass_entry.get()

    if self.check(username, password):
      # ログインユーザー名を設定
      self.login_name = username
      self.success()
    else:
      self.fail()

  #-----------------------------------------------------------------
  # 入力されたユーザー情報が登録済か確認する
  #
  def check(self, username, password):
    # DB接続
    self.connection = sqlite3.connect(DB_NAME)
    self.cursor = self.connection.cursor()
    # まだDBにテーブルがなければ作成
    self.cursor.execute('CREATE TABLE IF NOT EXISTS user_info (username text, passwordtext)')
    # ユーザー情報を取得
    check = self.cursor.execute('SELECT * FROM user_info WHERE username=? and password=?', [username, password])
    # 取得したユーザー情報をリスト化
    user_list = check.fetchall()
    # ユーザー情報の有無をチェック
    if user_list:
      ret = True
    else:
      ret =False
    # DB接続をクローズ
    self.connection.close()
    # ユーザー情報が登録されているかどうかを返却
    return ret
    
  #-----------------------------------------------------------------
  # ユーザ名とパスワードを登録する
  #
  def register(self):
    # 入力された情報をEntryウィジェットから取得
    username = self.name_entry.get()
    password = self.pass_entry.get()
    
    self.save(username, password)
  
  #-----------------------------------------------------------------
  # 入力されたユーザ情報を登録する
  #
  def save(self, usarname, password):
    # DB接続
    self.connection = sqlite3.connect(DB_NAME)
    self.cursor = self.connection.cursor()
    # まだDBにテーブルがなければ作成
    self.cursor.execute('CREATE TABLE IF NOT EXISTS user_info(username text, password text)')
    # 取得した情報をDBに追記
    self.cursor.execute('INSERT INTO user_info VALUES(?, ?)', [username, password])
    # DBを保存
    self.connection.commit()
    # DB接続をクローズ
    self.connection.close()

  #-----------------------------------------------------------------
  # ログイン失敗時の処理を行う
  #
  def fail(self):
    for widget in self.widgets:
      widget.destroy()

    self.message = tk.Label(self.root,
                            text='ログインに失敗しました',
                            font=('',12))
    self.message.place(x=self.root.winfo_width() // 2,
                       y=self.root.winfo_height() // 2,
                       anchor=tk.CENTER)

    self.root.after(1000, self.redisplay)
  
  #-----------------------------------------------------------------
  # ログイン画面を再度表示する
  #
  def redisplay(self):
    self.message.destroy()
    self.create_widgets()

  #-----------------------------------------------------------------
  # ログイン成功時の処理を実行する
  #
  def success(self):
    for widget in self.widgets:
      widget.destroy()

    self.message = tk.Label(self.root, 
                            text='ログインに成功しました',
                            font=("",12))
    self.message.place(x=self.root.winfo_width() // 2,
                       y=self.root.winfo_height() // 2,
                       anchor=tk.CENTER)

    self.root.after(1000, self.main_start)
  
  #-----------------------------------------------------------------
  # アプリ本体を起動する
  #
  def main_start(self):
    self.message.destroy()

    self.main.start(self.login_name)

class YicDiary:    # カレンダーアプリ
  def __init__(self, root):
    root.title('予定管理アプリ')
    self.root = root

  #-----------------------------------------------------------------
  # アプリを起動する
  #
  def start(self, login_name):
    self.login_name = login_name

    self.root.resizable(0, 0)
    self.root.grid_columnconfigure((0, 1), weight=1)
    self.sub_win = None

    self.year  = da.date.today().year
    self.mon = da.date.today().month
    self.today = da.date.today().day

    self.title_A = None
    self.title_B = None
    self.title_C = None

    # 左上側のカレンダー部分
    self.upperleftFrame = tk.Frame(self.root)
    self.upperleftFrame.grid(row=0, column=0)
    self.upperleftBuild()

    # 右上側のログインユーザーの予定管理部分
    self.upperrightFrame = tk.Frame(self.root)
    self.upperrightFrame.grid(row=0, column=1)
    self.upperrightBuild()

    # 左下側のログイン名表記部分
    self.lowerleftFrame = tk.Frame(self.root)
    self.lowerleftFrame.grid(row=1, column=0)
    self.lowerleftBuild()

    # 右下側のその他の予定管理部分
    self.lowerrightFrame = tk.Frame(self.root)
    self.lowerrightFrame.grid(row=1, column=1)
    self.lowerrightBuild()

  #-----------------------------------------------------------------
  # アプリの左上側の領域を作成する
  #
  # leftFrame: 左側のフレーム
  def upperleftBuild(self):
    self.viewLabel = tk.Label(self.upperleftFrame, font=('', 10))
    self.beforButton = tk.Button(self.upperleftFrame, text='＜', font=('', 10), command=lambda:self.disp(-1))
    self.nextButton = tk.Button(self.upperleftFrame, text='＞', font=('', 10), command=lambda:self.disp(1))

    self.viewLabel.grid(row=0, column=1, pady=10, padx=10)
    self.beforButton.grid(row=0, column=0, pady=10, padx=10)
    self.nextButton.grid(row=0, column=2, pady=10, padx=10)

    self.calendar = tk.Frame(self.upperleftFrame)
    self.calendar.grid(row=1, column=0, columnspan=3)
    self.disp(0)

  #-----------------------------------------------------------------
  # アプリの左下側の領域を作成する。
  #
  # lowerleftFrame: 左下側のフレーム
  def lowerleftBuild(self):
    self.login_now = tk.Label(self.lowerleftFrame, text='ログイン名: ' + self.login_name, font=('', 10))
    self.login_now.grid(row=0, column=0, pady=15, padx=15)

  #-----------------------------------------------------------------
  # アプリの右上側の領域を作成する
  #
  # upperrightFrame: 右上側のフレーム
  def upperrightBuild(self):
    self.r1_frame = tk.Frame(self.upperrightFrame)
    self.r1_frame.grid(row=0, column=0, pady=10)

    temp_A = '{}年{}月{}日の予定'.format(self.year, self.mon, self.today)
    self.title_A = tk.Label(self.r1_frame, text=temp_A, font=('', 12))
    self.title_A.grid(row=0, column=0, padx=20)

    self.button = tk.Button(self.upperrightFrame, text='追加', command=lambda:self.add())
    self.button.grid(row=0, column=1)

    self.r2_frame = tk.Frame(self.upperrightFrame)
    self.r2_frame.grid(row=1, column=0)

    self.schedule_1()

  #-----------------------------------------------------------------
  # アプリの右上側の領域にログインユーザーの予定を表示する
  #
  def schedule_1(self):
    schedule = None
    kind = None
    # ウィジットを廃棄
    for widget in self.r2_frame.winfo_children():
      widget.destroy()

    # データベースに予定の問い合わせを行う
    connection = pymysql.connect(host='127.0.0.1',
                                 user='root',
                                 password='',
                                 db='apr01',
                                 charset='utf8mb4',
                                 cursorclass=pymysql.cursors.DictCursor)

    with connection.cursor() as cursor:
      cursor = connection.cursor()

      days = '{}-{}-{}'.format(self.year, self.mon, self.today)
      names = self.login_name

      sql_schedule = '''SELECT S.Dates Dates, S.User_Name User_Name,
                        K.Kind_Name Kind_Name, S.Schedule_Contents Schedule FROM Schedule_2 S 
                        INNER JOIN Kinds K ON S.KindID = K.KindID 
                        WHERE Dates = %s AND User_Name = %s'''
      cursor.execute(sql_schedule, [days, names])

      for fetched_line in cursor.fetchall():
        schedule = fetched_line['Schedule']
        kind = fetched_line['Kind_Name']

      temp_B = '名前: {}'.format(names)
      temp_C = '種別: {}'.format(kind)
      temp_D = '予定: {}'.format(schedule)
      self.title_B = tk.Label(self.r2_frame, text=temp_B, font=('', 10))
      self.title_B.grid(row=1, column=0, padx=10)
      self.title_C = tk.Label(self.r2_frame, text=temp_C, font=('', 10))
      self.title_C.grid(row=2, column=0, padx=10)
      self.title_D = tk.Label(self.r2_frame, text=temp_D, font=('', 10))
      self.title_D.grid(row=3, column=0, padx=10)

  #-----------------------------------------------------------------
  # アプリの右下側の領域を作成する
  #
  # lowerrightFrame: 右下側のフレーム
  def lowerrightBuild(self):
    self.r3_frame = tk.Frame(self.lowerrightFrame)
    self.r3_frame.grid(row=0, column=0, pady=10)

    temp_E = 'その他のユーザーの予定'
    self.title_E = tk.Label(self.r3_frame, text=temp_E, font=('', 12))
    self.title_E.grid(row=0, column=0, padx=20)

    self.r4_frame = tk.Frame(self.lowerrightFrame)
    self.r4_frame.grid(row=1, column=0)

    self.schedule_2()

  #-----------------------------------------------------------------
  # アプリの右下側の領域にその他のユーザーの予定を表示する。
  #
  def schedule_2(self):
    schedule = None
    kind = None
    # ウィジットを廃棄
    for widget in self.r4_frame.winfo_children():
      widget.destroy()

    # データベースに予定の問い合わせを行う
    connection = pymysql.connect(host='127.0.0.1',
                                 user='root',
                                 password='',
                                 db='apr01',
                                 charset='utf8mb4',
                                 cursorclass=pymysql.cursors.DictCursor)

    with connection.cursor() as cursor:
      cursor = connection.cursor()

      days = '{}-{}-{}'.format(self.year, self.mon, self.today)
      names = self.login_name

      sql_schedule = '''SELECT S.Dates Dates, S.User_Name User_Name,
                        K.Kind_Name Kind_Name, S.Schedule_Contents Schedule FROM Schedule_2 S 
                        INNER JOIN Kinds K ON S.KindID = K.KindID 
                        WHERE Dates = %s AND User_Name != %s'''
      cursor.execute(sql_schedule, [days, names])

      for fetched_line in cursor.fetchall():
        names = fetched_line['User_Name']
        schedule = fetched_line['Schedule']
        kind = fetched_line['Kind_Name']

      if names == self.login_name:
        names = None

      temp_F = '名前: {}'.format(names)
      temp_G = '種別: {}'.format(kind)
      temp_H = '予定: {}'.format(schedule)
      self.title_F = tk.Label(self.r4_frame, text=temp_F, font=('', 10))
      self.title_F.grid(row=1, column=0, padx=10)
      self.title_G = tk.Label(self.r4_frame, text=temp_G, font=('', 10))
      self.title_G.grid(row=2, column=0, padx=10)
      self.title_H = tk.Label(self.r4_frame, text=temp_H, font=('', 10))
      self.title_H.grid(row=3, column=0, padx=10)

  #-----------------------------------------------------------------
  # カレンダーを表示する
  #
  # argv: -1 = 前月
  #        0 = 今月（起動時のみ）
  #        1 = 次月
  def disp(self, argv):
    self.mon = self.mon + argv
    if self.mon < 1:
      self.mon, self.year = 12, self.year - 1
    elif self.mon > 12:
      self.mon, self.year = 1, self.year + 1

    self.viewLabel['text'] = '{}年{}月'.format(self.year, self.mon)

    cal = ca.Calendar(firstweekday=6)
    cal = cal.monthdayscalendar(self.year, self.mon)

    # ウィジットを廃棄
    for widget in self.calendar.winfo_children():
      widget.destroy()

    # 見出し行
    r = 0
    for i, x in enumerate(WEEK):
      label_day = tk.Label(self.calendar, text=x, font=('', 10), width=3, fg=WEEK_COLOUR[i])
      label_day.grid(row=r, column=i, pady=1)

    # カレンダー本体
    r = 1
    for week in cal:
      for i, day in enumerate(week):
        if day == 0: day = ' ' 
        label_day = tk.Label(self.calendar, text=day, font=('', 10), fg=WEEK_COLOUR[i], borderwidth=1)
        if (da.date.today().year, da.date.today().month, da.date.today().day) == (self.year, self.mon, day):
          label_day['relief'] = 'solid'
        label_day.bind('<Button-1>', self.click)
        label_day.grid(row=r, column=i, padx=2, pady=1)
      r = r + 1

    # 画面右側の表示を変更
    if self.title_A is not None:
      self.today = 1
      self.title_A['text'] = '{}年{}月{}日の予定'.format(self.year, self.mon, self.today)


  #-----------------------------------------------------------------
  # 予定を追加したときに呼び出されるメソッド
  #
  def add(self):
    if self.sub_win == None or not self.sub_win.winfo_exists():
      self.sub_win = tk.Toplevel()
      self.sub_win.geometry("300x300")
      self.sub_win.resizable(0, 0)

      # ラベル
      sb1_frame = tk.Frame(self.sub_win)
      sb1_frame.grid(row=0, column=0)
      temp = '{}年{}月{}日　追加する予定'.format(self.year, self.mon, self.today)
      title = tk.Label(sb1_frame, text=temp, font=('', 12))
      title.grid(row=0, column=0)

      # 予定種別（コンボボックス）
      sb2_frame = tk.Frame(self.sub_win)
      sb2_frame.grid(row=1, column=0)
      label_1 = tk.Label(sb2_frame, text='種別 : 　', font=('', 10))
      label_1.grid(row=0, column=0, sticky=tk.W)
      self.combo = ttk.Combobox(sb2_frame, state='readonly', values=actions)
      self.combo.current(0)
      self.combo.grid(row=0, column=1)

      # テキストエリア（垂直スクロール付）
      sb3_frame = tk.Frame(self.sub_win)
      sb3_frame.grid(row=2, column=0)
      self.text = tk.Text(sb3_frame, width=40, height=15)
      self.text.grid(row=0, column=0)
      scroll_v = tk.Scrollbar(sb3_frame, orient=tk.VERTICAL, command=self.text.yview)
      scroll_v.grid(row=0, column=1, sticky=tk.N+tk.S)
      self.text["yscrollcommand"] = scroll_v.set

      # 保存ボタン
      sb4_frame = tk.Frame(self.sub_win)
      sb4_frame.grid(row=3, column=0, sticky=tk.NE)
      button = tk.Button(sb4_frame, text='保存', command=lambda:self.done())
      button.pack(padx=10, pady=10)
    elif self.sub_win != None and self.sub_win.winfo_exists():
      self.sub_win.lift()


  #-----------------------------------------------------------------
  # 予定追加ウィンドウで「保存」を押したときに呼び出されるメソッド
  #
  def done(self):
    # 名前
    names = self.login_name

    # 日付
    days = '{}-{}-{}'.format(self.year, self.mon, self.today)
    print(days)

    # 種別
    kinds = self.combo.get()
    print(kinds)

    # 予定詳細
    memo = self.text.get("1.0", "end")
    print(memo)

    # データベースに新規予定を挿入する
    connection = pymysql.connect(host='127.0.0.1',
                                 user='root',
                                 password='',
                                 db='apr01',
                                 charset='utf8mb4',
                                 cursorclass=pymysql.cursors.DictCursor)
  
    try:
      # トランザクション開始
      connection.begin()

      with connection.cursor() as cursor:
        cursor = connection.cursor()

        sql_1 = 'SELECT KindID FROM Kinds WHERE Kind_Name = %s'
        cursor.execute(sql_1,[kinds])
        for fetched_line in cursor.fetchall():
          kindsID = fetched_line['KindID']

        sql_2 = 'INSERT INTO Schedule_2(User_Name, Dates, KindID, Schedule_Contents) VALUES(%s, %s, %s, %s)'
        cursor.execute(sql_2,[names, days, kindsID, memo])

        sql_3 = 'SELECT * FROM Schedule_2'
        cursor.execute(sql_3)

        results = cursor.fetchall()
        for i, row in enumerate (results):
          print(i, row)

      connection.commit()

    except Exception as e:
      print('error:', e)
      connection.rollback()
    finally:
      connection.close()
    
    self.sub_win.destroy()

  #-----------------------------------------------------------------
  # 日付をクリックした際に呼びだされるメソッド（コールバック関数）
  #
  # event: 左クリックイベント <Button-1>
  def click(self, event):
    day = event.widget['text']
    if day != ' ':
      self.title_A['text'] = '{}年{}月{}日の予定'.format(self.year, self.mon, day)
      self.today = day
    self.schedule_1()
    self.schedule_2()

def Main():
  root = tk.Tk()
  root.geometry('520x280')
  main = YicDiary(root)
  login = Login(root, main)
  root.mainloop()

if __name__ == '__main__':
  Main()
