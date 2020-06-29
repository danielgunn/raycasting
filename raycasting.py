import pygame
from pygame.math import Vector2, Vector3
from random import randint
from numpy import interp
from math import cos
from math import radians

width = 300
height = 300

class Boundary:
    def __init__(self, width, height):
        self.a = Vector2(randint(10,width-10),randint(10,height-10))
        self.b = Vector2(randint(10,width-10),randint(10,height-10))
        self.color = (randint(20,255), randint(20,255), randint(20,255))

    def show(self, screen):
        pygame.draw.line(screen, self.color, self.a, self.b)

class Ray:
    def __init__(self, pos, angle):
        self.pos = pos
        self.dir = Vector2(1,0)
        self.dir.rotate_ip(angle)

    def show(self):
        endRay = self.pos + (self.dir * 10)
        pygame.draw.line(screen, (255,255,255), self.pos, endRay)

    def cast(self, wall):
        '''
        :param wall: A Boundary object
        :return: the point of intersection, of this ray and the boundary or None
        '''

        # https://en.wikipedia.org/wiki/Line%E2%80%93line_intersection
        x1 = wall.a.x
        y1 = wall.a.y
        x2 = wall.b.x
        y2 = wall.b.y
        x3 = self.pos.x
        y3 = self.pos.y
        x4 = self.pos.x + self.dir.x * 100  #TODO: not 100
        y4 = self.pos.y + self.dir.y * 100

        den = (x1 - x2) * (y3 - y4) - (y1 - y2) * (x3 - x4)
        if den == 0:
            return None  # They are parallel

        t = ((x1 - x3) * (y3 - y4) - (y1 - y3) * (x3 - x4))/ den
        u = -((x1 - x2) * (y1 - y3) - (y1 - y2) * (x1 - x3))/ den

        if t > 0 and t < 1 and u > 0:
            e = Vector2()
            e.x = x1 + t * (x2 - x1)
            e.y = y1 + t * (y2 - y1)
            return e
        else:
            return None

        return None

class Camera:
    def __init__(self, fov):
        self.pos = Vector2(width/2, height/2)
        self.fov = fov
        self.rays = []
        self.heading = 0

    def rotate(self, angle_offset):
        self.heading += angle_offset
        self.heading = self.heading % 360

    def move(self, forward_offset):
        dir = Vector2(1,0)
        dir.rotate_ip(self.heading)
        dir.normalize_ip()
        self.pos = self.pos + forward_offset*dir

    def update(self, fov):
        self.rays = []
        self.fov = fov # TODO: Will we actually use this anywhere?
        for deg in range(int(self.heading - self.fov//2), int(self.heading + self.fov//2),1):
            self.rays.append(Ray(self.pos, deg))

    def look(self, screen, walls):
        scene = []
        for r in self.rays:
            close_p = None
            close_d = -1
            close_c = (0,0,0)
            for wall in walls:
                p = r.cast(wall)
                if p is not None:
                    d = self.pos.distance_to(p)
                    a = Vector2(0,0).angle_to(r.dir) - self.heading
                    d *= cos(radians(a))
                    if close_d == -1 or d < close_d:
                        close_p = p
                        close_d = d
                        close_c = wall.color
            if close_p is not None:
                pygame.draw.line(screen,(0,0,255), self.pos, close_p)
                scene.append((close_d,close_c))
            else:
                scene.append((-1,(0,0,0)))
        return scene

    def show(self, screen):
        pygame.draw.ellipse(screen, (0,255,0),pygame.Rect(self.pos.x-4,self.pos.y-4,8,8))



pygame.init()

screen = pygame.display.set_mode((width*2, height))
clock = pygame.time.Clock()

walls = []
for i in range(5):
    walls.append(Boundary(width, height))
# ray = Ray(100,150)
camera = Camera(0)

running = True
while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

    clock.tick(60)
    keys = pygame.key.get_pressed()
    if keys[pygame.K_RIGHT]:
        camera.rotate(1)
    if keys[pygame.K_LEFT]:
        camera.rotate(-1)
    if keys[pygame.K_UP]:
        camera.move(1)
    if keys[pygame.K_DOWN]:
        camera.move(-1)

    mouseY = pygame.mouse.get_pos()[1]
    fov = interp(mouseY, [0, height], [5, 350])

    camera.update(fov)

    screen.fill((0,0,0))

    for wall in walls:
        wall.show(screen)

    scene = camera.look(screen, walls)
    max_distance = Vector2(0,0).distance_to(Vector2(width,height))
    for i in range(len(scene)):
        s = scene[i]
        if s[0] != -1:
            scale = s[0]
            h = interp(scale,[0,max_distance],[height/2,0])
            bright = interp(scale, [0, max_distance], [1,0.0])
            bright = bright ** 5
            c = (s[1][0]*bright,s[1][1]*bright,s[1][2]*bright)
            x = int(width + i*width/len(scene))
            p1 = Vector2(x, height//2 - h)
            p2 = Vector2(x, height//2 + h)
            pygame.draw.line(screen, c, p1, p2,width//len(scene)+1)
    camera.show(screen)

    pygame.display.flip()

pygame.quit()
