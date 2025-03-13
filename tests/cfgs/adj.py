"""
Auto generate configs from adjacency matrix

"""

graph = [
    [0, 0, 0, 0, 0, 0, 0, 0],
    [0, 0, 1, 0, 0, 0, 5, 8],
    [0, 1, 0, 3, 0, 0, 0, 0],
    [0, 0, 3, 0, 4, 0, 0, 0],
    [0, 0, 0, 4, 0, 2, 0, 6],
    [0, 0, 0, 0, 2, 0, 1, 0],
    [0, 5, 0, 0, 0, 1, 0, 0],
    [0, 8, 0, 0, 6, 0, 0, 0],
]


for i, row in enumerate(graph):
    if sum(row) > 0:
        with open(f"./figure1/cfg{i}.txt", "a", encoding='utf-8') as f:
            f.write(f"router-id {i}\n")

            input_line  = "input-ports"
            output_line = "output-ports"
            for j, col in enumerate(row):
                if col != 0:
                    input_line  += f" 6{j}{i}0"
                    output_line += f" 6{i}{j}0-{col}-{j}"

            f.write(input_line  + "\n")
            f.write(output_line + "\n")
