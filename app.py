import streamlit as st
import subprocess
import os

def convert_file(uploaded_file, output_format):
    input_path = f"temp/{uploaded_file.name}"
    output_path = f"temp/converted.{output_format}"

    with open(input_path, "wb") as f:
        f.write(uploaded_file.getbuffer())

    try:
        command = [
            "ffmpeg",
            "-i", input_path,
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

    uploaded_file = st.file_uploader("Prześlij plik", type=["jpeg", "png", "bmp", "flv", "mov", "mp4", "avi", "wav", "mp3", "3gp", "midi"])
    output_format = st.selectbox("Wybierz format docelowy", ["jpeg", "png", "bmp", "flv", "mov", "mp4", "avi", "wav", "mp3", "3gp", "midi"])

    if uploaded_file and output_format:
        if uploaded_file.size > 10 * 1024 * 1024:
            st.error("Plik jest za duży. Maksymalny rozmiar to 10 MB.")
        else:
            output_path = convert_file(uploaded_file, output_format)
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
