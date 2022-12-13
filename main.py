import cv2
import numpy as np  
from PIL import ImageFont, ImageDraw, Image
from random import randint
import tkinter as tk
import tkinter.ttk as ttk
import tkinter.filedialog as filedialog
from PIL import Image, ImageTk
import threading
import configparser
import os
import re
import time

# グローバル変数の定義
file_path = ""
texts = "new"
simg = None
stop_flag = False
break_flag = False
button4 = None
save_dir = "./"
bg_color = "black"
font_path = './data/fonts/HGRPP1.TTC'
mainicon = "./data/icon/main.png"
configicon = "./data/icon/main.png"
frame1 = None
frame2 = None
renamedpath = ""
workflag = False
autosave = "off"

# 設定保存用関数
def save_config():
    config = configparser.ConfigParser()
    config["default"]={
        "save_dir":save_dir,
        "bg_color":bg_color,
        "font":font_path,
        "autosave":autosave
    }
    with open("./data/config.ini","w", encoding="utf-8") as fp:
        config.write(fp)

# 設定読み込み用関数
def load_config():
    global save_dir, bg_color, font_path, autosave
    config = configparser.ConfigParser()
    config_ini_path = './data/config.ini'

    # iniファイルが存在するかチェック
    if os.path.exists(config_ini_path):
        with open(config_ini_path, encoding='utf-8') as fp:
            config.read_file(fp)
            save_dir = config["default"]["save_dir"]
            bg_color = config["default"]["bg_color"]
            font_path = config["default"]["font"]
            autosave = config["default"]["autosave"]
    else:
        save_config()

# 生成画像保存用関数
def save_img():
    global save_dir, renamedpath
    paths = file_path.split("/")
    savefilename = paths[len(paths)-1].replace(".jpg",f"({texts}).jpg").replace(".png",f"({texts}).png")
    if save_dir == "./":
        sd = file_path.replace(paths[len(paths)-1],"")
    else:
        sd = save_dir
    writepath = sd+"/"+savefilename
    d_f = writepath.split("/")
    imgfilename = d_f[len(d_f)-1]
    imgdirname = writepath.replace(imgfilename,"")
    writepath = imgdirname + rename_file_num(imgdirname, imgfilename)
    renamedpath = writepath
    print(renamedpath+"に保存しました。")
    imwrite(renamedpath, simg)

# 保存ファイル名重複時用リネーム関数
def rename_file_num(dir="./", file_name = ""):
    dirlist = os.listdir(dir)
    if len(dirlist) == 0:
        return file_name
    count = 0
    tmp = file_name
    while(True):
      if os.path.isfile(dir+file_name):
        count+=1
        file_name = tmp.replace(".png",f"({count}).png")
        file_name = tmp.replace(".jpg",f"({count}).jpg")
      else:break
    return file_name

# 文字の描画、経過表示用関数
def letter_img():
    global simg, stop_flag, break_flag, font_path, workflag
    workflag = True
    alphachannel_flag = False
    if file_path.endswith(".png"):
        original = imread(file_path, cv2.IMREAD_UNCHANGED)
        alphachannel_flag = True
    else:
        original = imread(file_path)

    # 画像の配列サイズを取得
    h, w, c = original.shape
    
    # 文字の描画位置の調整用の変数
    hspace = int(h/40)
    wspace = int(w/80)
    
    # 背景の設定
    if bg_color == "img":
        if file_path.endswith(".png"):
            img = imread(file_path, cv2.IMREAD_UNCHANGED)
            alphachannel_flag = True
        else:
            img = imread(file_path)
    else:
        img = np.zeros((h+hspace,w+wspace,c),np.uint8)
        if bg_color=="white":
            img+=255

    # 表示用画像の準備
    copy_img = img.copy()
    if w > 1000 or h > 500: # 画像サイズが一定以上ならサイズを調整する
        r = ((w + h)/1500)
        #print(w//r)
        copy_img = cv2.resize(copy_img,(int(w//r), int(h//r)))

    s = (h+w)/20
    t = len(texts)

    i=0
    ii = 0
    while(True):
        if break_flag: # 終了判断
            break
        elif stop_flag: # 一時停止処理
            while(True):
                cv2.imshow("working", copy_img)
                time.sleep(0.2) # ループによる負荷を軽くするため
                cv2.waitKey(1)
                if break_flag:
                    break
                if stop_flag == False:
                    break
       
        # 文字サイズの設定(始めは大き目で徐々に小さくする。一定より小さくなったら少しだけ大きく戻す。)
        if i % 1000 == 0 and i != 0:
            s = s*0.85
            #print(s)
        if ii <= 10 and int(s) < int((h+w)/400): 
            s = int((h+w)/400)*3
            ii += 1
        size = int(s)

        # 描画座標
        x, y = randint(0, w-1),randint(0, h-1) 

        # 表示する色
        color = original[y,x] # 座標の色をoriginalから取得
        r = int(color[2])
        g = int(color[1])
        b = int(color[0])

        if alphachannel_flag:
            a = int(color[3])
        else:
            a = 0

        # 表示させる文字
        message = texts[i % t -1]

        input_font = ImageFont.truetype(font_path, size)
        img_pil = Image.fromarray(img) # 配列の各値を8bit(1byte)整数型(0～255)をPIL Imageに変換。
        draw = ImageDraw.Draw(img_pil) # drawインスタンスを生成
        position = (x, y) # テキスト表示位置
        draw.text(position, message, font = input_font, fill = (b, g, r, a) )

        img = np.array(img_pil) # PIL を配列に変換

        # 描画ズレの防止でずらした分を戻す
        copy_img = img.copy()[hspace:h+hspace, wspace:w+wspace]
        if w > 1000 or h > 500:
            r = ((w + h)/1500)
            copy_img = cv2.resize(copy_img,(int(w//r), int(h//r)))
        
        ## 表示
        cv2.imshow("working", copy_img)
        cv2.waitKey(1)
        simg = img.copy()[hspace:h+hspace, wspace:w+wspace]
        i += 1

    # 停止処理
    workflag = False
    break_flag = False
    cv2.destroyAllWindows()

# 日本語(OpenCVで扱えない)文字が入ったファイルを読み込むための関数
def imread(filename, flags=cv2.IMREAD_COLOR, dtype=np.uint8):
    try:
        n = np.fromfile(filename, dtype)
        img = cv2.imdecode(n, flags)
        return img
    except Exception as e:
        print(e)
        return None

# 日本語文字が入ったファイル名で保存するための関数
def imwrite(filename, img, params=None):
    try:
        ext = os.path.splitext(filename)[1]
        result, n = cv2.imencode(ext, img, params)
        if result:
            with open(filename, mode='w+b') as f:
                n.tofile(f)
            return True
        else:
            return False
    except Exception as e:
        print(e)
        return False

# メインウインドウ
class MainWindow(ttk.Frame):
    global file_path, button4
    file = ""
    texts = ""
    def __init__(self, app):
        super().__init__(app)
        self.pack()
        self.create_widget()

    def create_widget(self):
        global canvas
        # Widget用変数を定義
        self.filename = tk.StringVar()
        self.b4text = tk.StringVar()
        self.b4text.set("一時停止")
        self.pack(expand=1, fill=tk.BOTH)
        y1, y2, y3= 5, 250, 320
        x1, x2, x3 = 5, 45, 325
        w = 280
        label = ttk.Label(self,text="ファイル")
        label.place(x=x1,y=y1)
        
        filenameEntry = ttk.Entry(self,text="",textvariable= self.filename)
        filenameEntry.place(x=x2,y=y1, width=w)
   
        width, height = 385, 210
        canvas = tk.Canvas(self, width = width, height = height, bg="white", relief = tk.RIDGE, borderwidth="2")
        canvas.place(x=5, y=28)

        button = ttk.Button(self,text="参照",command =self.openFileDialog )
        button.place(x=x3,y=y1-2)

        label = ttk.Label(self,text="テキスト")
        label.place(x=x1,y=y2)
        
        self.txts = ttk.Entry(self,text="")
        self.txts.place(x=x2,y=y2, width=w)

        button2 = ttk.Button(self,text="開始",command = self.start)
        button2.place(x=x1,y=y3)
        
        button3 = ttk.Button(self,text="保存",command = save_img)
        button3.place(x=x1+120, y=y3)
        
        button4 = ttk.Button(self,text="",textvariable= self.b4text ,command = self.stop_work)
        button4.place(x=x1+200, y=y3) 

        button5 = ttk.Button(self,text="停止",command = self.break_work)
        button5.place(x=318, y=y3)

        button6 = ttk.Button(self,text="設定",command = self.push_config)
        button6.place(x=318, y=y3-30)


    # 画像選択ダイアログ
    def openFileDialog(self):
        global file_path
        typ = [('画像ファイル','*.jpg'),('画像ファイル','*.png'), ('すべてファイル','*')] 
        dir = 'C:\\pg'
        self.file  = filedialog.askopenfilename(filetypes = typ, initialdir = dir) 
        if self.file != "":
            self.filename.set(self.file)
            file_path=self.file
            self.drawimg()
    
    # 入力画像の表示用関数
    def drawimg(self):
        global pitimg
        width, height = 380, 200
        pitimg = Image.open(open(self.file, 'rb'))
        pitimg.thumbnail((width, height), Image.ANTIALIAS)
        w, _ = pitimg.size
        pitimg = ImageTk.PhotoImage(pitimg)
        x=int(200-(w/2))
        y=8
        canvas.create_image(x, y, image=pitimg, anchor=tk.NW)

    startbreak = False

    # 処理を開始する
    def start(self):
        global texts, stop_flag
        if workflag:
            stop_flag = True
            self.startbreak = True
            yesno = tk.messagebox.askyesno(title="確認", message="実行中の処理を停止してもよろしいですか？")
            if yesno:
                self.break_work()
                time.sleep(0.3)
            else:
                tk.messagebox.showwarning(title="警告", message="開始するには実行中の処理を停止してください。")
                stop_flag = False
                self.startbreak = False
                return
            self.startbreak = False
        texts = self.txts.get()
        if len(file_path) == 0:
            tk.messagebox.showwarning(title="警告", message="ファイルを選択してください。")
            return
        elif len(texts) == 0:
            tk.messagebox.showwarning(title="警告", message="テキストを入力してください。")
            return
        thread1 = threading.Thread(target=letter_img)
        thread1.start()
    
    # 文字の描画処理を一時停止・再開するための関数
    def stop_work(self):
        global stop_flag, texts
        if stop_flag:
            texts = self.txts.get()
            stop_flag = False
            self.b4text.set("一時停止")
            
        else:
            stop_flag = True
            self.b4text.set("再開")
    
    # 文字の描画処理を停止(終了)するための関数
    def break_work(self):
        global break_flag, stop_flag
        stop_flag = True
        yesno = False
        if workflag and not self.startbreak:
            yesno = tk.messagebox.askyesno(title="確認", message="処理を停止してもよろしいですか？")
        if yesno or self.startbreak:
            if autosave == "on":
                yesno = True
            else:
                yesno = tk.messagebox.askyesno(title="確認", message="画像を保存しますか？")
            if yesno:
                save_img()
            
            self.b4text.set("一時停止")
            break_flag = True
        stop_flag = False
    
    # 設定ウインドウの表示用関数
    def push_config(self):
        global frame2
        configapp = tk.Toplevel()
        configapp.geometry("300x150")
        configapp.resizable(width=False, height=False)
        #アイコンを指定
        configapp.iconphoto(False, tk.PhotoImage(file=configicon))
        #タイトルを指定
        configapp.title("設定")
        # モーダルにする設定
        configapp.grab_set()        # モーダルにする
        configapp.focus_set()       # フォーカスを新しいウィンドウをへ移す
        configapp.transient(self.master)   # タスクバーに表示しない

        frame2 = ConfigWindow(configapp)
        # ダイアログが閉じられるまで待つ
        app.wait_window(configapp) 
        configapp.mainloop()

# 設定ウインドウ
class ConfigWindow(ttk.Frame):
    def __init__(self, app):
        super().__init__(app)
        load_config()
        self.app = app
        self.pack()
        self.create_widget()

    # ウィジェットの配置
    def create_widget(self):
        self.dirname = tk.StringVar()
        self.dirname.set(save_dir)
        self.fontname = tk.StringVar()
        self.fontname.set(font_path)
        self.pack(expand=1, fill=tk.BOTH)
        self.combo1 = tk.StringVar()
        self.check2 = tk.BooleanVar()
        if bg_color == "black":
            self.combo1.set("黒")
        elif bg_color == "white":
            self.combo1.set("白")
        else:
            self.combo1.set("元画像")
        if autosave == "on":
            self.check2.set(True)
        else:
            self.check2.set(False)
        y1, y2, y3, y4= 5, 55, 120, 30
        x0, x1, x2, x3, x4, x5= 75, 5, 100, 225, 150, 45
        w = 180
        label = ttk.Label(self,text="保存先")
        label.place(x=x1,y=y1)
        
        filenameEntry = ttk.Entry(self,text="",textvariable= self.dirname)
        filenameEntry.place(x=x5,y=y1, width=w)
        
        button = ttk.Button(self,text="参照",command =self.save_dir_dialog)
        button.place(x=x3,y=y1-2)

        label = ttk.Label(self,text="フォント")
        label.place(x=x1,y=y4)
        
        filenameEntry = ttk.Entry(self,text="",textvariable= self.fontname)
        filenameEntry.place(x=x5,y=y4, width=w)
        
        button = ttk.Button(self,text="参照",command =self.open_font_dialog)
        button.place(x=x3,y=y4-2)

        label = ttk.Label(self,text="背景")
        label.place(x=x1,y=y2)
        module = ("黒", "白", "元画像")
        self.combobox = ttk.Combobox(self, textvariable=self.combo1, values=module, width=6)
        self.combobox.place(x=x5, y=y2)

        button2 = ttk.Button(self,text="決定",command = self.push_ok)
        button2.place(x=x0,y=y3)
        
        button3 = ttk.Button(self,text="適用",command = self.push_save)
        button3.place(x=x4, y=y3)

        button5 = ttk.Button(self,text="閉じる",command = self.push_quit)
        button5.place(x=x3, y=y3)

        button2 = ttk.Button(self,text="初期化",command = self.push_clear)
        button2.place(x=x3,y=y3-30)

        self.chk2 = ttk.Checkbutton(self, variable=self.check2, text='自動で保存する')
        self.chk2.place(x=x1, y=y3-40)

    # フォント選択ダイアログ
    def open_font_dialog(self):
        global font
        typ = [('フォント','*.ttc'),('すべてファイル','*')] 
        dir = './data/fonts/'
        self.font  = filedialog.askopenfilename(filetypes = typ, initialdir = dir) 
        if self.font != "":
            self.fontname.set(self.font)
            font=self.font
    
    # 保存先選択ダイアログ
    def save_dir_dialog(self):
        global save_dir
        dir = 'C:\\pg'
        self.dir = filedialog.askdirectory(initialdir = dir) 
        if self.dir != "":
            self.dirname.set(self.dir)
            save_dir=self.dir

    # 設定保存関数
    def push_save(self):
        global bg_color, autosave
        bg = self.combo1.get()
        if bg == "白":
            bg_color = "white"
        elif bg == "黒":
            bg_color = "black"
        else:
            bg_color = "img"
        if self.check2.get():
            autosave = "on"
        else:
            autosave = "off"
        self.fontname.set(font_path)
        self.dirname.set(save_dir)
        save_config()

    # 保存する場合
    def push_ok(self):
        self.push_save()
        self.app.destroy()
    

    # 保存しない場合
    def push_quit(self):
        self.app.destroy()

    # 初期化
    def push_clear(self):
        global save_dir, bg_color, font, autosave
        save_dir = "./"
        bg_color= "black"
        font = './data/fonts/HGRPP1.TTC'
        autosave = "off"
        self.dirname.set(save_dir)
        self.fontname.set(font)
        self.combo1.set("黒")
        self.check2.set(False)


if __name__ == "__main__":
    load_config()
    #Tkインスタンスを作成
    app  = tk.Tk()
    #画面サイズ
    app.geometry("400x350")
    app.resizable(width=False, height=False)
    #アイコンを指定
    app.iconphoto(False, tk.PhotoImage(file=mainicon))
    #タイトルを指定
    app.title("文字で画像再現ツール")

    # #フレームを作成する
    frame1 = MainWindow(app)
    # 格納したTkインスタンスのmainloopで画面を起こす
    app.mainloop()

    # 並列処理の停止フラグ
    stop_flag = True
    break_flag = True