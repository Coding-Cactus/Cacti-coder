from math import ceil
from math import floor

from random import choice
from random import shuffle
from random import randint

def challenge_1():
	invalid = randint(100, 400)
	passwords = []
	
	for i in range(1000):
		password = []

		if i < invalid:
			correct_things = [choice([True, False]), choice([True, False]), choice([True, False])]
			while False not in correct_things:			
				correct_things = [choice([True, False]), choice([True, False]), choice([True, False])]
	
			if correct_things[0]:
				length = 10
			else:
				length = choice([randint(6, 9), randint(11, 14)])				
	
			if correct_things[1]:
				numbers = 3
			else:
				numbers = choice([randint(0, 2), randint(4, length)])				
				
			if correct_things[2]:
				if length - numbers <= 2:
					caps = length - numbers
				else:
					caps = randint(2, length - numbers)
			else:
				caps = randint(0, 1)
				if length - numbers - caps < 0:
					caps = length - numbers				
	
			lowers = length - numbers - caps
		else:
			length = 10
			numbers = 3
			caps = randint(2, length-numbers)
			lowers = length - numbers - caps
			
		for n in range(numbers):
			password.append(str(randint(0, 9)))

		for n in range(caps):
			password.append(chr(randint(65, 90)))

		for n in range(lowers):
			password.append(chr(randint(97, 122)))


		shuffle(password)
		passwords.append("".join(password))

	shuffle(passwords)
	return invalid, passwords

def challenge_2():
	nums = []
	for i in range(1000):
		nums.append(randint(75, 200))

	average = sum(nums)/len(nums)

	sorted_nums = sorted(nums)
	min_num = sorted_nums[0]
	max_num = sorted_nums[-1]
	diff = max([ceil(average) - min_num, max_num - floor(average)])

	if choice([False, True]):
		fraud = average + randint(diff+10, diff+50)
	else:
		fraud = average - randint(diff+10, diff+50)

	line_num = randint(1, len(nums))

	nums.insert(line_num-1, fraud)

	return line_num, list(map(str, nums))

def challenge_3():
	counts = []
	used_counts = []
	
	modal_freq = randint(25, 50)
	modal_count = ""
	for i in range(randint(3, 10)*2):
		modal_count += chr(randint(97, 122))

	counts += [modal_count] * modal_freq

	modal_num = 0
	for i in range(int(len(modal_count)/2)):
		modal_num += (ord(modal_count[i]) - 96) * (ord(modal_count[-1*(i+1)]) - 96)
	used_counts.append(modal_num)

	while len(counts) < 1000:
		spine_num = used_counts[-1]
		while spine_num in used_counts:
			if len(counts) > 1000 - modal_freq:
				freq = 1000 - len(counts)
			else:
				freq = randint(1, modal_freq-1)
				
			spine_count = ""
			for i in range(randint(3, 10)*2):
				spine_count += chr(randint(97, 122))

				spine_num = 0
				for i in range(int(len(spine_count)/2)):
					spine_num += (ord(spine_count[i]) - 96) * (ord(spine_count[-1*(i+1)]) - 96)
		
		counts += [spine_count] * freq	
		used_counts.append(spine_num)

	shuffle(counts)
	return modal_num, counts

def challenge_4():
	grid = [[None for __ in range(32)] for _ in range(32)]

	super_cacti = randint(50, 200)

	for i in range(super_cacti):
		x, y = randint(1, 30), randint(1, 30)

		while grid[y][x]:
			x, y = randint(1, 30), randint(1, 30)


		grid[y][x] = randint(500, 5000)

		grid[y-1][x] = randint(1, 499)
		grid[y][x+1] = randint(1, 499)
		grid[y+1][x] = randint(1, 499)
		grid[y][x-1] = randint(1, 499)

	for y in range(len(grid)):
		for x in range(len(grid[y])):
			if not grid[y][x]:
				grid[y][x] = randint(500, 5000)
				
	super_cacti = 0
	for y in range(len(grid)):
		if y == 0 or y == 31: continue
		for x in range(len(grid[y])):
			if x == 0 or x == 31: continue
			if grid[y-1][x] < 500 and grid[y][x+1] < 500 and grid[y+1][x] < 500 and grid[y][x-1] < 500:
				super_cacti += 1

	for y in range(len(grid)):
		grid[y] = ",".join(list(map(str, grid[y])))

	return super_cacti, grid