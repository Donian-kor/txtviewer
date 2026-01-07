import tkinter as tk
from tkinter import filedialog, font, colorchooser, ttk
import os, json
import chardet

search_results = []
current_index = -1
current_folder = ""

# 현재 실행 중인 pyw 파일과 같은 폴더에 settings.json 저장
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
SETTINGS_FILE = os.path.join(BASE_DIR, "settings.json")

# ---------------- 설정 저장/불러오기 ----------------
def save_settings(font_name, font_size, bg_color, fg_color, last_folder=None, last_file=None):
    settings = {
        "font_name": font_name,
        "font_size": font_size,
        "bg_color": bg_color,
        "fg_color": fg_color,
        "last_folder": last_folder,
        "last_file": last_file
    }
    with open(SETTINGS_FILE, "w", encoding="utf-8") as f:
        json.dump(settings, f)

def load_settings():
    global current_folder
    try:
        with open(SETTINGS_FILE, "r", encoding="utf-8") as f:
            settings = json.load(f)
        text_area.config(
            font=(settings["font_name"], int(settings["font_size"])),
            bg=settings["bg_color"],
            fg=settings["fg_color"]
        )
        # 마지막 폴더 자동 불러오기
        if settings.get("last_folder") and os.path.isdir(settings["last_folder"]):
            current_folder = settings["last_folder"]
            file_list.delete(0, tk.END)
            for f in os.listdir(current_folder):
                if f.lower().endswith(".txt"):
                    file_list.insert(tk.END, f)
            # 마지막 파일 자동 열기
            if settings.get("last_file"):
                filepath = os.path.join(current_folder, settings["last_file"])
                if os.path.isfile(filepath):
                    try:
                        idx = list(os.listdir(current_folder)).index(settings["last_file"])
                        file_list.selection_set(idx)
                    except ValueError:
                        pass
                    show_content(None)
    except FileNotFoundError:
        pass

# ---------------- 파일 불러오기 ----------------
def load_files():
    global current_folder
    folder = filedialog.askdirectory(title="폴더 선택")
    if folder:
        current_folder = folder
        file_list.delete(0, tk.END)
        for f in os.listdir(folder):
            if f.lower().endswith(".txt"):
                file_list.insert(tk.END, f)
        # 설정 저장 시 마지막 폴더도 기록
        save_settings(text_area.cget("font").split()[0],
                      text_area.cget("font").split()[1],
                      text_area.cget("bg"),
                      text_area.cget("fg"),
                      last_folder=current_folder)

def show_content(event):
    selection = file_list.curselection()
    if selection and current_folder:
        filename = file_list.get(selection[0])
        filepath = os.path.join(current_folder, filename)
        encoding_used = "utf-8"
        try:
            with open(filepath, "r", encoding="utf-8") as f:
                content = f.read()
        except UnicodeDecodeError:
            try:
                with open(filepath, "r", encoding="cp949") as f:
                    content = f.read()
                encoding_used = "cp949"
            except UnicodeDecodeError:
                with open(filepath, "rb") as f:
                    rawdata = f.read(50000)
                result = chardet.detect(rawdata)
                encoding_used = result["encoding"]
                with open(filepath, "r", encoding=encoding_used) as f:
                    content = f.read()

        text_area.delete(1.0, tk.END)
        text_area.insert(tk.END, content)

        line_count = content.count("\n") + 1
        file_size = os.path.getsize(filepath)
        status_label.config(
            text=f"라인 수: {line_count} | 파일 크기: {file_size} bytes | 인코딩: {encoding_used}"
        )

        # 마지막 파일 저장
        save_settings(text_area.cget("font").split()[0],
                      text_area.cget("font").split()[1],
                      text_area.cget("bg"),
                      text_area.cget("fg"),
                      last_folder=current_folder,
                      last_file=filename)

def delete_file(event=None):
    selection = file_list.curselection()
    if selection and current_folder:
        filename = file_list.get(selection[0])
        filepath = os.path.join(current_folder, filename)
        try:
            os.remove(filepath)
            file_list.delete(selection[0])
            text_area.delete(1.0, tk.END)
            status_label.config(text="")
        except Exception:
            pass

# ---------------- 옵션 GUI ----------------
settings_win = None

def open_font_settings():
    global settings_win
    if settings_win and tk.Toplevel.winfo_exists(settings_win):
        settings_win.deiconify()
        settings_win.lift()
        return

    settings_win = tk.Toplevel(root)
    settings_win.title("폰트/배경/색상 설정")
    settings_win.geometry("400x250")

    # 메인창 위치 기준으로 우측에 배치
    root.update_idletasks()
    x = root.winfo_x() + root.winfo_width()
    y = root.winfo_y()
    settings_win.geometry(f"+{x}+{y}")

    settings_win.configure(bg="#2d2d2d")

    fonts = list(font.families())
    fonts.sort()

    tk.Label(settings_win, text="폰트 선택:", bg="#2d2d2d", fg="#ffffff").pack(pady=5)
    font_combo = ttk.Combobox(settings_win, values=fonts, state="readonly")
    font_combo.set(text_area.cget("font").split()[0])
    font_combo.pack(pady=5)

    tk.Label(settings_win, text="폰트 크기:", bg="#2d2d2d", fg="#ffffff").pack(pady=5)

    def only_numbers(char): return char.isdigit()
    vcmd = (settings_win.register(only_numbers), "%S")

    size_entry = tk.Entry(settings_win, validate="key", validatecommand=vcmd)
    size_entry.insert(0, text_area.cget("font").split()[1])
    size_entry.pack(pady=5)

    def change_bg_color():
        color_code = colorchooser.askcolor(title="배경색 선택")
        if color_code[1]:
            text_area.config(bg=color_code[1])

    def change_fg_color():
        color_code = colorchooser.askcolor(title="글자색 선택")
        if color_code[1]:
            text_area.config(fg=color_code[1])

    tk.Button(settings_win, text="배경색 변경", command=change_bg_color,
              bg="#444444", fg="#ffffff").pack(pady=5)
    tk.Button(settings_win, text="글자색 변경", command=change_fg_color,
              bg="#444444", fg="#ffffff").pack(pady=5)

    def apply_changes():
        selected_font = font_combo.get()
        try:
            selected_size = int(size_entry.get())
        except ValueError:
            selected_size = 12
        text_area.config(font=(selected_font, selected_size))
        save_settings(selected_font, selected_size,
                      text_area.cget("bg"), text_area.cget("fg"),
                      last_folder=current_folder,
                      last_file=file_list.get(file_list.curselection()[0]) if file_list.curselection() else None)

    tk.Button(settings_win, text="적용", command=apply_changes,
              bg="#555555", fg="#ffffff").pack(pady=10)

# ---------------- 메인 윈도우 ----------------
root = tk.Tk()
root.title("TXT 뷰어 (Dark Mode)")
window_width = 900
window_height = 600
screen_width = root.winfo_screenwidth()
screen_height = root.winfo_screenheight()
offset = 555 # 오른쪽 끝에서 떨어질 여백
x = screen_width - window_width - offset
y = (screen_height - window_height) // 2
root.geometry(f"{window_width}x{window_height}+{x}+{y}")
root.configure(bg="#1e1e1e")
default_font = ("맑은 고딕", 12)

# PanedWindow 생성
paned = tk.PanedWindow(root, orient=tk.HORIZONTAL, sashrelief=tk.RAISED, sashwidth=5, bg="#1e1e1e")
paned.pack(fill=tk.BOTH, expand=True)

# 좌측 파일 목록
file_frame = tk.Frame(paned, bg="#1e1e1e")
file_scrollbar = tk.Scrollbar(file_frame)
file_scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
file_list = tk.Listbox(file_frame, width=40, font=default_font, selectmode=tk.SINGLE,
                       bg="#2d2d2d", fg="#ffffff",
                       selectbackground="yellow", selectforeground="black",
                       yscrollcommand=file_scrollbar.set)
file_list.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=10, pady=10)
file_scrollbar.config(command=file_list.yview)

file_list.bind("<<ListboxSelect>>", show_content)
file_list.bind("<Delete>", delete_file)
paned.add(file_frame, padx=10, pady=10)

# 우측 텍스트 영역
text_frame = tk.Frame(paned, bg="#1e1e1e")
text_scrollbar_y = tk.Scrollbar(text_frame)
text_scrollbar_y.pack(side=tk.RIGHT, fill=tk.Y)
text_area = tk.Text(text_frame, wrap="word", font=default_font, bg="#2d2d2d", fg="#ffffff",
                    insertbackground="#ffffff", padx=10, pady=10,
                    yscrollcommand=text_scrollbar_y.set)
text_area.pack(side=tk.TOP, fill=tk.BOTH, expand=True)
text_scrollbar_y.config(command=text_area.yview)

status_label = tk.Label(text_frame, text="", anchor="w", bg="#1e1e1e", fg="#ffffff", font=("맑은 고딕", 10))
status_label.pack(side=tk.BOTTOM, fill=tk.X)

paned.add(text_frame, padx=10, pady=10)

# 메뉴
menu = tk.Menu(root, bg="#2d2d2d", fg="#ffffff", tearoff=0)
root.config(menu=menu)

file_menu = tk.Menu(menu, tearoff=0, bg="#2d2d2d", fg="#ffffff")
menu.add_cascade(label="파일", menu=file_menu)
file_menu.add_command(label="폴더 열기", command=load_files)

option_menu = tk.Menu(menu, tearoff=0, bg="#2d2d2d", fg="#ffffff")
menu.add_cascade(label="옵션", menu=option_menu)
option_menu.add_command(label="폰트/배경/색상 설정", command=open_font_settings)

# 프로그램 시작 시 설정 불러오기
load_settings()

# 메인 루프 실행
root.mainloop()