import os
import ipywidgets as widgets
from IPython.display import display, clear_output, HTML
from llama_index.core import SimpleDirectoryReader, VectorStoreIndex
from model_config import Settings

# Ideiglenes könyvtár létrehozása Windows környezethez
temp_dir = os.path.join(os.getcwd(), 'temp_files')
os.makedirs(temp_dir, exist_ok=True)

# Globális változók
index = None
query_engine = None
conversation_history = []
default_query = "Mi az összegzése a dokumentumnak?"
file_name = None  # Globális változó a fájl nevének tárolására

# Szövegmező widget a kérdéshez
input_box = widgets.Text(
    description="Kérdés:",
    placeholder="Írd be a kérdésed...",
    layout=widgets.Layout(width='50%')
)

# Kimeneti mező a válaszhoz
output_box = widgets.Output(layout=widgets.Layout(width='50%', height='300px'))

# File feltöltő widget
file_upload = widgets.FileUpload(
    accept='.pdf',  # Csak PDF fájlok
    multiple=False,
    description="Feltöltés"
)

# A fájl feldolgozása és az index frissítése
def handle_file_upload(change):
    global index, query_engine, file_name
    uploaded_files = file_upload.value

    # Ellenőrizzük, hogy van-e feltöltött fájl
    if not uploaded_files:
        return

    # Ellenőrizzük a feltöltött fájl típusát
    if isinstance(uploaded_files, dict):
        file_info = list(uploaded_files.values())[0]
    else:
        # Ha tuple, akkor a fájl közvetlenül is elérhető
        file_info = uploaded_files[0]

    # Nyomtassuk ki a fájl információit a hibakereséshez
    print("Fájl információk:", file_info)

    # Feltételezzük, hogy a fájl információk közvetlenül elérhetők
    try:
        file_name = file_info['metadata']['name']
        file_content = file_info['content']
    except KeyError:
        # Ha a fájl nem tartalmaz 'metadata' kulcsot
        file_name = file_info['name']  # Kérjük, ellenőrizze ezt a kulcsot is
        file_content = file_info['content']

    # Fájl mentése
    file_path = os.path.join(temp_dir, file_name)
    with open(file_path, 'wb') as f:
        f.write(file_content)
    
    # Dokumentumok betöltése
    documents = SimpleDirectoryReader(input_files=[file_path]).load_data()
    index = VectorStoreIndex.from_documents(documents)
    query_engine = index.as_query_engine()
    
    # Információs üzenet a felhasználónak
    with output_box:
        clear_output(wait=True)
        print(f"Fájl sikeresen feltöltve és feldolgozva: {file_name}")
        
        # Alapértelmezett kérdés automatikus beküldése
        input_box.value = default_query
        on_submit(input_box)

# A kérdés feldolgozása és a válasz megjelenítése
def on_submit(query):
    if not query_engine:
        with output_box:
            clear_output(wait=True)
            print("Kérlek, tölts fel egy fájlt először.")
        return
    
    with output_box:
        clear_output(wait=True)  # Korábbi válaszok törlése
        
        # Kontektus építése a történetből
        conversation = "\n".join(conversation_history)
        full_query = f"{conversation}\nKérdés: {query.value}"
        
        # Válasz lekérése
        response = query_engine.query(full_query)
        
        # Történet frissítése
        conversation_history.append(f"Kérdés: {query.value}")
        conversation_history.append(f"Válasz: {response}")
        
        # Válasz megjelenítése HTML formában
        display(HTML(f"<p><strong>{file_name}</strong></p><p>{response}</p>"))

# Widgetek megjelenítése
def display_widgets():
    display(file_upload)
    file_upload.observe(handle_file_upload, names='value')
    display(input_box, output_box)
    input_box.on_submit(on_submit)
