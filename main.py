import tkinter as tk
from tkinter import filedialog
import pandas as pd
import folium
from PIL import Image, ImageTk  # Importa las bibliotecas necesarias
import simplekml

def cargar_archivo():
    ruta_archivo = filedialog.askopenfilename(title="Seleccionar archivo",
                                              filetypes=(("Archivos Excel", "*.xlsx"), ("Archivos CSV", "*.csv"), ("Todos los archivos", "*.*")))
    if ruta_archivo:
        try:
            if ruta_archivo.endswith('.xlsx'):
                df = pd.read_excel(ruta_archivo)  # Lee el archivo Excel
            else:
                df = pd.read_csv(ruta_archivo)  # Lee el archivo CSV
            generar_mapa(df)  # Llama a la función para generar el mapa
       
        except Exception as e:
            resultado_label.config(text=f"Error al cargar el archivo: {e}")

def generar_mapa(dataframe):
    mapa = folium.Map(location=[dataframe['Latitud'].mean(), dataframe['Longitud'].mean()], zoom_start=10)  # Centra el mapa en el promedio de las coordenadas
    kml = simplekml.Kml()  # Crea un objeto Kml de simplekml

    for index, row in dataframe.iterrows():
        info = f"<b>Numero:</b> {row['Numb']}<br><b>Fecha:</b> {row['Fecha']}"  # Aquí puedes personalizar la información que deseas mostrar
        folium.Marker([row['Latitud'], row['Longitud']], popup=info).add_to(mapa)
        #folium.Marker([row['Latitud'], row['Longitud']]).add_to(mapa)  # Añade marcadores al mapa
        kml.newpoint(name=row['Numb'], description=info, coords=[(row['Longitud'], row['Latitud'])])

    mapa.save('mapa.html')  # Guarda el mapa como archivo HTML
    kml.save('mapa.kmz')

    resultado_label.config(text="Mapa generado, consulta el archivo mapa.html")

# Configuración de la interfaz gráfica
root = tk.Tk()
root.title("Georreferenciación de coordenadas")

# Carga y muestra el logo
logo_path = "images/logo.png"  # Reemplaza con la ruta de tu archivo PNG
logo = Image.open(logo_path)
#logo = logo.resize((200, 200), Image.AFFINE)  # Ajusta el tamaño del logo
logo_tk = ImageTk.PhotoImage(logo)
logo_label = tk.Label(root, image=logo_tk)
logo_label.pack()

encabezado_label = tk.Label(root, text="Selecciona un archivo CSV con datos de latitud y longitud:")
encabezado_label.pack()

boton_cargar = tk.Button(root, text="Cargar archivo", command=cargar_archivo)
boton_cargar.pack()

resultado_label = tk.Label(root, text="")
resultado_label.pack()

root.mainloop()
