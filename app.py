import streamlit as st
import subprocess
import os
import shutil
import importlib

def get_ffmpeg_executable():
    """Return path to ffmpeg executable.

    Order of detection:
    1. system ffmpeg (shutil.which)
    2. imageio_ffmpeg.get_ffmpeg_exe() if imageio-ffmpeg is installed
    Returns None if no executable is available.
    """
    system_ffmpeg = shutil.which("ffmpeg")
    if system_ffmpeg:
        return system_ffmpeg

    # Try imageio-ffmpeg if available
    try:
        imageio_ffmpeg = importlib.import_module("imageio_ffmpeg")
        ff = imageio_ffmpeg.get_ffmpeg_exe()
        if ff:
            return ff
    except Exception:
        pass

    return None


def convert_file(uploaded_file, output_format, ffmpeg_exe=None):
    input_path = f"temp/{uploaded_file.name}"
    output_path = f"temp/converted.{output_format}"

    with open(input_path, "wb") as f:
        f.write(uploaded_file.getbuffer())

    if ffmpeg_exe is None:
        ffmpeg_exe = get_ffmpeg_executable()

    if ffmpeg_exe is None:
        # No ffmpeg available
        if os.path.exists(input_path):
            os.remove(input_path)
        return None

    try:
        command = [
            ffmpeg_exe,
            "-y",
            "-i",
            input_path,
            output_path
        ]
        subprocess.run(command, check=True)
        return output_path
    except subprocess.CalledProcessError:
        return None
    finally:
        if os.path.exists(input_path):
            os.remove(input_path)

def main():
    st.title("Konwerter plików multimedialnych")
    st.caption("Limit 10MB per file • JPEG, PNG, BMP, FLV, MOV, MP4, AVI, WAV, MP3, 3GP, MIDI")

    # Refined custom CSS to hide the default placeholder text in the file uploader
    st.markdown(
        """
        <style>
        div[data-testid="stFileUploader"] div:first-child {
            display: none;
        }
        </style>
        """,
        unsafe_allow_html=True
    )

    uploaded_file = st.file_uploader("Prześlij plik (maksymalny rozmiar: 10MB)", type=["jpeg", "png", "bmp", "flv", "mov", "mp4", "avi", "wav", "mp3", "3gp", "midi", "jpg", "mpeg4"], help="Limit 10MB per file")
    output_format = st.selectbox("Wybierz format docelowy", ["jpeg", "png", "bmp", "flv", "mov", "mp4", "avi", "wav", "mp3", "3gp", "midi"])

    # Check ffmpeg availability once and reuse
    ffmpeg_exe = get_ffmpeg_executable()
    if ffmpeg_exe is None:
        st.warning("Nie znaleziono binarki ffmpeg. Możesz zainstalować pakiet systemowy `ffmpeg` lub użyć `imageio-ffmpeg` jako fallback.")
        if st.button("Zainstaluj imageio-ffmpeg (pip)"):
            with st.spinner("Instaluję imageio-ffmpeg..."):
                import sys
                import subprocess as _sub
                try:
                    _sub.check_call([sys.executable, "-m", "pip", "install", "imageio-ffmpeg"])
                    st.success("Zainstalowano imageio-ffmpeg. Odśwież stronę, aby użyć go jako ffmpeg.")
                except Exception as e:
                    st.error(f"Instalacja nie powiodła się: {e}")

    if uploaded_file and output_format:
        # Determine the type of the uploaded file
        video_formats = ["flv", "mov", "mp4", "avi", "3gp", "mpeg4"]
        image_formats = ["jpeg", "png", "bmp", "jpg"]
        audio_formats = ["wav", "mp3", "midi"]

        file_extension = uploaded_file.name.split(".")[-1].lower()

        if file_extension in video_formats and output_format not in video_formats:
            st.error("Nie można konwertować plików wideo na inne typy niż wideo.")
            return
        elif file_extension in image_formats and output_format not in image_formats:
            st.error("Nie można konwertować obrazów na inne typy niż obrazy.")
            return
        elif file_extension in audio_formats and output_format not in audio_formats:
            st.error("Nie można konwertować plików audio na inne typy niż audio.")
            return

        if uploaded_file.size > 10 * 1024 * 1024:
            st.error("Plik jest za duży. Maksymalny rozmiar to 10 MB.")
        else:
            output_path = convert_file(uploaded_file, output_format, ffmpeg_exe=ffmpeg_exe)
            if output_path:
                with open(output_path, "rb") as f:
                    st.download_button(
                        label="Pobierz przekonwertowany plik",
                        data=f,
                        file_name=f"converted.{output_format}",
                        mime="application/octet-stream"
                    )
                st.success("Konwersja zakończona sukcesem!")
                os.remove(output_path)
            else:
                st.error("Wystąpił błąd podczas konwersji pliku.")

if __name__ == "__main__":
    if not os.path.exists("temp"):
        os.makedirs("temp")
    main()
