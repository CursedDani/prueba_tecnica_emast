# Lógica de datos 1:
# El Elemento solitario

def Solitary(arr:list) -> int:
    count = {}
    for i in arr:
        if i in count:
            count[i] = False
        else:
            count[i] = True

    for key, value in count.items():
        if value:
            return key

# Logica de datos 2:
# Limpieza de ceros

def ZeroCleaner(arr:list) -> list:
    count = []
    z_count = 0
    for i in arr:
        if i != 0:
            count.append(i)
        else:
            z_count += 1
    count.extend([0] * z_count)
    return count

# Logica de datos 3:
# Compresor de texto


print(f'Ejercicio 1 Ejemplo 1 output : {Solitary([4, 1, 2, 1, 2])}')
print(f'Ejercicio 1 Ejemplo 2 output : {Solitary([2,2,1,1,3,3,4,4,5,5,10,10,12,12])}')
print(f'Ejercicio 1 Ejemplo 3 output : {Solitary([0,0,0,0,0,0,1,0,0,0,0])}')
print(f'Ejercicio 2 Ejemplo 1 output : {ZeroCleaner([0, 1, 0, 3, 12] )}')
print(f'Ejercicio 2 Ejemplo 2 output : {ZeroCleaner([0, 0, 1] )}')
print(f'Ejercicio 2 Ejemplo 3 output : {ZeroCleaner([0, 0, 0, 0, 0] )}')
