import cv2
import numpy as np
import random

# list of colours that are offered as lego pieces referneces https://rebrickable.com/colors/
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
    [53, "Reddish Orange", [202, 76, 11]],
    [54, "Royal Blue", [76, 97, 219]],
    [55, "Maersk Blue", [53, 146, 195]],
    [56, "Chrome Green", [60, 179, 113]],
    [57, "Opal Trans-Bright Green", [132, 182, 141]],
    [58, "Modulex Lemon", [189, 198, 24]],
    [59, "Salmon", [242, 112, 94]],
    [60, "Modulex Light Gray", [156, 156, 156]],
    [61, "Vintage Yellow", [243, 195, 5]]

]

# Helps with colour grouping by using K-clustering
def kcluster_color(img, k=15):
    data = img.reshape((-1, 3))
    data = np.float32(data) #conversion to float  for grouping calculations
    criteria = (cv2.TERM_CRITERIA_EPS + + cv2.TERM_CRITERIA_MAX_ITER, 10, 1.0)
    _, labels, centers = cv2.kmeans(data, k, None, criteria, 10, cv2.KMEANS_RANDOM_CENTERS)

    centers = np.uint8(centers) #conversion back
    result = centers[labels.flatten()]
    result = result.reshape(img.shape)
    return result

# Converting the image into a pixelated form but processes image a bit first
def pixelate(img, scale=0.04):
    img = cv2.convertScaleAbs(img, alpha=1.5, beta=-25) #contrast increase

    img = cv2.bilateralFilter(img, 9, 75, 75) #blur

    edges = cv2.Canny(img, 100, 200)

    img = kcluster_color(img, k=8)

    img_low_res = cv2.resize(img, (32, 32))
    return img_low_res, edges

# calculating the difference between image colour and database colour
def color_difference(color1, color2):
    c1 = [int(x) for x in color1]
    c2 = [int(x) for x in color2]

    dR = c1[0] - c2[0]
    dG = c1[1] - c2[1]
    dB = c1[2] - c2[2]

    return 2* dR * dR + 4*dG * dG + 3*dB * dB

# determing what colour works best based on colour difference (greedy)
def best_color_match(color_rgb, color_pallete=lego_colors_list):
    best_color = None
    d_minimum = None
    for p in color_pallete:
        d = color_difference(color_rgb, p[2])
        d += sum(p[2]) * 0.1 #pushes higher contrast
        if d_minimum is None or d_minimum > d:
            d_minimum = d
            best_color = p
    return best_color

# generating the actual "lego" pixelated image
def lego_maker(pixel_img):
    lego_img = np.zeros(pixel_img.shape, dtype=np.uint8)

    for row in range(len(pixel_img)):
        for col in range(len(pixel_img[0])):
            r = pixel_img[row][col][2]
            g = pixel_img[row][col][1]
            b = pixel_img[row][col][0]
            pixel_rgb = (r, g, b)

            match_color = best_color_match(pixel_rgb)
            match_color_rgb = match_color[2]
            lego_img[row][col][0] = match_color_rgb[2]
            lego_img[row][col][1] = match_color_rgb[1]
            lego_img[row][col][2] = match_color_rgb[0]

    return lego_img

def filter_colors(img):
    h, w, _ = img.shape
    new_img = img.copy()

    for row in range(1, h - 1):
        for col in range(1, w - 1):
            neighbors = []

            for dr in [-1, 0, 1]:
                for dc in [-1, 0, 1]:
                    neighbors.append(tuple(img[row + dr][col + dc]))

            most_common = max(set(neighbors), key=neighbors.count)

            # ONLY replace if strong agreement (>=5 out of 9)
            if neighbors.count(most_common) >= 6:
                new_img[row][col] = most_common

    return new_img


def create_genome(unique_colors, size=1024):
    '''
    Basically Creating a list of 1024 elements with unique numbers from list of unique_colors 
    and mentioning its index in the genome list 
    '''
    genome = []  
    for i in range(size): 
        # Choosing a random color
        random_color_index = random.randint(0, len(unique_colors) - 1)
        # adding random color index to the genome
        genome.append(random_color_index)

    return genome


def create_population(size, unique_colors):
    ''' Creating Multiple Genomes to get our generation'''
    new_population = []
    for i in range(size):
        individual = create_genome(unique_colors)
        new_population.append(individual)
    return new_population


def get_fitness(genome, target_img, unique_colors):
    '''Creating a image from our genome and then comparing with our original image to get a error score'''
    
    '''1st Part: Creating a Image from Genome'''
    
    candidate_img = np.zeros((32, 32, 3), dtype=np.uint8) 
    for i in range(1024):
        row = i // 32 #Tells the Row Number
        col = i % 32  #tells the colmn Number
        
        color_id = genome[i]
        # Get the BGR values from unique_colors
        b, g, r = unique_colors[color_id]
        # Put it in the image
        candidate_img[row, col] = [b, g, r]

    """2nd part: Comparing the generated image with original image calculating the score"""
    total_error = 0
    for row in range(32):
        for col in range(32):
            pixel_target = target_img[row, col]
            pixel_candidate = candidate_img[row, col]
            diff_b = abs(int(pixel_target[0]) - int(pixel_candidate[0]))
            diff_g = abs(int(pixel_target[1]) - int(pixel_candidate[1]))
            diff_r = abs(int(pixel_target[2]) - int(pixel_candidate[2]))
            total_error = total_error + diff_b + diff_g + diff_r
            #total error range can be = size(1024 here) * (b_error(0-255) + g_error(0-255) + r_error(0-255))
    return total_error

def crossover(parent1, parent2):
    '''Combining good parts of two parents from random point'''
    # Pick a random point to cut the 1024-gene list
    cut_point = random.randint(0, 1023)
    # Take the start from parent1 and the rest from parent2
    child = parent1[:cut_point] + parent2[cut_point:]
    return child


def mutate(genome, unique_colors, chance=0.01):
    '''Randomly changeing 1% of the genome pixel to another color from unique_colors'''
    
    for i in range(1024):
        
        if random.random() < chance:
            genome[i] = random.randint(0, len(unique_colors) - 1)
    return genome

def create_next_gen(scored_pop, unique_colors):
    '''Evouling a next generation via choosing best genomes from previous generations and evolving them using mutation and crossover'''
    new_gen = []
    #using top few genomes as it is
    elite_count = 5
    for i in range(elite_count):
        elite_genome = scored_pop[i][1]
        new_gen.append(elite_genome)
    
    #Choosing rest by evolving
    while len(new_gen) < 100:
        # Randomly picking two parents from top 20 or 30 parents
        parent_a = random.choice(scored_pop[:20])[1] # 20 ->30
        parent_b = random.choice(scored_pop[:20])[1] # 20 ->30
    
        child = crossover(parent_a, parent_b)
    
        child = mutate(child, unique_colors)
        new_gen.append(child)
    return new_gen

def run_generator(img):
    img_low_res, edges = pixelate(img)
    edges_small = cv2.resize(edges, (32, 32))

    final_img = lego_maker(img_low_res)
    final_img = filter_colors(final_img)
    # all the Unique colors present in image to make generations easier and faster
    # uniqueColors = [[b,g,r], [b,g,r] .... length(n-2) , [b,g,r]]
    unique_colors = np.unique(final_img.reshape(-1, 3), axis=0)

    # cv2.imwrite("SimplifiedColorsImage.jpg" ,final_img)

    num_generations = 10000
    current_population = create_population(100, unique_colors)
    print("Starting Evoulation please wait.")

    best_genome = None

    for gen in range(num_generations):
        # scoring everyone here
        scored_pop = []
        for individual in current_population:
            score = get_fitness(individual, final_img, unique_colors)
            scored_pop.append((score, individual))
        # sorting the scored_population
        scored_pop.sort(key=lambda x: x[0])
        # UserFeedback so that they know code is running
        if gen % 500 == 0:
            print(f"Generation {gen} & Current Error: {scored_pop[0][0]}")
        # Creat Next Generation
        current_population = create_next_gen(scored_pop, unique_colors)

        # Final Preview of Results
        print("Evolution finished!")
        best_genome = scored_pop[0][1]
    final_result_img = np.zeros((32, 32, 3), dtype=np.uint8)
    for i in range(1024):
        row = i // 32
        col = i % 32
        b, g, r = unique_colors[best_genome[i]]
        final_result_img[row, col] = [b, g, r]

    big_final = cv2.resize(final_result_img, (400, 400), interpolation=cv2.INTER_NEAREST)
    #cv2.imwrite("FinalResults.jpg", big_final)
    #cv2.imwrite("ProcessedImage.jpg", cv2.resize(final_img, (400, 400), interpolation=cv2.INTER_NEAREST))
    final_img = cv2.resize(final_img, (400, 400), interpolation=cv2.INTER_NEAREST)
    return final_img

