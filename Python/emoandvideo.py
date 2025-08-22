import customtkinter as ctk
import cv2
import threading
import os
import sys
import subprocess

ctk.set_appearance_mode("System")
ctk.set_default_color_theme("blue")

root = ctk.CTk()
root.geometry("400x500")
root.title("Месенджер з емоджі та відео")

chat_frame = ctk.CTkScrollableFrame(root, width=380, height=300)
chat_frame.pack(pady=10, padx=10, fill="both", expand=True)

def send_message(msg):
    label = ctk.CTkLabel(chat_frame, text=msg, anchor="w", justify="left")
    label.pack(fill="x", pady=2, padx=5)
    chat_frame.update_idletasks()

button_frame = ctk.CTkFrame(root, fg_color="transparent")
button_frame.pack(side="bottom", fill="x", padx=10, pady=10)

btn1 = ctk.CTkButton(button_frame, text="😊", width=40, height=40, font=("Arial", 20))
btn1.pack(side="left", padx=5)

btn2 = ctk.CTkButton(button_frame, text="📷", width=40, height=40, font=("Arial", 20))
btn2.pack(side="left", padx=5)

emoji_panel = ctk.CTkFrame(root, fg_color="lightgray", corner_radius=10)
emoji_panel.place_forget()
emoji_list = ["😀","😂","😍","😎","🥳","😇"]

def emoji_click(em):
    send_message(f"Ти: {em}")
    emoji_panel.place_forget()

for i, em in enumerate(emoji_list):
    btn = ctk.CTkButton(emoji_panel, text=em, width=30, height=30, font=("Arial", 16),
                        command=lambda e=em: emoji_click(e))
    btn.grid(row=0, column=i, padx=3, pady=3)

def toggle_emoji_panel():
    if emoji_panel.winfo_ismapped():
        emoji_panel.place_forget()
    else:
        x = btn1.winfo_rootx() - root.winfo_rootx() + btn1.winfo_width()/2 - emoji_panel.winfo_reqwidth()/2
        y = btn1.winfo_rooty() - root.winfo_rooty() - emoji_panel.winfo_reqheight() - 5
        x = max(0, min(x, root.winfo_width() - emoji_panel.winfo_reqwidth()))
        emoji_panel.place(x=x, y=y)

btn1.configure(command=toggle_emoji_panel)

recording = False
video_counter = 0

def open_video_file(filename):
    filepath = os.path.abspath(filename)
    try:
        if sys.platform.startswith('win'):
            os.startfile(filepath)
        elif sys.platform.startswith('darwin'):
            subprocess.Popen(['open', filepath])
        else:
            subprocess.Popen(['xdg-open', filepath])
    except Exception as e:
        print("Не вдалося відкрити відео:", e)

def record_video():
    global recording, video_counter
    filename = f"video_{video_counter}.avi"
    video_counter += 1

    cap = cv2.VideoCapture(0)
    if not cap.isOpened():
        print("Не вдалося відкрити камеру")
        return

    fourcc = cv2.VideoWriter_fourcc(*'XVID')
    out = cv2.VideoWriter(filename, fourcc, 20.0, (640, 480))

    while recording:
        ret, frame = cap.read()
        if not ret:
            break
        frame = cv2.flip(frame, 1)
        out.write(frame)
        cv2.imshow('Recording', frame)
        if cv2.waitKey(1) & 0xFF == ord('q'):
            break

    cap.release()
    out.release()
    cv2.destroyAllWindows()


    send_message("Ти: Відео надіслано")
    video_btn = ctk.CTkButton(chat_frame, text="▶ Відкрити відео", width=120, height=25,
                              command=lambda f=filename: open_video_file(f))
    video_btn.pack(pady=2)

def toggle_recording():
    global recording
    if recording:
        recording = False
        btn2.configure(text="📷")
    else:
        recording = True
        btn2.configure(text="⏹")
        threading.Thread(target=record_video, daemon=True).start()

def play_sound():
    try:
        subprocess.run(["ffmpeg", "-i", "sound.mp3", "-nodisp", "-autoexit"], check=True)
    except FileNotFoundError:
        print("Помилка: ffmpeg не знайдено. Переконайся, що він встановлений та доданий у PATH.")

btn2.configure(command=toggle_recording)

play_sound()

root.mainloop()
