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


print(Solitary([4, 4, 1, 2, 1, 2]))
