class Test:
    pass

rows = 5
columns = 5
element = Test()

# Verwende die saubere Erzeugung ohne den Referenz-Fehler von vorhin:
matrix = [[None for _ in range(columns)] + [[0, 0]] for _ in range(rows)]
matrix.append([[0, 0] for _ in range(columns)])

# Element in der Matrix platzieren
matrix[1][1] = element

# Funktion zum Suchen des Elements
def find_element_in_matrix(target_matrix, target_element):
    for r_index, row in enumerate(target_matrix):
        if target_element in row:
            c_index = row.index(target_element)
            return r_index, c_index  # Gibt (Reihe, Spalte) zurück
    return None

# Suche ausführen
position = find_element_in_matrix(matrix, element)
print(position)  # Ausgabe: (1, 1)

print(matrix[0][-2])
print(len(matrix))

# Ausgabe zur Überprüfung
for row in matrix:
    print(row)