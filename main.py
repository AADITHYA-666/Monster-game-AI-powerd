import pygame
import random
import math
import numpy as np
from pygame import gfxdraw

# Initialize Pygame
pygame.init()

# Constants
WINDOW_WIDTH = 1280
WINDOW_HEIGHT = 720
FPS = 60
GRAVITY = 0.8
JUMP_POWER = -15

# Colors
BLACK = (0, 0, 0)
WHITE = (255, 255, 255)
BLUE = (0, 100, 255)
ORANGE = (255, 165, 0)
RED = (255, 0, 0)
GREEN = (0, 255, 0)
PLATFORM_COLOR = (100, 100, 100)

class Platform:
    def __init__(self, x, y, width, height):
        self.rect = pygame.Rect(x, y, width, height)
        self.color = PLATFORM_COLOR

    def draw(self, surface):
        pygame.draw.rect(surface, self.color, self.rect)

class Monster:
    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.width = 40
        self.height = 40
        self.velocity = [0, 0]
        self.health = 100
        self.damage = 10
        self.rect = pygame.Rect(x, y, self.width, self.height)
        self.direction = 1
        self.speed = 2

    def update(self, platforms):
        # Apply gravity
        self.velocity[1] += GRAVITY
        
        # Move horizontally
        self.x += self.speed * self.direction
        
        # Check platform collisions
        self.rect.x = self.x
        self.rect.y = self.y
        
        for platform in platforms:
            if self.rect.colliderect(platform.rect):
                if self.direction > 0:
                    self.x = platform.rect.left - self.width
                    self.direction = -1
                else:
                    self.x = platform.rect.right
                    self.direction = 1
        
        # Update position
        self.x += self.velocity[0]
        self.y += self.velocity[1]
        
        # Update rect position
        self.rect.x = self.x
        self.rect.y = self.y

    def draw(self, surface):
        pygame.draw.rect(surface, RED, self.rect)
        # Health bar
        health_width = (self.health / 100) * self.width
        pygame.draw.rect(surface, GREEN, (self.x, self.y - 10, health_width, 5))

class Weapon:
    def __init__(self, name, damage, range, cooldown):
        self.name = name
        self.damage = damage
        self.range = range
        self.cooldown = cooldown
        self.last_shot = 0

    def can_shoot(self, current_time):
        return current_time - self.last_shot >= self.cooldown

class Mech:
    def __init__(self, name, health, speed, weapon_slots):
        self.name = name
        self.health = health
        self.max_health = health
        self.speed = speed
        self.weapon_slots = weapon_slots
        self.weapons = []
        self.active = False

    def add_weapon(self, weapon):
        if len(self.weapons) < self.weapon_slots:
            self.weapons.append(weapon)
            return True
        return False

class Particle:
    def __init__(self, x, y, color):
        self.x = x
        self.y = y
        self.color = color
        self.size = random.randint(2, 4)
        self.life = 255
        self.velocity = [random.uniform(-2, 2), random.uniform(-2, 2)]
        self.gravity = 0.1

    def update(self):
        self.x += self.velocity[0]
        self.y += self.velocity[1]
        self.velocity[1] += self.gravity
        self.life -= 5
        self.size = max(0, self.size - 0.1)

    def draw(self, surface):
        if self.life > 0:
            alpha = max(0, min(255, self.life))
            color = (*self.color, alpha)
            pygame.draw.circle(surface, color, (int(self.x), int(self.y)), int(self.size))

class Player:
    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.width = 40
        self.height = 60
        self.velocity = [0, 0]
        self.acceleration = 0.5
        self.max_speed = 5
        self.friction = 0.9
        self.jumping = False
        self.rect = pygame.Rect(x, y, self.width, self.height)
        self.health = 100
        self.max_health = 100
        self.weapons = [
            Weapon("Basic Gun", 20, 200, 500),
            Weapon("Shotgun", 40, 100, 1000),
            Weapon("Sniper", 100, 400, 2000)
        ]
        self.current_weapon = 0
        self.mechs = [
            Mech("Light Mech", 200, 3, 2),
            Mech("Heavy Mech", 400, 2, 3)
        ]
        self.active_mech = None
        self.resources = {"metal": 0, "energy": 0, "parts": 0}
        self.trail_particles = []

    def move(self, keys, platforms):
        # Horizontal movement
        if keys[pygame.K_LEFT]:
            self.velocity[0] = -self.max_speed
        elif keys[pygame.K_RIGHT]:
            self.velocity[0] = self.max_speed
        else:
            self.velocity[0] *= self.friction

        # Apply gravity
        self.velocity[1] += GRAVITY

        # Jumping
        if keys[pygame.K_SPACE] and not self.jumping:
            self.velocity[1] = JUMP_POWER
            self.jumping = True

        # Update position
        self.x += self.velocity[0]
        self.y += self.velocity[1]

        # Platform collisions
        self.rect.x = self.x
        self.rect.y = self.y

        for platform in platforms:
            if self.rect.colliderect(platform.rect):
                if self.velocity[1] > 0:  # Falling
                    self.rect.bottom = platform.rect.top
                    self.y = self.rect.y
                    self.velocity[1] = 0
                    self.jumping = False
                elif self.velocity[1] < 0:  # Jumping
                    self.rect.top = platform.rect.bottom
                    self.y = self.rect.y
                    self.velocity[1] = 0

        # Keep player in bounds
        self.x = max(0, min(WINDOW_WIDTH - self.width, self.x))
        self.y = max(0, min(WINDOW_HEIGHT - self.height, self.y))

        # Add trail particles
        if random.random() < 0.3:
            self.trail_particles.append(Particle(self.x + self.width/2, self.y + self.height/2, BLUE))

    def shoot(self, target_x, target_y, current_time):
        if self.active_mech:
            for weapon in self.active_mech.weapons:
                if weapon.can_shoot(current_time):
                    weapon.last_shot = current_time
                    return True
        else:
            weapon = self.weapons[self.current_weapon]
            if weapon.can_shoot(current_time):
                weapon.last_shot = current_time
                return True
        return False

    def draw(self, surface):
        # Draw trail particles
        for particle in self.trail_particles[:]:
            particle.update()
            particle.draw(surface)
            if particle.life <= 0:
                self.trail_particles.remove(particle)

        # Draw player
        if self.active_mech:
            pygame.draw.rect(surface, ORANGE, self.rect)
        else:
            pygame.draw.rect(surface, BLUE, self.rect)

        # Health bar
        health_width = (self.health / self.max_health) * self.width
        pygame.draw.rect(surface, GREEN, (self.x, self.y - 10, health_width, 5))

class Game:
    def __init__(self):
        self.screen = pygame.display.set_mode((WINDOW_WIDTH, WINDOW_HEIGHT))
        pygame.display.set_caption("Monster Hunter Platformer")
        self.clock = pygame.time.Clock()
        self.player = Player(WINDOW_WIDTH // 2, WINDOW_HEIGHT // 2)
        self.platforms = [
            Platform(0, WINDOW_HEIGHT - 40, WINDOW_WIDTH, 40),  # Ground
            Platform(300, 500, 200, 20),
            Platform(100, 400, 200, 20),
            Platform(500, 300, 200, 20),
            Platform(700, 200, 200, 20),
        ]
        self.monsters = [
            Monster(400, 300),
            Monster(200, 200),
        ]
        self.particles = []
        self.running = True
        self.camera_shake = 0
        self.current_time = 0

    def handle_events(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.running = False
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    self.running = False
                elif event.key == pygame.K_1:
                    self.player.current_weapon = 0
                elif event.key == pygame.K_2:
                    self.player.current_weapon = 1
                elif event.key == pygame.K_3:
                    self.player.current_weapon = 2
                elif event.key == pygame.K_m:
                    # Toggle mech
                    if self.player.active_mech:
                        self.player.active_mech = None
                    else:
                        self.player.active_mech = self.player.mechs[0]
            elif event.type == pygame.MOUSEBUTTONDOWN:
                if event.button == 1:  # Left click
                    mouse_x, mouse_y = pygame.mouse.get_pos()
                    if self.player.shoot(mouse_x, mouse_y, self.current_time):
                        # Create shooting effect
                        self.particles.append(Particle(
                            self.player.x + self.player.width/2,
                            self.player.y + self.player.height/2,
                            ORANGE
                        ))

    def update(self):
        self.current_time = pygame.time.get_ticks()
        keys = pygame.get_pressed()
        self.player.move(keys, self.platforms)

        # Update monsters
        for monster in self.monsters:
            monster.update(self.platforms)
            # Check collision with player
            if monster.rect.colliderect(self.player.rect):
                self.player.health -= monster.damage
                if self.player.health <= 0:
                    self.running = False

        # Update particles
        for particle in self.particles[:]:
            particle.update()
            if particle.life <= 0:
                self.particles.remove(particle)

        # Update camera shake
        if self.camera_shake > 0:
            self.camera_shake -= 1

    def draw(self):
        # Clear screen with a dark background
        self.screen.fill((10, 10, 20))

        # Apply camera shake
        shake_offset = (
            random.randint(-self.camera_shake, self.camera_shake),
            random.randint(-self.camera_shake, self.camera_shake)
        )

        # Draw platforms
        for platform in self.platforms:
            platform.draw(self.screen)

        # Draw monsters
        for monster in self.monsters:
            monster.draw(self.screen)

        # Draw particles
        for particle in self.particles:
            particle.draw(self.screen)

        # Draw player
        self.player.draw(self.screen)

        # Draw UI
        font = pygame.font.Font(None, 36)
        # Controls
        controls_text = "WASD: Move | SPACE: Jump | 1-3: Switch Weapons | M: Toggle Mech | ESC: Quit"
        text = font.render(controls_text, True, WHITE)
        self.screen.blit(text, (20, 20))

        # Resources
        resources_text = f"Metal: {self.player.resources['metal']} | Energy: {self.player.resources['energy']} | Parts: {self.player.resources['parts']}"
        text = font.render(resources_text, True, WHITE)
        self.screen.blit(text, (20, 60))

        # Current weapon
        weapon_text = f"Weapon: {self.player.weapons[self.player.current_weapon].name}"
        text = font.render(weapon_text, True, WHITE)
        self.screen.blit(text, (20, 100))

        # Mech status
        if self.player.active_mech:
            mech_text = f"Active Mech: {self.player.active_mech.name} | Health: {self.player.active_mech.health}"
            text = font.render(mech_text, True, WHITE)
            self.screen.blit(text, (20, 140))

        pygame.display.flip()

    def run(self):
        while self.running:
            self.handle_events()
            self.update()
            self.draw()
            self.clock.tick(FPS)

if __name__ == "__main__":
    game = Game()
    game.run()
    pygame.quit() 