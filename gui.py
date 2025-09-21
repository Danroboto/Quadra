import tkinter as tk
from tkinter import messagebox, Toplevel, ttk, scrolledtext
from PIL import Image, ImageTk
import requests
import io

def abrir_calificacion(puesto_id, ventana_detalle):
    calif_win = Toplevel(ventana_detalle)
    calif_win.title("Agregar Calificación")

    tk.Label(calif_win, text="Comentario:").pack(pady=(10,0))
    comentario_entry = tk.Entry(calif_win, width=50)
    comentario_entry.pack(pady=5)

    tk.Label(calif_win, text="Calificación (1-5):").pack()
    calificacion_var = tk.IntVar(value=5)
    calificacion_spin = tk.Spinbox(calif_win, from_=1, to=5, textvariable=calificacion_var)
    calificacion_spin.pack(pady=5)

    def enviar_calificacion():
        comentario = comentario_entry.get()
        calificacion = calificacion_var.get()

        if not comentario.strip():
            messagebox.showwarning("Atención", "El comentario no puede estar vacío")
            return

        data = {
            'comentario': comentario,
            'calificacion': calificacion
        }

        try:
            response = requests.post(
                f"http://127.0.0.1:5000/puestos/{puesto_id}/comentarios",
                json=data
            )
            if response.status_code == 201:
                messagebox.showinfo("Éxito", "Comentario enviado correctamente")
                calif_win.destroy()
            else:
                messagebox.showerror("Error", "No se pudo enviar el comentario")
        except Exception as e:
            messagebox.showerror("Error", f"No se pudo conectar al servidor:\n{e}")

    tk.Button(calif_win, text="Enviar", command=enviar_calificacion).pack(pady=10)

def mostrar_detalles(puesto, ventana_principal):
    ventana = Toplevel(ventana_principal)
    ventana.title(f"Detalles: {puesto['nombre']}")

    frame_izq = tk.Frame(ventana)
    frame_izq.grid(row=0, column=0, padx=10, pady=10)

    frame_der = tk.Frame(ventana)
    frame_der.grid(row=0, column=1, padx=10, pady=10, sticky='n')

   
    foto_url = f"http://127.0.0.1:5000/static/uploads/{puesto['foto']}"
    try:
        img_response = requests.get(foto_url)
        img_data = img_response.content
        image = Image.open(io.BytesIO(img_data))
        image.thumbnail((250, 250))
        photo = ImageTk.PhotoImage(image)

        img_label = tk.Label(frame_izq, image=photo)
        img_label.image = photo
        img_label.pack()
    except Exception:
        tk.Label(frame_izq, text="[Imagen no disponible]").pack()

   
    tk.Label(frame_der, text=puesto['nombre'], font=("Helvetica", 16, "bold")).pack(anchor='w')
    tk.Label(frame_der, text=puesto['descripcion'], wraplength=300).pack(anchor='w', pady=5)
    tk.Label(frame_der, text=f"Ubicación: {puesto['latitud']}, {puesto['longitud']}").pack(anchor='w')
    tk.Label(frame_der, text=f"⭐ Promedio: {puesto['promedio_calificacion']:.1f} ({puesto['total_comentarios']} comentarios)").pack(anchor='w', pady=5)

    
    tk.Label(frame_der, text="Comentarios:", font=("Helvetica", 12, "underline")).pack(anchor='w', pady=(10,0))
    comentarios_text = scrolledtext.ScrolledText(frame_der, width=40, height=10, state='disabled')
    comentarios_text.pack()

    
    try:
        response = requests.get(f"http://127.0.0.1:5000/puestos/{puesto['id']}/comentarios")
        if response.status_code == 200:
            comentarios = response.json()
            comentarios_text.config(state='normal')
            comentarios_text.delete('1.0', tk.END)
            if comentarios:
                for c in comentarios:
                    comentarios_text.insert(tk.END, f"{c['fecha']} - ⭐{c['calificacion']}\n{c['comentario']}\n\n")
            else:
                comentarios_text.insert(tk.END, "No hay comentarios aún.")
            comentarios_text.config(state='disabled')
        else:
            comentarios_text.insert(tk.END, "Error al cargar comentarios.")
    except Exception:
        comentarios_text.insert(tk.END, "Error al cargar comentarios.")

    
    tk.Button(frame_der, text="Agregar Calificación", command=lambda: abrir_calificacion(puesto['id'], ventana)).pack(pady=10)

def ver_puestos_mejorado():
    try:
        response = requests.get('http://127.0.0.1:5000/puestos')
        puestos = response.json()
    except Exception as e:
        messagebox.showerror("Error", f"No se pudo obtener la lista de puestos:\n{e}")
        return

    ventana = Toplevel()
    ventana.title("Lista de Puestos")

    
    cols = ("Nombre", "Promedio", "Comentarios")
    tree = ttk.Treeview(ventana, columns=cols, show='headings')
    tree.pack(fill='both', expand=True)

    for col in cols:
        tree.heading(col, text=col)
        tree.column(col, width=150)

    
    puestos_dict = {}

    for puesto in puestos:
        tree.insert('', 'end', iid=puesto['id'], values=(
            puesto['nombre'],
            f"{puesto['promedio_calificacion']:.1f} ⭐",
            puesto['total_comentarios']
        ))
        puestos_dict[puesto['id']] = puesto

    def on_select(event):
        selected_id = tree.focus()
        if selected_id:
            puesto = puestos_dict[int(selected_id)]
            mostrar_detalles(puesto, ventana)

    tree.bind('<<TreeviewSelect>>', on_select)

def subir_puesto():
    ventana = Toplevel()
    ventana.title("Subir Puesto")

    tk.Label(ventana, text="Nombre:").grid(row=0, column=0, sticky='e')
    nombre_entry = tk.Entry(ventana, width=40)
    nombre_entry.grid(row=0, column=1, padx=10, pady=5)

    tk.Label(ventana, text="Descripción:").grid(row=1, column=0, sticky='e')
    descripcion_entry = tk.Entry(ventana, width=40)
    descripcion_entry.grid(row=1, column=1, padx=10, pady=5)

    tk.Label(ventana, text="Latitud:").grid(row=2, column=0, sticky='e')
    lat_entry = tk.Entry(ventana, width=40)
    lat_entry.grid(row=2, column=1, padx=10, pady=5)

    tk.Label(ventana, text="Longitud:").grid(row=3, column=0, sticky='e')
    lon_entry = tk.Entry(ventana, width=40)
    lon_entry.grid(row=3, column=1, padx=10, pady=5)

    tk.Label(ventana, text="Foto (ruta local):").grid(row=4, column=0, sticky='e')
    foto_entry = tk.Entry(ventana, width=40)
    foto_entry.grid(row=4, column=1, padx=10, pady=5)

    def enviar():
        nombre = nombre_entry.get()
        descripcion = descripcion_entry.get()
        lat = lat_entry.get()
        lon = lon_entry.get()
        foto_path = foto_entry.get()

        if not all([nombre, descripcion, lat, lon, foto_path]):
            messagebox.showerror("Error", "Completa todos los campos")
            return

        try:
            with open(foto_path, 'rb') as f:
                files = {'foto': (foto_path.split('/')[-1], f)}
                data = {
                    'nombre': nombre,
                    'descripcion': descripcion,
                    'latitud': lat,
                    'longitud': lon
                }
                response = requests.post('http://127.0.0.1:5000/puestos', data=data, files=files)

            if response.status_code == 201:
                messagebox.showinfo("Éxito", "Puesto subido correctamente")
                ventana.destroy()
            else:
                messagebox.showerror("Error", "Error al subir puesto")

        except Exception as e:
            messagebox.showerror("Error", f"No se pudo subir la foto:\n{e}")

    tk.Button(ventana, text="Subir", command=enviar).grid(row=5, column=0, columnspan=2, pady=10)

def main():
    root = tk.Tk()
    root.title("Quadra Mejorado")
    root.geometry("400x250")

    style = ttk.Style(root)
    style.configure('TButton', font=('Helvetica', 12), padding=10)

    tk.Label(root, text="Bienvenido a Quadra", font=("Helvetica", 16, "bold")).pack(pady=20)

    ttk.Button(root, text="Subir Puesto", command=subir_puesto).pack(pady=10)
    ttk.Button(root, text="Ver Puestos", command=ver_puestos_mejorado).pack(pady=10)

    root.mainloop()

if __name__ == '__main__':
    main()
