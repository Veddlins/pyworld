import pygame
import random
from PIL import Image

pygame.init()

size = [900, 900]
res_scale = 1
res = [i//res_scale for i in size]

cam_x, cam_y = 0, 0

window = pygame.display.set_mode(size)
screen = pygame.transform.scale(window, res)

clock = pygame.time.Clock()

chunk_size = 8
tile_size = 16

textures = {0: [pygame.image.load('0.png')],
			1: [pygame.image.load('1.png')]}
textures2 = {0: [],
			 1: [pygame.image.load('obeddom.png')]}

world_size_block_x = 128
world_size_block_y = 128


world_size_chunk_x = 100//chunk_size
world_size_chunk_y = 100//chunk_size

world_map = Image.open('world.png')
world_map = world_map.resize((world_size_block_x, world_size_block_y), Image.ANTIALIAS)
world_map = world_map.load()

perlin_noise = Image.open('perlin_noise.png')
perlin_noise = perlin_noise.resize((world_size_block_x, world_size_block_y), Image.ANTIALIAS)
perlin_noise = perlin_noise.load()
noice_scroll_x = random.randint(0, world_size_block_x)
noice_scroll_y = random.randint(0, world_size_block_y)

def get_block_frommap(block_x, block_y):
	return((world_map[block_x, block_y][0]/255) + (perlin_noise[(block_x+noice_scroll_x)%world_size_block_x, (block_y+noice_scroll_y)%world_size_block_y][0]/255))

spawn_x, spawn_y = random.randint(0, world_size_block_x-1), random.randint(0, world_size_block_y-1)
while get_block_frommap(spawn_x, spawn_y) < 0.5:
	spawn_x, spawn_y = random.randint(0, world_size_block_x-1), random.randint(0, world_size_block_y-1)
cam_x = spawn_x*tile_size - res[0]//2
cam_y = spawn_y*tile_size - res[1]//2


def point_to_tile(x, y):
	tile_x = x//tile_size
	tile_y = y//tile_size

	return [tile_x, tile_y]

def chunk_finder(x, y):
	tile_gx, tile_gy = point_to_tile(x, y)[0], point_to_tile(x, y)[1]


	tile_x = int(tile_gx%chunk_size)
	tile_y = int(tile_gy%chunk_size)

	chunk_x = int(tile_gx//chunk_size)
	chunk_y = int(tile_gx//chunk_size)
	if (chunk_x < 0 or chunk_y < 0) or (chunk_x > world_size_chunk_x-1 or chunk_y > world_size_chunk_y-1):
		return None

	return [tile_x, tile_y, chunk_x, chunk_y]

def replace_chunk(pos, tile_type):
	tile_data = chunk_finder(*pos)
	chunk = chunks[tile_data[2]+tile_data[3]*world_size_chunk_x]
	chunk.map[tile_data[0]+tile_data[1]*chunk_size] = tile_type

def chunks_on_screen():
	x1 = cam_pl_x // (chunk_size*tile_size)
	y1 = cam_pl_y // (chunk_size*tile_size)

	x2 = (cam_x+res[0]) // (chunk_size*tile_size)
	y2 = (cam_y+res[1]) // (chunk_size*tile_size)


	x1 = round(min(max(x1, 0), world_size_chunk_x-1))
	x2 = round(min(max(x2, 0), world_size_chunk_x-1))

	y1 = round(min(max(y1, 0), world_size_chunk_y-1))
	y2 = round(min(max(y2, 0), world_size_chunk_y-1))

	result = []
	for y in range(y1, y2+1):
		for x in range(x1, x2+1):
			result.append(x+y*world_size_chunk_x)

	return result

def generate_tile(x, y, chunk_x, chunk_y):
	tile_x = (chunk_x//tile_size)+x
	tile_y = (chunk_y//tile_size)+y

	ground = int(world_map[tile_x, tile_y][0]/255 > 0.5)
	ground = int(get_block_frommap(tile_x, tile_y) > 0.5)

	spawn = (tile_x == spawn_x and tile_y == spawn_y)

	if ground:
		if spawn:
			 return [1, 1]
		else:
			return[1, 0]
	else:
		return[0, 0]

class Chunk:
	def __init__(self, x, y):
		self.x, self.y = x, y
		self.map = []
		self.map2 = []
		for y in range(chunk_size):
			for x in range(chunk_size):
				tile_data = generate_tile(x, y, self.x, self.y)
				self.map.append(tile_data[0])
				self.map2.append(tile_data[1])

	def render(self):
		for y in range(chunk_size):
			for x in range(chunk_size):
				texture = textures[self.map[x+y*chunk_size]][0]
				if self.map2[x+y*chunk_size] != 0: 
						texture2 = textures2[self.map2[x+y*chunk_size]][0]	
				screen.blit(texture, (round(self.x+x*tile_size - cam_pl_x), round(self.y+y*tile_size - cam_pl_y)))
				if self.map2[x+y*chunk_size] != 0: 
						screen.blit(texture2, (round(self.x+x*tile_size - cam_pl_x), round(self.y+y*tile_size - cam_pl_y)))




chunks = []
for y in range(world_size_chunk_y):
	for x in range(world_size_chunk_x):
		chunks.append(Chunk(x*chunk_size*tile_size, y*chunk_size*tile_size))

cam_pl_x = cam_x
cam_pl_y = cam_y

frame = 0
while 1:
	screen.fill((0, 0, 0))
	for event in pygame.event.get():
		if event.type == pygame.QUIT:
			exit()
#выведение в консоли координат чанка при нажатии и его замена
		if event.type == pygame.MOUSEBUTTONDOWN:
			pos = [pygame.mouse.get_pos()[0]/res_scale+cam_pl_x, pygame.mouse.get_pos()[1]/res_scale+cam_pl_y]
			if event.button == 1:
				print('Курсор на координатах:', chunk_finder(*pos))
				if chunk_finder(*pos) != None:
					replace_chunk(pos, 1)
			if event.button == 3:
				print('Курсор на координатах:', chunk_finder(*pos))
				if chunk_finder(*pos) != None:
					replace_chunk(pos, 0)

#управление на WASD
 
	key = pygame.key.get_pressed()
	if key[pygame.K_a]:
		cam_x -= 5
	if key[pygame.K_d]:
		cam_x += 5
	if key[pygame.K_w]:
		cam_y -= 5
	if key[pygame.K_s]:
		cam_y += 5

	for i in chunks_on_screen():
		chunks[i].render()

	window.blit(pygame.transform.scale(screen, size), (0, 0))
	pygame.display.update()
	clock.tick(300)

	cam_pl_x += (cam_x-cam_pl_x)//10
	cam_pl_y += (cam_y-cam_pl_y)//10

	frame += 1
	if frame%100 == 0:
		pygame.display.set_caption('FPS: '+str(round(clock.get_fps())))
		chunks_on_screen()
