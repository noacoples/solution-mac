import os
import sys
import shutil
import subprocess
import tkinter as tk
from tkinter import messagebox
import yt_dlp as youtube_dl

# En Mac, guardamos siempre en ~/Downloads/descargados
CARPETA_DESCARGAS = os.path.join(os.path.expanduser("~"), "Downloads", "descargados")
os.makedirs(CARPETA_DESCARGAS, exist_ok=True)


def obtener_carpeta_ffmpeg():
    """Devuelve la carpeta donde están ffmpeg y ffprobe (dentro del .app, carpeta local o sistema)."""
    posibles_carpetas = []

    # 1. Si corre empaquetado dentro de Solution.app (PyInstaller)
    if getattr(sys, 'frozen', False):
        posibles_carpetas.append(getattr(sys, '_MEIPASS', os.path.dirname(sys.executable)))
        posibles_carpetas.append(os.path.dirname(sys.executable))

    # 2. Si corre como script normal (.py), revisa la misma carpeta del archivo
    posibles_carpetas.append(os.path.dirname(os.path.abspath(__file__)))

    # 3. Rutas típicas de Mac (Homebrew en Apple Silicon M1/M2/M3 o Intel)
    posibles_carpetas.extend([
        "/opt/homebrew/bin",
        "/usr/local/bin"
    ])

    for carpeta in posibles_carpetas:
        ruta_bin = os.path.join(carpeta, "ffmpeg")
        if os.path.exists(ruta_bin):
            # Asegura que tenga permisos de ejecución en Mac
            try:
                os.chmod(ruta_bin, 0o755)
                ruta_probe = os.path.join(carpeta, "ffprobe")
                if os.path.exists(ruta_probe):
                    os.chmod(ruta_probe, 0o755)
            except Exception:
                pass
            return carpeta

    # Último recurso: si está en el PATH general de la Mac
    ffmpeg_sistema = shutil.which("ffmpeg")
    if ffmpeg_sistema:
        return os.path.dirname(ffmpeg_sistema)

    return None


def abrir_carpeta_mac(ruta):
    """Abre la carpeta directamente en el Finder de macOS."""
    subprocess.run(["open", ruta])


def descargar_mp3():
    url = url_input.get().strip()
    if not url:
        messagebox.showerror("Error", "Por favor, ingresa un enlace de YouTube.")
        return

    ffmpeg_dir = obtener_carpeta_ffmpeg()
    if not ffmpeg_dir:
        messagebox.showerror(
            "Falta FFmpeg",
            "No se encontró ffmpeg. Asegúrate de poner los archivos 'ffmpeg' y 'ffprobe' en la carpeta antes de crear la app."
        )
        return

    descargar_btn.config(state="disabled", text="⏳")
    app.update()

    try:
        opciones = {
            'format': 'bestaudio/best',
            # Un enlace de video con &list debe descargar solo ese video.
            'noplaylist': True,
            'outtmpl': os.path.join(CARPETA_DESCARGAS, '%(title)s.%(ext)s'),
            'ffmpeg_location': ffmpeg_dir,
            'postprocessors': [{
                'key': 'FFmpegExtractAudio',
                'preferredcodec': 'mp3',
                'preferredquality': '320',
            }],
            'extractor_args': {
                'youtube': {
                    'player_client': ['default', 'web_embedded']
                }
            }
        }

        with youtube_dl.YoutubeDL(opciones) as ydl:
            ydl.download([url])

        messagebox.showinfo("vamoooo", "descargación finaliready 🥳")
        abrir_carpeta_mac(CARPETA_DESCARGAS)

    except Exception as e:
        messagebox.showerror("Error", f"Ocurrió un error: {str(e)}")
    finally:
        descargar_btn.config(state="normal", text="😎")


# --- Interfaz Gráfica ---
app = tk.Tk()
app.title("Solu")
app.geometry("700x300")
app.configure(bg="black")

tk.Label(app, text="S O L U", fg="white", bg="black", font=("Courier", 16)).pack(pady=10)

url_input = tk.Entry(
    app, width=40, fg="white", bg="black",
    insertbackground="white", highlightbackground="white"
)
url_input.pack(pady=5)

descargar_btn = tk.Button(
    app, text="😎", command=descargar_mp3,
    fg="black", bg="black", highlightbackground="yellow",
    font=("Courier", 12), relief="ridge"
)
descargar_btn.pack(pady=20)

watermark = tk.Label(
    app, text="Nanu Boumper",
    fg="#666666", bg="black",
    font=("Courier", 10)
)
watermark.place(relx=1.0, rely=1.0, x=-10, y=-8, anchor="se")

app.mainloop()