import pygame, sys, math, random

pygame.font.init()
gamefont = pygame.font.SysFont("Comic Sans MS",20)

playfield = pygame.Surface((600,600))
playfield_rect = playfield.get_rect()
playfield_color = [random.randint(0,64) for i in range(3)]
win = pygame.display.set_mode(playfield_rect.bottomright)
planettypelist = []


run = True
fps = 60
clock = pygame.time.Clock()

planets = pygame.sprite.Group()
enemies = pygame.sprite.Group()
players = pygame.sprite.Group()


# adding some pre-defined values to pygame.sprite.Sprite
class Sprite(pygame.sprite.Sprite):
    def __init__(self,health=3,mytype="sprite"):
        pygame.sprite.Sprite.__init__(self)
        self.type = mytype
        self.health = health
    def on_collide(self,collision):
        ...
    def hurt(self,amt=1):
        # takes damage and destroys it if dead
        self.health -= 1
        if self.health <= 0:
            self.kill()
    def wrap(self):
        # wrapping around
        while self.pos[0] > playfield_rect.right:
            self.pos[0] -= playfield_rect.right
        while self.pos[0] < playfield_rect.left:
            self.pos[0] += playfield_rect.right
        while self.pos[1] > playfield_rect.bottom:
            self.pos[1] -= playfield_rect.bottom
        while self.pos[1] < playfield_rect.top:
            self.pos[1] += playfield_rect.bottom


# planet item
class Planet(Sprite):
    def __init__(self,radius=10,pos=[0,0],health=10):
        # creates a Planet object with the given arguments
        Sprite.__init__(self,health=health)
        self.image = pygame.Surface((radius*2,radius*2),pygame.SRCALPHA)
        self.rect = self.image.get_rect()
        self.pos = self.rect.center = pos
        self.radius = self.health * 2
        # drawing circle
        self.color = (random.randint(0,255),random.randint(0,255),random.randint(0,255))
        self.update_surf()
        self.mask = pygame.mask.from_surface(self.image)
        # various info
        self.spd = 0.005 # momentum gain
        self.friction = 0.7 # momentum loss, slipperiness
    
    def update_surf(self):
        self.image.fill((0,0,0,0))
        pygame.draw.circle(surface=self.image,color=self.color,center=(self.radius,self.radius),radius=self.radius)
        self.image.blit(gamefont.render(str(self.health),False,"BLACK"),(self.radius-10,self.radius-15))

    def hurt(self):
        Sprite.hurt(self)
        self.update_surf()


# moving planet bc im silly
class MovingPlanet(Planet):
    def __init__(self,radius=10,pos=[0,0],health=10,move_vals=[0,0]):
        Planet.__init__(self,radius,pos,health)
        self.ogpos=self.pos[:]
        self.move_vals = move_vals
    def update(self):
        # print(self.pos)
        self.pos[0] += self.move_vals[0]
        self.pos[1] += self.move_vals[1]
        self.wrap()
        self.rect.center=self.pos

# defendable planet
class DefendPlanet(Planet):
    def __init__(self,radius=10,pos=[0,0],health=10,move_vals=[0,0]):
        Planet.__init__(self,radius,pos,health)
        self.color = [0,0,0]
    def update(self):
        for i in range(len(self.color)):
            self.color[i] += random.randint(-5,5)
            if self.color[i] < 0:
                self.color[i] = 0
            if self.color[i] > 255:
                self.color[i] = 255
        self.update_surf()


# updating planet type list
planettypelist.append(Planet)
planettypelist.append(MovingPlanet)
planettypelist.append(DefendPlanet)

# player item
class Player(Sprite):
    
    def __init__(self,planet=None,theta=0):
        # creates player latched onto a specified planet -- cannot start in freefall
        Sprite.__init__(self,health=3)
        self.image = pygame.Surface((7,7))
        self.image.fill("WHITE")
        self.planet = planet #the planet the player is on, which is also a value to see if the player is freefalling or not.
        self.theta = theta 
        self.rect = self.image.get_rect()
        # movement info
        self.pos = [0,0]
        self.momentum = 0
        self.moving_left = False
        self.moving_right = False
        self.momentum_max = 0.2   # maximum speed player can reach
        self.momentum_min = 0.0001 # minimum speed before it rounds to 0
        # freefall info
        self.move_vals = None # not yet
        self.airspeed = 5
        self.airtimer = 0 
        self.airmax = 600 # you die if you're in the air for longer than 10 seconds


    def update(self):
        # if grounded on a planet
        if self.planet is not None:
            self.grounded_movement()
        else:
            self.air_movement()

        # wrapping around
        self.wrap()
        
        self.rect.center = self.pos

            
            
        
    def grounded_movement(self):
        # updating positioning
        self.pos[0] = self.planet.pos[0] + (self.planet.radius * math.cos(self.theta))
        self.pos[1] = self.planet.pos[1] + (self.planet.radius * math.sin(self.theta))
        # stopping movement 
        if self.moving_left and self.moving_right:
            # stopping movement if moving in both directions
            self.moving_left = self.moving_right = False
        
        # moving counterclockwise
        if self.moving_left:
            self.momentum -= self.planet.spd
            # capping max momentum
            if abs(self.momentum) > self.momentum_max:
                self.momentum = self.momentum_max*-1
        
        # moving clockwise
        if self.moving_right:
            self.momentum += self.planet.spd
            # capping max momentum
            if abs(self.momentum) > self.momentum_max:
                self.momentum = self.momentum_max*1
        
        # updating friction if moving in opposite direction or not moving at all
        if not (self.moving_left or self.moving_right) or (self.moving_right and  self.momentum < 0) or (self.moving_left and self.momentum > 0):
            self.momentum = round(self.momentum*self.planet.friction,5)
        
        # minimum speed
        if abs(self.momentum) <= self.momentum_min:
            self.momentum = 0
        
        # updating theta
        self.theta += self.momentum


    def air_movement(self):
        # now I'm freeeeeee
        # free fallin'
        if self.move_vals == None:
            self.move_vals = [
                math.cos(self.theta)*self.airspeed,
                math.sin(self.theta)*self.airspeed
            ]
        # moving
        self.pos[0] += self.move_vals[0]
        self.pos[1] += self.move_vals[1]
        # timer
        self.airtimer += 1
        # print(self.pos,self.move_vals)
        
    def on_collide(self,collision):
        # if a planet is being collided with, the player is in the air, and the player's been in the air for longer than 3 frames, hit the planet
        if type(collision) in planettypelist and self.planet == None and self.airtimer>5:
            self.planet = collision
            
            self.theta = math.atan2(self.pos[1]-self.planet.pos[1],self.pos[0]-self.planet.pos[0])
            self.move_vals = None


    def event_handler(self,event):
        match event.type:
            case pygame.KEYDOWN:
                match event.key:
                    case pygame.K_LEFT:
                        #move counterclockwise
                        self.moving_left=True
                        self.moving_right=False
                    case pygame.K_RIGHT:
                        #move clockwise
                        self.moving_right=True
                        self.moving_left=False
                    case pygame.K_SPACE:
                        #shoot
                        players.add(
                            Bullet(player=self)
                        )
                    case pygame.K_UP:
                        #jump
                        self.airtimer = 0
                        self.planet = None
            case pygame.KEYUP:
                match event.key:
                    case pygame.K_LEFT:
                        # stop move counterclockwise
                        self.moving_left = False
                    case pygame.K_RIGHT:
                        # stop move clockwise
                        self.moving_right = False


# bullet item
class Bullet(Sprite):
    def __init__(self,player,spd=7.5,lifespan=30):
        Sprite.__init__(self,health=1)
        # image/rect info
        self.image = pygame.Surface((5,5))
        self.image.fill("GREEN")
        self.rect = self.image.get_rect()
        # filling in values
        self.spd = spd
        self.player = player
        self.lifespan = lifespan
        self.timer = 0 
        # movement/angle info
        self.theta = self.player.theta
        self.move_vals = (math.cos(self.theta)*self.spd,math.sin(self.theta)*self.spd) 
        self.pos = self.player.pos[:] #making a copy of the player position

    def update(self):
        # moving position
        self.pos[0] += self.move_vals[0]
        self.pos[1] += self.move_vals[1]
        
        # wrapping around
        self.wrap()

        # finalizing position
        self.rect.center = self.pos

        # timer info
        self.timer += 1
        if self.timer > self.lifespan:
            self.kill()

    def on_collide(self,collision):
        if type(collision) == Enemy:
            pass # enemy handles killing of bullet



# enemy item
class Enemy(Sprite):
    def __init__(self,planet):
        Sprite.__init__(self,health=1)
        # sprite info
        self.image = pygame.Surface((12,12)) 
        self.image.fill("RED")
        self.rect = self.image.get_rect()
        self.mask = pygame.mask.from_surface(self.image)
        self.pos = [0,0]
        
        # behavior info
        self.planet = planet #what planet the enemy is attacking. I'm gonna make various classes
        self.theta = random.uniform(0,3.14*2)
        self.spd = 1 # how fast the radius shrinks
        self.radius = math.sqrt( (playfield_rect.width**2) + (playfield_rect.height**2) ) # the radius is always the same because this is the largest distance it could be.
        # calling update so it doesn't teleport for one frame
        self.update()

    def update(self):
        self.radius -= self.spd
        # updating positioning
        self.pos[0] = self.planet.pos[0] + (self.radius * math.cos(self.theta))
        self.pos[1] = self.planet.pos[1] + (self.radius * math.sin(self.theta))
        # finalizing
        self.rect.center = self.pos
        # print(self.radius, self.theta, self.pos)


    def on_collide(self,collision):
        if type(collision) == Planet:
            if collision == self.planet:
                collision.hurt()
                self.hurt()
        else:
            collision.hurt()
            self.hurt() 
        



# generating a level of planets
for i in range(random.randint(5,10)):
    health = random.randint(20,60)
    pos = [random.uniform(health*1.2,playfield_rect.width-health*1.2),random.uniform(health*1.2,playfield_rect.height-health*1.2)]
    planets.add(
        random.choice([Planet,MovingPlanet,DefendPlanet])(health,pos,health=health//2)
            )


# generating player
player = Player(planet=random.choice(planets.sprites()),theta=0)
players.add(player)

while run:
    # sprite update
    players.update()
    planets.update()
    enemies.update()
    # sprite draw
    win.fill(playfield_color)
    planets.draw(win)
    players.draw(win)
    enemies.draw(win)
    # print
    # print(player.momentum,player.momentum_max,player.moving_left,player.moving_right)

    # collision
    collide_playerplanet = pygame.sprite.groupcollide(players,planets,False,False,collided=pygame.sprite.collide_mask).items()
    collide_enemyplanet = pygame.sprite.groupcollide(planets,enemies,False,False,collided=pygame.sprite.collide_mask).items()
    collide_playerenemy = pygame.sprite.groupcollide(players,enemies,False,False,collided=pygame.sprite.collide_mask).items()
    for i in (collide_playerplanet,collide_enemyplanet,collide_playerenemy):
        for k,v in i:
            for j in v: #iterating through each planet collision
                k.on_collide(j)
                j.on_collide(k)
            


    # updating display
    pygame.display.update()
    # event checking
    for event in pygame.event.get():
        player.event_handler(event)

        match event.type:
            case pygame.QUIT:
                run = False 
            case pygame.KEYDOWN:
                match event.key:
                    case pygame.K_s:
                        enemies.add(Enemy(planet=random.choice(planets.sprites())))

    # ticking clock
    clock.tick(fps)
    
        
            
        
        