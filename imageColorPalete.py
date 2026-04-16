import cv2
import numpy as np
import random

# =====================================================
# ALL 53 LEGO COLORS
# =====================================================
lego_colors_list = [
    [1,  "Black",                [5,   19,  29 ]], [2,  "Blue",                 [0,   85,  191]],
    [3,  "Green",                [35,  120, 65 ]], [4,  "Dark Turquoise",       [0,   143, 155]],
    [5,  "Red",                  [201, 26,  9  ]], [6,  "Dark Pink",            [200, 112, 160]],
    [7,  "Bright Green",         [75,  159, 74 ]], [8,  "Yellow",               [242, 205, 55 ]],
    [9,  "White",                [255, 255, 255]], [10, "Tan",                  [228, 205, 158]],
    [11, "Orange",               [254, 138, 24 ]], [12, "Magenta",              [146, 57,  120]],
    [13, "Lime",                 [187, 233, 11 ]], [14, "Dark Tan",             [149, 138, 115]],
    [15, "Bright Pink",          [228, 173, 200]], [16, "Medium Lavender",      [172, 120, 186]],
    [17, "Lavender",             [225, 213, 237]], [18, "Reddish Brown",        [88,  42,  18 ]],
    [19, "Light Bluish Gray",    [160, 165, 169]], [20, "Dark Bluish Gray",     [108, 110, 104]],
    [21, "Medium Blue",          [90,  147, 219]], [22, "Light Nougat",         [246, 215, 179]],
    [23, "Metallic Silver",      [165, 169, 180]], [24, "Metallic Gold",        [219, 172, 52 ]],
    [25, "Medium Nougat",        [170, 125, 85 ]], [26, "Dark Purple",          [63,  54,  145]],
    [27, "Nougat",               [208, 145, 104]], [28, "Yellowish Green",      [223, 238, 165]],
    [29, "Flat Silver",          [137, 135, 136]], [30, "Bright Light Orange",  [248, 187, 61 ]],
    [31, "Bright Light Blue",    [159, 195, 233]], [32, "Bright Light Yellow",  [255, 240, 58 ]],
    [33, "Dark Blue",            [10,  52,  99 ]], [34, "Dark Green",           [24,  70,  50 ]],
    [35, "Pearl Gold",           [170, 127, 46 ]], [36, "Dark Brown",           [53,  33,  0  ]],
    [37, "Dark Red",             [114, 14,  15 ]], [38, "Dark Azure",           [7,   139, 201]],
    [39, "Medium Azure",         [54,  174, 191]], [40, "Light Aqua",           [173, 195, 192]],
    [41, "Olive Green",          [155, 154, 90 ]], [42, "Chrome Gold",          [187, 165, 61 ]],
    [43, "Sand Green",           [160, 188, 172]], [44, "Sand Blue",            [96,  116, 161]],
    [45, "Chrome Silver",        [224, 224, 224]], [46, "Dark Orange",          [169, 85,  0  ]],
    [47, "Glow in Dark White",   [217, 217, 217]], [48, "Coral",                [255, 105, 143]],
    [49, "Vibrant Yellow",       [235, 216, 0  ]], [50, "Medium Brown",         [117, 89,  69 ]],
    [51, "Warm Tan",             [204, 163, 115]], [52, "Pearl Titanium",       [62,  60,  57 ]],
    [53, "Reddish Orange",       [202, 76,  11 ]],
]

PALETTE = np.array([c[2] for c in lego_colors_list], dtype=np.uint8)

# =====================================================
# CONFIG
# =====================================================
GRID     = 64       
TILE     = 4  
TILES_X  = GRID // TILE
TILES_Y  = GRID // TILE

POP      = 150      
GENS     = 2000     # Increased
MUT_RATE = 0.10     
ELITE_K  = 5

# Pre-calculate the best color index for every single tile to "guide" mutations
def get_target_indices(target_img):
    indices = []
    for ty in range(TILES_Y):
        for tx in range(TILES_X):
            y, x = ty * TILE + TILE//2, tx * TILE + TILE//2
            pixel = target_img[y, x]
            diffs = np.sum((PALETTE.astype(np.float32) - pixel)**2, axis=1)
            indices.append(np.argmin(diffs))
    return indices

class Genome:
    def __init__(self):
        self.tiles = [random.randint(0, len(PALETTE) - 1) for _ in range(TILES_X * TILES_Y)]
        self.fitness = float("inf")

    def render(self):
        img = np.zeros((GRID, GRID, 3), dtype=np.uint8)
        for i, color_idx in enumerate(self.tiles):
            ty, tx = divmod(i, TILES_X)
            img[ty*TILE:(ty+1)*TILE, tx*TILE:(tx+1)*TILE] = PALETTE[color_idx]
        return img

    def mutate(self, target_indices):
        for i in range(len(self.tiles)):
            if random.random() < MUT_RATE:
                if random.random() < 0.6: # 60% chance to move TOWARDS the correct color
                    self.tiles[i] = target_indices[i]
                else:
                    self.tiles[i] = random.randint(0, len(PALETTE) - 1)

def crossover(p1, p2):
    child = Genome()
    cut = random.randint(0, len(p1.tiles))
    child.tiles = p1.tiles[:cut] + p2.tiles[cut:]
    return child

def run(target_img):
    target_indices = get_target_indices(target_img)
    pop = [Genome() for _ in range(POP)]
    
    for gen in range(GENS + 1):
        for p in pop:
            rendered = p.render()
            p.fitness = np.mean((rendered.astype(np.float32) - target_img.astype(np.float32))**2)
        
        pop.sort(key=lambda x: x.fitness)
        
        if gen % 100 == 0:
            print(f"Gen {gen:4d} | MSE: {pop[0].fitness:.2f}")

        new_pop = pop[:ELITE_K] # Keep elites
        while len(new_pop) < POP:
            parent1 = random.choice(pop[:20])
            parent2 = random.choice(pop[:20])
            child = crossover(parent1, parent2)
            child.mutate(target_indices)
            new_pop.append(child)
        pop = new_pop
        
    return pop[0]

# =====================================================
# RUN
# =====================================================
target = cv2.imread("animal.jpg")
target = cv2.cvtColor(target, cv2.COLOR_BGR2RGB)
target = cv2.resize(target, (GRID, GRID))

best = run(target)
result = best.render()

# Save outputs
cv2.imwrite("AnimalImage_big.jpg", cv2.cvtColor(cv2.resize(result, (640, 640), interpolation=cv2.INTER_NEAREST), cv2.COLOR_RGB2BGR))
print("Done! Look at AnimalImage_big.jpg")