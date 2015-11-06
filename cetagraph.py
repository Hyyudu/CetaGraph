#!coding=utf-8

from OpenGL.GL import *
from OpenGL.GLU import *
from OpenGL.GLUT import *
from random import *

import sys, math

def get_view_angle(dx, dy):
	print("Calculating view_angle from "+str((dx, dy)))
	if dx==0:
		ret= 90 if dy>0 else -90
	else:
		ret= 180-math.atan(dy*1.0/dx)*180/math.pi
	print("view_angle="+str(ret))
	return ret-90

def get_tangage(rad, dz):
	print("Calculating tangage from "+str((rad, dz)))
	if rad == 0:
		ret = 90 if dz>0 else -90;
	else:
		ret = math.atan(dz*1.0/rad)*180/math.pi
	print("tangage = "+str(ret))
	return ret
 
class CetaGraph():

	ortho = 0
	mult = 1.5
	# links between planets
	show_links = 0
	speed=2
	accel = 4
	sizes = {
			# planet radius
			"sphere_radius": 30,
			# relative size of ships to planets
			"ship_scale": 0.02,
			# relative sizes of ships to each other
			"scales":	{
				"transport": 6,
				"station": 7,
				"scout": 3,
				"cruiser": 12,
				"battleship": 16
			},
			"orbit_min_radius": 1.2,
			"orbit_max_radius": 1.4,
			"orbit_min_height": -0.2,
			"orbit_max_height": 0.2,
			"pw_min_height": 0.9,
			"pw_max_height": 1.4,
			"pw_min_radius": 0.7,
			"pw_max_radius": 1.8
		}
	sizes['astro_unit'] = sizes['sphere_radius']*5

	view_angle = 45
	camera_x = 0
	camera_y = 0
	camera_z = 0
	camera_tangage = 0

	fleet_colors = {
		'cetaganda': 'ffffff',
		'barrayar': 'f71015',
		'earth': '00fcff',
		'beta': 'e400ff',
 		'vervan': 'ffde00',
		'illirika': 'ff9601',
		'hegen_hub': 'cb79ff'
	}

	planet_colors = {
		"R" :'580404',
		"r" :'af7777',
		"G" :'083a00',
		"g" :'67955f',
		"Y" :'5b3405',
		"y" :'feff85',
		"B" :'1a2f72',
		"b" :'6777aa',
		"w" :'bebec0',
		'q': '999999' #eta kita
	}

	def html2rgb(self, html):
		html = html.strip()
		if html[0] == '#': html = html[1:]
		return (int(html[0:2], 16), int(html[2:4], 16), int(html[4:6], 16))

	def setHtmlColor(self, html):
		glColor3d(*map(lambda x: x/255.0, self.html2rgb(html)))

	def InitGL(self, Width, Height):
		seed()
		glBlendFunc(GL_SRC_ALPHA, GL_ONE_MINUS_SRC_ALPHA);
		glEnable(GL_BLEND)
		 # Сглаживание точек
		glEnable(GL_POINT_SMOOTH)
		glHint(GL_POINT_SMOOTH_HINT, GL_NICEST)
		 # Сглаживание линий
		glEnable(GL_LINE_SMOOTH)
		glHint(GL_LINE_SMOOTH_HINT, GL_NICEST)
		 # Сглаживание полигонов
		glEnable(GL_POLYGON_SMOOTH)
		glHint(GL_POLYGON_SMOOTH_HINT, GL_NICEST)
		glClearColor(0.0, 0.0, 0.0, 0.0)
		glClearDepth(1.0)
		glDepthFunc(GL_LESS)
		glEnable(GL_DEPTH_TEST)
		glEnable(GL_LIGHTING)
		glEnable(GL_LIGHT0)
		glEnable(GL_COLOR_MATERIAL)
		glMatrixMode(GL_PROJECTION)
		glLoadIdentity()
		self.setView(Width, Height)
		glMatrixMode(GL_MODELVIEW)
		self.planets = self.get_planets()

		nations = self.fleet_colors.keys()

		#base position
		if self.look_from and self.look_to:
			from_data = self.planets[self.look_from]
			# self.planets[self.look_to]['color'] = 'rrr'
			print(from_data)
			self.camera_x = self.xval(from_data, True)
			self.camera_y = self.yval(from_data, True)
			self.camera_z = self.zval(from_data, True)
			to_data = self.planets[self.look_to]
			dx = to_data['x'] - from_data['x']
			dy = to_data['y'] - from_data['y']
			dz = to_data['z'] - from_data['z']
			print(dx, dy, dz)
			self.view_angle = get_view_angle(dx, dy)
			self.move(1,1, self.sizes['sphere_radius']* self.sizes['orbit_max_radius']*1.1)
			flat_radius = math.sqrt(dx**2 + dy**2)
			self.camera_tangage = get_tangage(flat_radius, dz)


		for ship in self.ships:
			if ship.get("nation") and self.fleet_colors.get(ship.get("nation")):
				ship['color'] = self.html2rgb(self.fleet_colors.get(ship.get("nation")))
			ship['rotating_angle'] = randint(0, 359)
			sizes = self.sizes
			loc = ship['location']+'_'
			ship['orbit_diameter'] = triangular(sizes[loc+'min_radius'], sizes[loc+'max_radius'])*sizes['sphere_radius']*self.mult
			ship['vertical_offset'] = triangular(sizes[loc+'min_height'], sizes[loc+'max_height'])*sizes['sphere_radius']*self.mult
			if ship['type'] == 'station':
				ship['vertical_offset'] = -0.2*sizes['sphere_radius']*self.mult
				ship['orbit_diameter'] = sizes['sphere_radius']*self.mult




	def getval(self, data, coord, mult_au=False):
		if coord == 'x':
			val = data['x']
			camera = self.camera_x
		if coord == 'y':
			val = -data['z']
			camera = self.camera_y
		if coord == 'z':
			val = -data['y']
			camera = self.camera_z
		if mult_au: val *= self.sizes.get('astro_unit');
		return self.mult*val - camera;

	def xval(self, data, mult_au = False):
		return self.getval(data, 'x', mult_au)

	def yval(self, data, mult_au = False):
		return self.getval(data, 'y', mult_au)

	def zval(self, data, mult_au = False):
		return self.getval(data, 'z', mult_au)



	def setView(self, Width, Height):
		if self.ortho:
			glOrtho(-0, Width/10, 0, Height/10, -100, 1000)
		else:
			gluPerspective(45.0, float(Width)/float(Height), 0.1, 10000.0)

	def ReSizeGLScene(self,Width, Height):
		if Height == 0: Height = 1
		glViewport(0, 0, Width, Height)
		glMatrixMode(GL_PROJECTION)
		glLoadIdentity()
		self.setView(Width, Height)
		glMatrixMode(GL_MODELVIEW)

	def get_planets(self):
		return {
				"archipelag": {
					"planet_code": 23,
					"links": ['hegen_hub', 'klein', 'illirika'],
					"name": 'Архипелаг Джексона',
					"x": 3,
					"y": 7,
					"z": 3,
					"color": "RrY",
				},
				"barrayar": {
					"planet_code": 7,
					"links": ['komarra'],
					"name": 'Барраяр',
					"x": 3,
					"y": 6,
					"z": 6,
					"color": "Rrg"
				},
				"beta": {
					"planet_code": 31,
					"links": ['dagula', 'eskobar', 'sergiyar'],
					"name": 'Колония Бета',
					"x": 7,
					"y": 3,
					"z": 3,
					"color": "ybw"
				},
				"vervan": {
					"planet_code": 15,
					"links": ['hegen_hub', 'illirika'],
					"name": 'Верван',
					"x": 0,
					"y": 6,
					"z": 2,
					"color": "Yyw"
				},
				"dagula": {
					"planet_code": 5,
					"links": ['hegen_hub', 'ksi_kita', 'marilak', 'earth', 'beta'],
					"name": 'Дагула',
					"x": 6,
					"y": 0,
					"z": 2,
					"color": "rBg"
				},
				"earth": {
					"planet_code": 1,
					"links": ['dagula', 'hegen_hub', 'sigma_kita', 'eskobar'],
					"name": 'Земля',
					"x": 3,
					"y": 3,
					"z": 3,
					"color": "bGw"
				},
				"sergiyar": {
					"planet_code": 29,
					"links": ['eskobar','beta', 'komarra'],
					"name": 'Сергияр',
					"x": 6,
					"y": 3,
					"z": 6,
					"color": "yBG"
				},
				"illirika": {
					"planet_code": 17,
					"links": ['vervan', 'archipelag', 'tau_kita'],
					"name": 'Иллирика',
					"x": 0,
					"y": 6,
					"z": 4,
					"color": "Rrw"
				},
				"klein": {
					"planet_code": 25,
					"links": ['archipelag', 'eskobar'],
					"name": 'Станция Клайн',
					"x": 6,
					"y": 6,
					"z": 2,
					"color": "YBg"
				},
				"komarra": {
					"planet_code": 3,
					"links": ['sergiyar', 'earth', 'tau_kita', 'ro_kita', 'barrayar'],
					"name": 'Комарра',
					"x": 3,
					"y": 3,
					"z": 7,
					"color": "bgw",
				},
				"ksi_kita": {
					"planet_code": 19,
					"links": ['sigma_kita','dagula', 'eta_kita'],
					"name": 'Кси Кита',
					"x": 0,
					"y": 0,
					"z": 2,
					"color": "BbG"
				},
				"marilak": {
					"planet_code": 35,
					"links": ['dagula', 'sigma_kita'],
					"name": 'Марилак',
					"x": 6,
					"y": 0,
					"z": 4,
					"color": "rYb"
				},
				"mu_kita": {
					"planet_code": 13,
					"links": ['hegen_hub', 'eta_kita'],
					"name": 'Мю Кита',
					"x": -1,
					"y": 3,
					"z": 3,
					"color": "RYy"
				},
				"ro_kita": {
					"planet_code": 9,
					"links": ['komarra', 'eta_kita'],
					"name": 'Ро Кита',
					"x": 3,
					"y": 0,
					"z": 6,
					"color": "RrB"
				},
				"sigma_kita": {
					"planet_code": 37,
					"links": ['earth', 'marilak', 'eta_kita', 'ksi_kita'],
					"name": 'Сигма Кита',
					"x": 3,
					"y": -1,
					"z": 3,
					"color": "YyG"
				},
				"tau_kita": {
					"planet_code": 33,
					"links": ['komarra', 'illirika'],
					"name": 'Тау Кита',
					"x": 0,
					"y": 3,
					"z": 6,
					"color": "Ggw"
				},
				"hegen_hub": {
					"planet_code": 21,
					"links": ['archipelag', 'vervan', 'mu_kita', 'earth', 'dagula'],
					"name": 'Хеген Хаб',
					"x": 3,
					"y": 3,
					"z": 0,
					"color": "yGg"
				},
				"eskobar": {
					"planet_code": 27,
					"links": ['klein', 'earth', 'beta', 'sergiyar'],
					"name": 'Эскобар',
					"x": 6,
					"y": 6,
					"z": 4,
					"color": "RBb"
				},
				"eta_kita": {
					"planet_code": 11,
					"links": ['mu_kita', 'sigma_kita', 'ksi_kita', 'ro_kita'],
					"name": 'Эта Кита',
					"x": 0,
					"y": 0,
					"z": 4,
					"color": "qqq"
				}
			}

	def draw_planets(self):
		planet_precision = 30
		torus_precision = 30
		size = self.sizes['sphere_radius']*self.mult;
		for name, data in self.planets.items():
			glPushMatrix()
			# Сдвигаемся в нужную точку
			glTranslatef(self.xval(data, mult_au = True), self.yval(data, mult_au=True), self.zval(data, mult_au = True))
			# Planet ball
			self.setHtmlColor(self.planet_colors[data['color'][0]])
			glutSolidSphere(size, planet_precision,planet_precision)
			# planet torus
			self.setHtmlColor(self.planet_colors[data['color'][1]])
			glRotatef(45,1,0,0)
			glutSolidTorus(size*0.3, size*0.75, torus_precision, torus_precision)
			self.setHtmlColor(self.planet_colors[data['color'][2]])
			glRotatef(90,1,0,0)
			glutSolidTorus(size*0.3, size*0.75, torus_precision, torus_precision)
			glPopMatrix()

			if self.show_links and data.get('links'):
				# planet links
				glColor(1,1,1)
				glBegin(GL_LINES)
				for link in data['links']:
					neighbour = self.planets[link]
					glVertex3d(self.xval(neighbour, True), self.yval(neighbour, True), self.zval(neighbour, True))
					glVertex3d(self.xval(data), self.yval(data, True), self.zval(data))
					print("making link between "+neighbour['name']+" and "+data['name'])
				glEnd()

	def get_example_ships(self):
		planet = 'earth'
		return [
		{
			"type": "transport",
			"planet": planet,
			"location": "pw",
			"nation": "cetaganda",
			"orbit_diameter": 0,
			"rotating_angle": 0
		},
		{
			"type": "scout",
			"planet": planet,
			"location": "pw",
			"nation": "earth",
		},
		{
			"type": "station",
			"planet": planet,
			"location": "pw",
			"nation": "vervan"
		},
		{
			"type": "cruiser",
			"planet": planet,
			"location": "pw",
			"nation": "beta"
		},
		{
			"type": "battleship",
			"planet": planet,
			"location": "pw",
			"nation": "barrayar"
		}
	]

	def draw_ships(self):
		for ship in self.ships:
			size = self.sizes['sphere_radius']*self.sizes['ship_scale']*self.sizes['scales'][ship['type']]*self.mult
			glPushMatrix()
			glColor(ship['color'][0]/255., ship['color'][1]/255., ship['color'][2]/255.)
			# Сдвигаемся в центр планеты
			planet = self.planets[ship['planet']]
			glTranslatef(self.xval(planet, True), self.yval(planet, True), self.zval(planet, True))
			angle = ship['rotating_angle']*math.pi/180
			# Смещаем на орбиту
			glTranslatef(math.sin(angle)*ship['orbit_diameter'], ship['vertical_offset'], math.cos(angle)*ship['orbit_diameter'])
			# Поворачиваем на угол
			glRotatef(ship['rotating_angle']+90, 0, 1, 0)
			if ship['type'] == 'scout':
				glutSolidSphere(size*0.45, 20,20)
				glRotatef(90,1,0,0)
				glutSolidTorus(size*0.3, size*0.6, 20, 20)
			if ship['type'] == 'transport':
				quadratic = gluNewQuadric()
				gluCylinder(quadratic, size*0.3, size*0.3, size*1.2, 20, 20)      # to draw the lateral parts of the cylinder;
				glutSolidSphere(size*0.3, 20, 20)
				for i in range(3):
					glTranslatef(0, 0, size*0.25)
					gluCylinder(gluNewQuadric(), size*0.3, size*0.4, size*0.15, 20, 20)
					glTranslatef(0, 0, size*0.15)
					gluDisk(quadratic, size*0.3, size*0.4, 20, 20)
				glutSolidSphere(size*0.3, 20, 20)
			if ship['type'] == 'station':
				glutSolidSphere(size, 20, 20)
			if ship['type'] == 'cruiser':
				glPushMatrix()
				quad = gluNewQuadric()
				# Нос
				gluCylinder(quad, 0, size*0.2, size*0.2, 4,4)
				glTranslatef(0, 0, size*0.2)
				# Верхняя часть ракеты
				gluCylinder(quad, size*0.2, size*0.3, size*0.8, 4,4)
				glTranslatef(0, 0, size*0.8)
				# Нижняя часть ракеты
				gluCylinder(quad, size*0.3, size*0.4, size*0.4, 4,4)
				glTranslatef(0,0,size*0.4)
				# Нашлепка на задницу
				gluDisk(quad, 0, size*0.2, 4,4)
				glPopMatrix()
				glPushMatrix()
				# Первая пушка
				glTranslatef(size*0.3*2**-0.5, size*0.3*2**-0.5, size*0.3 )
				gluCylinder(quad, size*0.04, size*0.06, size*0.8, 10, 10)
				glPopMatrix()
				# Вторая пушка
				glPushMatrix()
				glTranslatef(-size*0.3*2**-0.5, size*0.3*2**-0.5, size*0.3 )
				gluCylinder(quad, size*0.04, size*0.06, size*0.8, 10, 10)
				glPopMatrix()
			if ship['type'] == 'battleship':
				quad = gluNewQuadric()
				# Нос
				gluCylinder(quad, 0, size*0.2, size*0.2, 20,20)
				glTranslatef(0, 0, size*0.2)
				# Верхняя часть ракеты
				gluCylinder(quad, size*0.2, size*0.3, size*0.8, 20,20)
				glTranslatef(0, 0, size*0.8)
				# Нижняя часть ракеты
				gluCylinder(quad, size*0.3, size*0.4, size*0.4, 20,20)
				glTranslatef(0,0,size*0.4)
				# Нашлепка на задницу
				gluDisk(quad, 0, size*0.4, 20,20)
				glPushMatrix()
				# Первое сопло
				glTranslatef(0, size*0.2, 0 )
				gluCylinder(quad, size*0.1, size*0.16, size*0.4, 10, 10)
				gluDisk(quad, 0, size*0.15,10,10)
				glPopMatrix()
				glPushMatrix()
				# Первое сопло
				glTranslatef(0, -size*0.2, 0 )
				gluCylinder(quad, size*0.1, size*0.16, size*0.4, 10, 10)
				gluDisk(quad, 0, size*0.15,10,10)
				glPopMatrix()

			glPopMatrix()


	def DrawGLScene(self):

		glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)
		glLoadIdentity()

		glRotatef(self.view_angle, 0, 1, 0)

		glRotatef(self.camera_tangage, math.cos(self.view_angle*math.pi/180), 0, math.sin(self.view_angle*math.pi/180))

		self.draw_planets()
		self.draw_ships()

		# self.draw_transport((1,0,0), 30.0)

		glutSwapBuffers()

	def move(self, straight, dir, range = 0):

		speed = self.speed * self.accel
		if range == 0: range = dir*speed
		dirmult = -1
		angle_rad = math.pi*self.view_angle/180
		tang_rad = math.pi*self.camera_tangage/180
		if straight:
			self.camera_x += -dirmult*range*math.sin(angle_rad)*math.cos(tang_rad)
			self.camera_y += dirmult*range*math.sin(tang_rad)
			self.camera_z += dirmult*range*math.cos(angle_rad)*math.cos(tang_rad)
		else:
			self.camera_x += dirmult*range*math.cos(angle_rad)
			self.camera_z += dirmult*range*math.sin(angle_rad)

	def KeyPressed(self, *args):
		speed = self.speed * self.accel
		key = args[0]
		if key =="\033": sys.exit()
		if key == 'j': self.view_angle -=1
		if key == 'k': self.view_angle +=1
		if key == 'w': self.move(1,1)
		if key == 's': self.move(1, -1)
		if key == 'a': self.move(0, 1)
		if key == 'd': self.move(0, -1)
		if key == 'u': self.camera_y +=speed
		if key == 'i': self.camera_y -=speed
		if key == 'o': self.camera_tangage = min(self.camera_tangage+1, 90)
		if key == 'p': self.camera_tangage = max(self.camera_tangage-1, -90)
		if key=='z': self.accel = min(self.accel+1, 10)
		if key=='x':self.accel = max(1, self.accel - 1)
		# Все кораблики вращаются
		for ship in self.ships:
			ship['rotating_angle'] = (ship['rotating_angle'] + 359)%360;
		print ("Coords: (x="+str(round(self.camera_x,2))+", y="+str( round(self.camera_y,2))+", z="+str(round(self.camera_z,2))+"). View_angle="+str(self.view_angle)+", tangage = "+str(self.camera_tangage))
		self.DrawGLScene()


	def main(self):
		glutInit(sys.argv)
		glutInitDisplayMode(GLUT_RGBA | GLUT_DOUBLE | GLUT_ALPHA | GLUT_DEPTH)
		glutInitWindowSize(800, 600)
		glutInitWindowPosition(0, 0)
		glutCreateWindow("OpenGL demo. Controls: WASDUI - move, JKOP - view. ZX - change speed")
		glutDisplayFunc(self.DrawGLScene)
		# glutIdleFunc(self.DrawGLScene)
		glutReshapeFunc(self.ReSizeGLScene)
		glutKeyboardFunc(self.KeyPressed)
		self.InitGL(1200, 900)
		glutMainLoop()

c = CetaGraph()
c.look_from = 'komarra'
c.look_to = 'earth'
c.ships = c.get_example_ships()
c.main()
