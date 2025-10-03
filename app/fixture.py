#función
def agregar_equipo(nombre):
    global ultimo_id, equipos

    try:
        # Validaciones
        if not isinstance(nombre, str):
            raise TypeError("El nombre del equipo debe ser una cadena de texto.")

        nombre = nombre.strip()
        if nombre == "":
            raise ValueError("El nombre del equipo no puede estar vacío.")
        
        if len(nombre) > 10:
            raise ValueError("El nombre del equipo no puede superar los 10 caracteres.")

        if nombre in equipos.values():
            raise ValueError(f"El equipo '{nombre}' ya existe.")

        ultimo_id += 1
        equipos[ultimo_id] = nombre
        print(f"✅ Equipo '{nombre}' agregado con ID {ultimo_id}.")
        return ultimo_id

    except (TypeError, ValueError) as e:
        print(f"❌ Error: {e}")
        return None

    finally:
        print("🔄 Operación finalizada.\n")


#codigo principal
equipos = {}   # Diccionario global para guardar los equipos
ultimo_id = 0  # Controla el último ID asignado

cantidad = int(input("Ingrese la cantidad de equipos: "))

while cantidad < 4 or cantidad > 16 or cantidad % 2 == 0:
    cantidad = int(input("❌ La cantidad debe ser mayor o igual a 4, menor o igual a 16 y **no puede ser par**: "))

for i in range(cantidad):
    while True: 
        nombre = input(f"Ingrese el nombre del equipo {i+1}: ")
        if agregar_equipo(nombre) is not None:
            break 
    print("Diccionario de equipos:", equipos)
