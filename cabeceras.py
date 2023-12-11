import tkinter as tk
from tkinter import filedialog
from tkinter import ttk  # Importar ttk para usar Treeview
import pandas as pd
import folium
from PIL import Image, ImageTk
import simplekml
import re

def cargar_archivo():
    global df, columnas_checkbox, checkbox_frame
    ruta_archivo = filedialog.askopenfilename(title="Seleccionar archivo",
                                              filetypes=(("Archivos Excel", "*.xlsx"), ("Archivos CSV", "*.csv"), ("Todos los archivos", "*.*")))
    if ruta_archivo:
        try:
            if ruta_archivo.endswith('.xlsx'):
                df = pd.read_excel(ruta_archivo)  # Lee el archivo Excel
            else:
                df = pd.read_csv(ruta_archivo)  # Lee el archivo CSV

            # Limpiar latitud y longitud
            df['Latitud'] = df['Latitud'].apply(lambda x: limpiar_coordenadas(x))
            df['Longitud'] = df['Longitud'].apply(lambda x: limpiar_coordenadas(x))

            #mostrar_cabeceras(df)  # Muestra las cabeceras en la interfaz gráfica
            mostrar_tabla_coordenadas()  # Muestra las coordenadas en la tabla

        except Exception as e:
            resultado_label.config(text=f"Error al cargar el archivo: {e}")

def limpiar_coordenadas(coordenada):
    # Utilizar una expresión regular para mantener solo números, guiones y comas
    cleaned = re.sub(r'[^0-9,\-.]', '', str(coordenada))
    return cleaned

# Resto del código sigue igual


def mostrar_cabeceras(dataframe):
    global columnas_checkbox, checkbox_frame
    checkbox_frame = tk.Frame(root)
    checkbox_frame.grid(row=3, column=0, columnspan=2)

    columnas_checkbox = {}  # Almacena los checkboxes de las columnas

    for idx, col in enumerate(dataframe.columns):
        var = tk.IntVar()
        checkbox = tk.Checkbutton(checkbox_frame, text=col, variable=var)
        checkbox.select()  # Marca los checkboxes por defecto
        checkbox.grid(row=idx, column=0, sticky=tk.W)
        columnas_checkbox[col] = var

def mostrar_tabla_coordenadas():
    global treeview
    coordenadas_df = df[['Latitud', 'Longitud']]
    if 'treeview' in globals() and isinstance(treeview, ttk.Treeview):
        treeview.destroy()

    treeview = ttk.Treeview(root)
    treeview["columns"] = ("Latitud", "Longitud")
    treeview.column("#0", width=0, stretch=tk.NO)  # Ocultar primera columna
    treeview.heading("#0", text="", anchor=tk.W)
    treeview.heading("Latitud", text="Latitud")
    treeview.heading("Longitud", text="Longitud")

    for index, row in coordenadas_df.iterrows():
        treeview.insert("", tk.END, text="", values=(row['Latitud'], row['Longitud']))

    treeview.grid(row=6, column=0, columnspan=2, pady=10)

def generar_mapa():
    mapa = folium.Map(location=[df['Latitud'].mean(), df['Longitud'].mean()], zoom_start=10)
    kml = simplekml.Kml()

    for index, row in df.iterrows():
        latitud = row['Latitud'].replace(',', '.')  # Reemplazar comas por puntos en la latitud
        longitud = row['Longitud'].replace(',', '.')  # Reemplazar comas por puntos en la longitud

        try:
            latitud = float(latitud)
            longitud = float(longitud)

            info = ""
            for col, var in columnas_checkbox.items():
                if var.get():
                    info += f"{col}: {row[col]}\n"

            folium.Marker(
                location=[latitud, longitud],
                popup=folium.Popup(info, max_width=300),
                tooltip=row['Nombre']
            ).add_to(mapa)

            kml.newpoint(name=row['Nombre'], description=info, coords=[(longitud, latitud)])

        except ValueError:
            pass  # Ignorar valores que no se pueden convertir a números

    mapa.save('mapa.html')
    kml.save('mapa.kmz')
    resultado_label.config(text="Mapa y archivo KMZ generados, consulta mapa.html y mapa.kmz")

    mapa = folium.Map(location=[df['Latitud'].mean(), df['Longitud'].mean()], zoom_start=10)
    kml = simplekml.Kml()

    for index, row in df.iterrows():
        info = ""
        for col, var in columnas_checkbox.items():
            if var.get():
                info += f"{col}: {row[col]}\n"

        folium.Marker(
            location=[row['Latitud'], row['Longitud']],
            popup=folium.Popup(info, max_width=300),
            tooltip=row['Nombre']
        ).add_to(mapa)

        kml.newpoint(name=row['Nombre'], description=info, coords=[(row['Longitud'], row['Latitud'])])

    mapa.save('mapa.html')
    kml.save('mapa.kmz')
    resultado_label.config(text="Mapa y archivo KMZ generados, consulta mapa.html y mapa.kmz")

# Configuración de la interfaz gráfica
root = tk.Tk()
root.title("Georreferenciación de coordenadas")

# Carga y muestra el logo
logo_path = "images/logo.png"
logo = Image.open(logo_path)
logo = logo.resize((200, 200), Image.AFFINE)
logo_tk = ImageTk.PhotoImage(logo)
logo_label = tk.Label(root, image=logo_tk)
logo_label.grid(row=0, column=0, columnspan=2)

encabezado_label = tk.Label(root, text="Selecciona un archivo Excel o CSV con datos de latitud, longitud, nombre y descripción:")
encabezado_label.grid(row=1, column=0, columnspan=2)

boton_cargar = tk.Button(root, text="Cargar archivo", command=cargar_archivo)
boton_cargar.grid(row=2, column=0, columnspan=2)

boton_generar_mapa = tk.Button(root, text="Generar Mapa", command=generar_mapa)
boton_generar_mapa.grid(row=4, column=0)

resultado_label = tk.Label(root, text="")
resultado_label.grid(row=5, column=0, columnspan=2)

root.mainloop()
