import cv2
import numpy as np
import random

# =====================================================
# ALL 53 LEGO COLORS
# =====================================================
lego_colors_list = [
    [1,  "Black",                [5,   19,  29 ]],
    [2,  "Blue",                 [0,   85,  191]],
    [3,  "Green",                [35,  120, 65 ]],
    [4,  "Dark Turquoise",       [0,   143, 155]],
    [5,  "Red",                  [201, 26,  9  ]],
    [6,  "Dark Pink",            [200, 112, 160]],
    [7,  "Bright Green",         [75,  159, 74 ]],
    [8,  "Yellow",               [242, 205, 55 ]],
    [9,  "White",                [255, 255, 255]],
    [10, "Tan",                  [228, 205, 158]],
    [11, "Orange",               [254, 138, 24 ]],
    [12, "Magenta",              [146, 57,  120]],
    [13, "Lime",                 [187, 233, 11 ]],
    [14, "Dark Tan",             [149, 138, 115]],
    [15, "Bright Pink",          [228, 173, 200]],
    [16, "Medium Lavender",      [172, 120, 186]],
    [17, "Lavender",             [225, 213, 237]],
    [18, "Reddish Brown",        [88,  42,  18 ]],
    [19, "Light Bluish Gray",    [160, 165, 169]],
    [20, "Dark Bluish Gray",     [108, 110, 104]],
    [21, "Medium Blue",          [90,  147, 219]],
    [22, "Light Nougat",         [246, 215, 179]],
    [23, "Metallic Silver",      [165, 169, 180]],
    [24, "Metallic Gold",        [219, 172, 52 ]],
    [25, "Medium Nougat",        [170, 125, 85 ]],
    [26, "Dark Purple",          [63,  54,  145]],
    [27, "Nougat",               [208, 145, 104]],
    [28, "Yellowish Green",      [223, 238, 165]],
    [29, "Flat Silver",          [137, 135, 136]],
    [30, "Bright Light Orange",  [248, 187, 61 ]],
    [31, "Bright Light Blue",    [159, 195, 233]],
    [32, "Bright Light Yellow",  [255, 240, 58 ]],
    [33, "Dark Blue",            [10,  52,  99 ]],
    [34, "Dark Green",           [24,  70,  50 ]],
    [35, "Pearl Gold",           [170, 127, 46 ]],
    [36, "Dark Brown",           [53,  33,  0  ]],
    [37, "Dark Red",             [114, 14,  15 ]],
    [38, "Dark Azure",           [7,   139, 201]],
    [39, "Medium Azure",         [54,  174, 191]],
    [40, "Light Aqua",           [173, 195, 192]],
    [41, "Olive Green",          [155, 154, 90 ]],
    [42, "Chrome Gold",          [187, 165, 61 ]],
    [43, "Sand Green",           [160, 188, 172]],
    [44, "Sand Blue",            [96,  116, 161]],
    [45, "Chrome Silver",        [224, 224, 224]],
    [46, "Dark Orange",          [169, 85,  0  ]],
    [47, "Glow in Dark White",   [217, 217, 217]],
    [48, "Coral",                [255, 105, 143]],
    [49, "Vibrant Yellow",       [235, 216, 0  ]],
    [50, "Medium Brown",         [117, 89,  69 ]],
    [51, "Warm Tan",             [204, 163, 115]],
    [52, "Pearl Titanium",       [62,  60,  57 ]],
    [53, "Reddish Orange",       [202, 76,  11 ]],
]

PALETTE = np.array([c[2] for c in lego_colors_list], dtype=np.uint8)

# =====================================================
# CONFIG
# =====================================================
GRID     = 64       # keep it manageable
BLOCKS   = 600      # LOTS of blocks so canvas is fully covered
POP      = 30
GENS     = 600
MUT_RATE = 0.15     # lower mutation = solutions survive longer
ELITE_K  = 5

# =====================================================
# LOAD + RESIZE IMAGE
# =====================================================
def load_image(path):
    img = cv2.imread(path)
    if img is None:
        raise FileNotFoundError(f"Could not load: {path}")
    img = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
    img = cv2.resize(img, (GRID, GRID))
    return img

# snap a pixel to the nearest lego color
def closest_color(pixel):
    diffs = np.sum((PALETTE.astype(np.float32) - np.array(pixel, dtype=np.float32)) ** 2, axis=1)
    return int(np.argmin(diffs))

# convert the whole target to lego-quantized colors up front
# this is what we're actually trying to match
def quantize_to_lego(target):
    h, w = target.shape[:2]
    quantized = np.zeros_like(target)
    for y in range(h):
        for x in range(w):
            idx = closest_color(target[y, x])
            quantized[y, x] = PALETTE[idx]
    return quantized

# =====================================================
# GENOME -- each block covers a tile on a grid
# KEY FIX: use a TILE-based approach so the whole canvas
# is guaranteed to be covered with no black gaps
# =====================================================

TILE = 4  # each lego "stud" is 4x4 pixels
TILES_X = GRID // TILE
TILES_Y = GRID // TILE

class Genome:
    def __init__(self, target_quantized=None):
        # one color per tile -- this guarantees full coverage, no black gaps
        num_tiles = TILES_X * TILES_Y
        if target_quantized is not None:
            # init each tile to the dominant lego color in that tile region
            self.tiles = []
            for ty in range(TILES_Y):
                for tx in range(TILES_X):
                    py = ty * TILE + TILE // 2
                    px = tx * TILE + TILE // 2
                    py = min(py, GRID - 1)
                    px = min(px, GRID - 1)
                    c = closest_color(target_quantized[py, px])
                    self.tiles.append(c)
        else:
            self.tiles = [random.randint(0, len(PALETTE) - 1) for _ in range(num_tiles)]

        self.fitness = float("inf")

    def render(self):
        img = np.zeros((GRID, GRID, 3), dtype=np.uint8)
        idx = 0
        for ty in range(TILES_Y):
            for tx in range(TILES_X):
                color = PALETTE[self.tiles[idx]]
                y1 = ty * TILE
                x1 = tx * TILE
                y2 = min(GRID, y1 + TILE)
                x2 = min(GRID, x1 + TILE)
                img[y1:y2, x1:x2] = color
                idx += 1
        return img

    def mutate(self, generation=0):
        for i in range(len(self.tiles)):
            if random.random() < MUT_RATE:
                # 20% big jump, 80% small nudge
                if random.random() < 0.2:
                    self.tiles[i] = random.randint(0, len(PALETTE) - 1)
                else:
                    self.tiles[i] = max(0, min(len(PALETTE) - 1,
                                               self.tiles[i] + random.randint(-2, 2)))

    def crossover(self, other):
        child = Genome()
        # single-point crossover
        cut = random.randint(0, len(self.tiles) - 1)
        child.tiles = self.tiles[:cut] + other.tiles[cut:]
        return child


# =====================================================
# FITNESS
# =====================================================
def calc_fitness(genome, target):
    rendered = genome.render()
    mse = np.mean((rendered.astype(np.float32) - target.astype(np.float32)) ** 2)
    return mse


# =====================================================
# TOURNAMENT SELECTION
# =====================================================
def tournament_select(pop, k=4):
    contestants = random.sample(pop, k)
    contestants.sort(key=lambda x: x.fitness)
    return contestants[0]


# =====================================================
# GA LOOP
# =====================================================
def run(target, target_quantized):
    pop = [Genome(target_quantized=target_quantized) for _ in range(POP)]
    best_ever = None

    for gen in range(GENS):
        for p in pop:
            p.fitness = calc_fitness(p, target)

        pop.sort(key=lambda x: x.fitness)

        if best_ever is None or pop[0].fitness < best_ever.fitness:
            best_ever = Genome()
            best_ever.tiles = pop[0].tiles[:]
            best_ever.fitness = pop[0].fitness

        if gen % 50 == 0:
            print(f"Gen {gen:4d}  |  MSE: {pop[0].fitness:.2f}  |  Best: {best_ever.fitness:.2f}")

        # elitism
        new_pop = []
        for i in range(ELITE_K):
            e = Genome()
            e.tiles = pop[i].tiles[:]
            e.fitness = pop[i].fitness
            new_pop.append(e)

        while len(new_pop) < POP:
            p1 = tournament_select(pop[:15])
            p2 = tournament_select(pop[:15])
            child = p1.crossover(p2)
            child.mutate(generation=gen)
            new_pop.append(child)

        pop = new_pop

    return best_ever


# =====================================================
# RUN
# =====================================================
target = load_image("animal.jpg")
print("Quantizing target to LEGO colors... (this takes a moment)")
target_quantized = quantize_to_lego(target)

print(f"Running GA: {GENS} generations, {TILES_X}x{TILES_Y} tile grid, {len(PALETTE)} colors")
best = run(target, target_quantized)

result = best.render()

# save outputs
cv2.imwrite("AnimalImage.jpg", cv2.cvtColor(result, cv2.COLOR_RGB2BGR))

# 10x upscale -- nearest neighbor keeps crisp lego stud edges
final_img1 = cv2.resize(result, (0, 0), fx=10, fy=10, interpolation=cv2.INTER_NEAREST)
cv2.imwrite("AnimalImage_big.jpg", cv2.cvtColor(final_img1, cv2.COLOR_RGB2BGR))

print("Done! Saved AnimalImage.jpg and AnimalImage_big.jpg")