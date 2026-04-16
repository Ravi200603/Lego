import cv2
import numpy as np
import random
lego_colors_list = [
    [1, "Black", [5, 19, 29]],
    [2, "Blue", [0, 85, 191]],
    [3, "Green", [35, 120, 65]],
    [4, "Dark Turquoise", [0, 143, 155]],
    [5, "Red", [201, 26, 9]],
    [6, "Dark Pink", [200, 112, 160]],
    [7, "Bright Green", [75, 159, 74]],
    [8, "Yellow", [242, 205, 55]],
    [9, "White", [255, 255, 255]],
    [10, "Tan", [228, 205, 158]],
    [11, "Orange", [254, 138, 24]],
    [12, "Magenta", [146, 57, 120]],
    [13, "Lime", [187, 233, 11]],
    [14, "Dark Tan", [149, 138, 115]],
    [15, "Bright Pink", [228, 173, 200]],
    [16, "Medium Lavender", [172, 120, 186]],
    [17, "Lavender", [225, 213, 237]],
    [18, "Reddish Brown", [88, 42, 18]],
    [19, "Light Bluish Gray", [160, 165, 169]],
    [20, "Dark Bluish Gray", [108, 110, 104]],
    [21, "Medium Blue", [90, 147, 219]],
    [22, "Light Nougat", [246, 215, 179]],
    [23, "Metallic Silver", [165, 169, 180]],
    [24, "Metallic Gold", [219, 172, 52]],
    [25, "Medium Nougat", [170, 125, 85]],
    [26, "Dark Purple", [63, 54, 145]],
    [27, "Nougat", [208, 145, 104]],
    [28, "Yellowish Green", [223, 238, 165]],
    [29, "Flat Silver", [137, 135, 136]],
    [30, "Bright Light Orange", [248, 187, 61]],
    [31, "Bright Light Blue", [159, 195, 233]],
    [32, "Bright Light Yellow", [255, 240, 58]],
    [33, "Dark Blue", [10, 52, 99]],
    [34, "Dark Green", [24, 70, 50]],
    [35, "Pearl Gold", [170, 127, 46]],
    [36, "Dark Brown", [53, 33, 0]],
    [37, "Dark Red", [114, 14, 15]],
    [38, "Dark Azure", [7, 139, 201]],
    [39, "Medium Azure", [54, 174, 191]],
    [40, "Light Aqua", [173, 195, 192]],
    [41, "Olive Green", [155, 154, 90]],
    [42, "Chrome Gold", [187, 165, 61]],
    [43, "Sand Green", [160, 188, 172]],
    [44, "Sand Blue", [96, 116, 161]],
    [45, "Chrome Silver", [224, 224, 224]],
    [46, "Dark Orange", [169, 85, 0]],
    [47, "Glow in Dark White", [217, 217, 217]],
    [48, "Coral", [255, 105, 143]],
    [49, "Vibrant Yellow", [235, 216, 0]],
    [50, "Medium Brown", [117, 89, 69]],
    [51, "Warm Tan", [204, 163, 115]],
    [52, "Pearl Titanium", [62, 60, 57]],
    [53, "Reddish Orange", [202, 76, 11]]
]
def pixelate(image_path):
    img = cv2.imread(image_path)
    
    img_low_res = cv2.resize(img, (16,16))
    
    return img_low_res

def color_difference(color1, color2):
    c1 = [int(x) for x in color1]
    c2 = [int(x) for x in color2]

    dR = c1[0] - c2[0]
    dG = c1[1] - c2[1]
    dB = c1[2] - c2[2]

    return (dR**2 + dG**2 + dB**2) ** 0.5

def best_color_match(color_rgb, color_pallete = lego_colors_list):
    best_color = None
    d_minimum = None
    for p in color_pallete:
        d = color_difference(color_rgb, p[2])
        if d_minimum is None or d_minimum > d:
            d_minimum = d
            best_color = p
    return best_color

def lego_maker(pixel_img):
    lego_img = np.zeros(pixel_img.shape, dtype = np.uint8)
    
    for row in range(len(pixel_img)):
        for col in range(len(pixel_img[0])):
            
            r = pixel_img[row][col][2]
            g = pixel_img[row][col][1]
            b = pixel_img[row][col][0]
            pixel_rgb =  (r,g,b)
            
            match_color =  best_color_match(pixel_rgb)
            match_color_rgb = match_color[2]
            
            lego_img[row][col][0] = match_color_rgb[2]
            lego_img[row][col][1] = match_color_rgb[1]
            lego_img[row][col][2] = match_color_rgb[0]
    return lego_img

img_low_res = pixelate('owl.jpg')


final_img = lego_maker(img_low_res)

# cv2.imshow("AnimalImage", final_img)
# cv2.waitKey(0)


colors = [c[2] for c in lego_colors_list]

def create_genome(size=256):
    """
    Creates a single 'DNA' string.
    A list of 256 random numbers between 0 and 52.
    """
    genome = [random.randint(0, 52) for _ in range(size)]
    return genome

def create_population(size):
    # Start with an empty list to hold our 100 individuals
    new_population = []
    
    # Loop 100 times
    for i in range(size):
        # 1. Create one random genome (256 numbers)
        individual = create_genome()
        
        # 2. Add that individual to our population list
        new_population.append(individual)
        
    # Return the full list of 100 genomes
    return new_population

# Create the starting group
population = create_population(100)


def get_fitness(genome, target_img):
    # STEP 1: Turn the list of numbers into an image we can see
    # Create a blank 16x16 black square
    candidate_img = np.zeros((16, 16, 3), dtype=np.uint8)
    
    for i in range(256):
        row = i // 16
        col = i % 16
        
        # Get the color index from our genome
        color_id = genome[i]
        # Get the RGB values we saved earlier
        r, g, b = colors[color_id]
        
        # Put it in the image (remembering BGR for OpenCV)
        candidate_img[row, col] = [b, g, r]

    # STEP 2: Compare our new image to the fox image
    total_error = 0
    
    # Go through every row and every column
    for r in range(16):
        for c in range(16):
            # Get the color of the pixel from both images
            pixel_target = target_img[r, c]
            pixel_candidate = candidate_img[r, c]
            
            # Calculate the difference for Blue, Green, and Red
            # we use 'abs' to make sure the difference is always a positive number
            diff_b = abs(int(pixel_target[0]) - int(pixel_candidate[0]))
            diff_g = abs(int(pixel_target[1]) - int(pixel_candidate[1]))
            diff_r = abs(int(pixel_target[2]) - int(pixel_candidate[2]))
            
            # Add these differences to our total error
            total_error = total_error + diff_b + diff_g + diff_r
            
    return total_error

def crossover(parent1, parent2):
    # Pick a random point to cut the 256-gene list
    cut_point = random.randint(0, 255)
    
    # Take the start from parent1 and the rest from parent2
    child = parent1[:cut_point] + parent2[cut_point:]
    
    return child

def mutate(genome, chance=0.01):
    # Go through every brick in the 256 list
    for i in range(256):
        # 0.01 means a 1% chance to change this specific brick
        if random.random() < chance:
            genome[i] = random.randint(0, 52)
            
    return genome

def create_next_gen(scored_pop):
    new_gen = []
    
    # 1. Keep the Best (Elite)
    # scored_pop[0][1] is the genome of the best-scoring individual
    best_genome = scored_pop[0][1]
    new_gen.append(best_genome)
    
    # 2. Fill the rest of the 99 spots
    while len(new_gen) < 100:
        # Pick two parents from the Top 20
        parent_a = random.choice(scored_pop[:20])[1]
        parent_b = random.choice(scored_pop[:20])[1]
        
        # Mix them
        child = crossover(parent_a, parent_b)
        
        # Tweak them
        child = mutate(child)
        
        new_gen.append(child)
        
    return new_gen

# 1. Setup
num_generations = 10000 # Increased for better results
current_population = create_population(100)

print("Evolution starting... please wait.")

for gen in range(num_generations):
    # A. Score everyone
    scored_pop = []
    for individual in current_population:
        score = get_fitness(individual, final_img)
        scored_pop.append((score, individual))
    
    # B. Sort them
    scored_pop.sort(key=lambda x: x[0])
    
    # C. Print progress to terminal (no images yet)
    if gen % 500 == 0:
        print(f"Generation {gen} | Current Error: {scored_pop[0][0]}")

    # D. Breed the next generation
    current_population = create_next_gen(scored_pop)

# --- FINAL RESULT PREVIEW ---
print("Evolution finished! Rendering final image...")

# Get the #1 best genome from the final population
best_genome = scored_pop[0][1]
final_result_img = np.zeros((16, 16, 3), dtype=np.uint8)

for i in range(256):
    row, col = i // 16, i % 16
    r, g, b = colors[best_genome[i]]
    final_result_img[row, col] = [b, g, r]

# Make it big so we can actually see it
big_final = cv2.resize(final_result_img, (400, 400), interpolation=cv2.INTER_NEAREST)

cv2.imshow("Final Fox Result", big_final)
cv2.imshow("Original Target", cv2.resize(final_img, (400, 400), interpolation=cv2.INTER_NEAREST))

print("Press any key on the image window to close.")
cv2.waitKey(0)
cv2.destroyAllWindows()