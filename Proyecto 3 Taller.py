import heapq #accedemos rapidamente al elemento más équeño o mas grande de coleccion en colas de prioridad
import os #interactamos con sistema operatibvo y asi con archivos y directorios
import sys #obtenemso argumenpos pasadoas al script interactuando con linea de comandos
import bitarray #manipula secuencias de bits

def nodos_huffman(simbolo, freq):
    return {"simbolo": simbolo, "frecuencia": freq, "Hijo Izquierdo": None, "Hijo Derecho": None}

def comparar_nodos(N):
    return N["frecuencia"]

def frecuencias(file_path):
    freqss = {}
    with open(file_path, "r") as file:
        for line in file:
            for char in line:
                if char in freqss:
                    freqss[char] += 1
                else:
                    freqss[char] = 1
    return freqss

def arbol_huffman(freqss):
    heap = [(freq, nodos_huffman(simbolo, freq)) for simbolo, freq in freqss.items()]
    #hacemos heap de tuplas donde cada tupla tiene una frecuenci ay un nodo de huffamn
    heapq.heapify(heap)

    while len(heap) > 1:
        freq1, HIz = heapq.heappop(heap)#freque 1 y 2 almacenan 
        freq2, HDrch = heapq.heappop(heap)
        merged = nodos_huffman(None, freq1 + freq2)
        merged["Hijo Izquierdo"] = HIz
        merged["Hijo Derecho"] = HDrch
        heapq.heappush(heap, (merged["frecuencia"], merged))
#el heap 0 selecciona la primera tupla
#heap 0 1 devuelve frecuencias construidas de freqss
    return heap[0][1] #0 es frecuenci adel nodo huffman y 1 el nodo huffman creado en nodos_huffman

def codigos_little_file(N, road="", storecode=None):
    if storecode is None:
        storecode = {}
    if N["simbolo"] is not None:
        storecode[N["simbolo"]] = road
    else:
        codigos_little_file(N["Hijo Izquierdo"], road + "0", storecode)
        codigos_little_file(N["Hijo Derecho"], road + "1", storecode)
    return storecode

def comprimir_archivo(file_path, storecode):
    comprimido = bitarray.bitarray()
    with open(file_path, 'r') as file:
        for line in file:
            for char in line:
                comprimido.extend(bitarray.bitarray(storecode[char]))
    return comprimido

def guardar_comprimido(file_path, comprimido, storecode, stats):
    with open(file_path + ".huff", "wb") as comprimir_file:
        comprimir_file.write(comprimido.tobytes())
    with open(file_path + ".table", "w") as table_file:
        for char, code in storecode.items():
            table_file.write(char + ": " + code + "\n")
    with open(file_path + ".stats", "w") as stats_file:
        stats_file.write("La altura del árbol es: " + str(stats["altura"]) + "\n")
        stats_file.write("La anchura del árbol es: " + str(stats["anchura"]) + "\n")
        stats_file.write("La cantidad de nodos por nivel es de: " + "\n")
        for level, count in stats["nodes_per_level"].items():
            stats_file.write("El nivel es " + str(level) + " y tiene: " + str(count) + "\n")
        stats_file.write("Tabla de frecuencias original: " + "\n")
        for char, freq in stats["frecuencias"].items():
            stats_file.write("El caracter: " + str(char) + " aparece con frecuencia de: " + str(freq) + "\n")

def huffman_stats(root):
    def height(N):
        if N is None:
            return 0
        return max(height(N["Hijo Izquierdo"]), height(N["Hijo Derecho"])) + 1

    def width(N):
        if N is None:
            return 0
        q = [N]
        max_width = 0
        while q:
            count = len(q)
            max_width = max(max_width, count)
            for _ in range(count):
                n_width = q.pop(0)
                if n_width["Hijo Izquierdo"]:
                    q.append(n_width["Hijo Izquierdo"])
                if n_width["Hijo Derecho"]:
                    q.append(n_width["Hijo Derecho"])
        return max_width

    def nodes_per_level(N):
        if N is None:
            return {}
        levels = {}
        q = [(N, 0)]
        while q:
            n_width, level = q.pop(0)
            if level not in levels:
                levels[level] = 0
            levels[level] += 1
            if n_width["Hijo Izquierdo"]:
                q.append((n_width["Hijo Izquierdo"], level + 1))
            if n_width["Hijo Derecho"]:
                q.append((n_width["Hijo Derecho"], level + 1))
        return levels

    return {
        "altura": height(root),
        "anchura": width(root),
        "nodes_per_level": nodes_per_level(root),
    }

def main_compressor(input_file):
    freqss = frecuencias(input_file)
    huffman_tree_root = arbol_huffman(freqss)
    storecode = codigos_little_file(huffman_tree_root)
    comprimido = comprimir_archivo(input_file, storecode)
    stats = huffman_stats(huffman_tree_root)
    stats["frecuencias"] = freqss
    guardar_comprimido(input_file, comprimido, storecode, stats)

def load_codes(table_file_path):
    storecode = {}
    with open(table_file_path, 'r') as table_file:
        for line in table_file:
            char, code = line.strip().split(': ')
            storecode[code] = char
    return storecode

def descomprimir_archivo(compressed_file_path, storecode, output_file_path):
    reverse_codes = {v: k for k, v in storecode.items()}
    bits = bitarray.bitarray()
    with open(compressed_file_path, 'rb') as compressed_file:
        bits.fromfile(compressed_file)

    decoded_text = ""
    current_code = ""
    for bit in bits:
        current_code += '1' if bit else '0'
        if current_code in reverse_codes:
            decoded_text += reverse_codes[current_code]
            current_code = ""

    with open(output_file_path, 'w') as output_file:
        output_file.write(decoded_text)

def main_decompressor(compressed_file, table_file, output_file):
    storecode = load_codes(table_file)
    descomprimir_archivo(compressed_file, storecode, output_file)
