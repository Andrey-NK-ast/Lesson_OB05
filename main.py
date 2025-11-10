import pygame
import random
import math

pygame.init()

# Константы
SCREEN_WIDTH = 800
SCREEN_HEIGHT = 600
TANK_SIZE = 40
BULLET_SIZE = 8
WALL_SIZE = 40
TANK_SPEED = 3
BULLET_SPEED = 7
ROTATION_SPEED = 3

# Цвет
BLACK = (0, 0, 0)
WHITE = (255, 255, 255)
RED = (255, 0, 0)
GREEN = (0, 255, 0)
BLUE = (0, 0, 255)
YELLOW = (255, 255, 0)
GRAY = (128, 128, 128)

#экран
screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
pygame.display.set_caption("Танчики")
clock = pygame.time.Clock()


class Tank:
    def __init__(self, x, y, color, controls):
        self.x = x
        self.y = y
        self.color = color
        self.angle = 0
        self.controls = controls
        self.cooldown = 0
        self.health = 100
        self.score = 0

    def draw(self):
        # танк
        tank_rect = pygame.Rect(0, 0, TANK_SIZE, TANK_SIZE)
        tank_rect.center = (self.x, self.y)

        # Поворот танка
        tank_surface = pygame.Surface((TANK_SIZE, TANK_SIZE), pygame.SRCALPHA)
        pygame.draw.rect(tank_surface, self.color, (0, 0, TANK_SIZE, TANK_SIZE))
        pygame.draw.rect(tank_surface, BLACK, (0, 0, TANK_SIZE, TANK_SIZE), 2)

        # Дуло танка
        pygame.draw.rect(tank_surface, BLACK, (TANK_SIZE // 2 - 2, 0, 4, TANK_SIZE // 2))

        # Поворачиваем танк
        rotated_tank = pygame.transform.rotate(tank_surface, self.angle)
        rotated_rect = rotated_tank.get_rect(center=tank_rect.center)

        # Отрисовка на экране
        screen.blit(rotated_tank, rotated_rect)

        # Отображение здоровья
        health_bar_width = TANK_SIZE
        health_bar_height = 5
        health_ratio = self.health / 100
        pygame.draw.rect(screen, RED, (self.x - health_bar_width // 2, self.y - TANK_SIZE // 2 - 10,
                                       health_bar_width, health_bar_height))
        pygame.draw.rect(screen, GREEN, (self.x - health_bar_width // 2, self.y - TANK_SIZE // 2 - 10,
                                         health_bar_width * health_ratio, health_bar_height))

    def move(self, keys, walls):
        # Сохраняем старые координаты для отката при столкновении
        old_x, old_y = self.x, self.y

        # Движение в направлениях (обновленное управление)
        if keys[self.controls["up"]]:
            self.y -= TANK_SPEED
        if keys[self.controls["down"]]:
            self.y += TANK_SPEED
        if keys[self.controls["left"]]:
            self.x -= TANK_SPEED
        if keys[self.controls["right"]]:
            self.x += TANK_SPEED

        # Поворот танка в направлении движения
        if keys[self.controls["up"]] and not keys[self.controls["down"]]:
            self.angle = 0
        elif keys[self.controls["down"]] and not keys[self.controls["up"]]:
            self.angle = 180
        elif keys[self.controls["left"]] and not keys[self.controls["right"]]:
            self.angle = 90
        elif keys[self.controls["right"]] and not keys[self.controls["left"]]:
            self.angle = 270

        # Диагональные направления
        if keys[self.controls["up"]] and keys[self.controls["left"]]:
            self.angle = 45
        elif keys[self.controls["up"]] and keys[self.controls["right"]]:
            self.angle = 315
        elif keys[self.controls["down"]] and keys[self.controls["left"]]:
            self.angle = 135
        elif keys[self.controls["down"]] and keys[self.controls["right"]]:
            self.angle = 225

        # Ограничение движения в пределах экрана
        self.x = max(TANK_SIZE // 2, min(SCREEN_WIDTH - TANK_SIZE // 2, self.x))
        self.y = max(TANK_SIZE // 2, min(SCREEN_HEIGHT - TANK_SIZE // 2, self.y))

        # Проверка столкновений со стенами
        for wall in walls:
            if self.collides_with(wall):
                self.x, self.y = old_x, old_y
                break

    def shoot(self):
        if self.cooldown <= 0:
            # Создание пули впереди танка
            bullet_x = self.x + math.sin(math.radians(self.angle)) * (TANK_SIZE // 2 + BULLET_SIZE // 2)
            bullet_y = self.y - math.cos(math.radians(self.angle)) * (TANK_SIZE // 2 + BULLET_SIZE // 2)
            return Bullet(bullet_x, bullet_y, self.angle, self)
        return None

    def collides_with(self, wall):
        # Проверка столкновения танка со стеной
        tank_rect = pygame.Rect(self.x - TANK_SIZE // 2, self.y - TANK_SIZE // 2, TANK_SIZE, TANK_SIZE)
        return tank_rect.colliderect(wall.rect)

    def update(self):
        if self.cooldown > 0:
            self.cooldown -= 1


class Bullet:
    def __init__(self, x, y, angle, owner):
        self.x = x
        self.y = y
        self.angle = angle
        self.owner = owner
        self.speed = BULLET_SPEED

    def draw(self):
        pygame.draw.circle(screen, YELLOW, (int(self.x), int(self.y)), BULLET_SIZE)

    def move(self):
        self.x += math.sin(math.radians(self.angle)) * self.speed
        self.y -= math.cos(math.radians(self.angle)) * self.speed

    def is_out_of_bounds(self):
        return (self.x < 0 or self.x > SCREEN_WIDTH or
                self.y < 0 or self.y > SCREEN_HEIGHT)

    def collides_with(self, tank):
        # Проверка столкновения пули с танком
        distance = math.sqrt((self.x - tank.x) ** 2 + (self.y - tank.y) ** 2)
        return distance < (TANK_SIZE // 2 + BULLET_SIZE)


class Wall:
    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.rect = pygame.Rect(x - WALL_SIZE // 2, y - WALL_SIZE // 2, WALL_SIZE, WALL_SIZE)

    def draw(self):
        pygame.draw.rect(screen, GRAY, self.rect)
        pygame.draw.rect(screen, BLACK, self.rect, 2)


def create_walls():
    walls = []
    # Создаем несколько случайных стен
    for _ in range(15):
        x = random.randint(WALL_SIZE // 2, SCREEN_WIDTH - WALL_SIZE // 2)
        y = random.randint(WALL_SIZE // 2, SCREEN_HEIGHT - WALL_SIZE // 2)
        walls.append(Wall(x, y))

    # Создаем границы
    walls.append(Wall(SCREEN_WIDTH // 2, 10))
    walls.append(Wall(SCREEN_WIDTH // 2, SCREEN_HEIGHT - 10))
    walls.append(Wall(10, SCREEN_HEIGHT // 2))
    walls.append(Wall(SCREEN_WIDTH - 10, SCREEN_HEIGHT // 2))

    return walls


def draw_score(player1, player2):
    font = pygame.font.SysFont(None, 36)
    player1_text = font.render(f"Игрок 1: {player1.score}", True, BLUE)
    player2_text = font.render(f"Игрок 2: {player2.score}", True, RED)
    screen.blit(player1_text, (10, 10))
    screen.blit(player2_text, (SCREEN_WIDTH - 150, 10))


def main():
    # Создание танков
    player1 = Tank(100, 100, BLUE, {
        "up": pygame.K_w,
        "down": pygame.K_s,
        "left": pygame.K_a,
        "right": pygame.K_d,
        "shoot": pygame.K_SPACE
    })

    player2 = Tank(SCREEN_WIDTH - 100, SCREEN_HEIGHT - 100, RED, {
        "up": pygame.K_UP,
        "down": pygame.K_DOWN,
        "left": pygame.K_LEFT,
        "right": pygame.K_RIGHT,
        "shoot": pygame.K_RCTRL
    })

    # Создание стен
    walls = create_walls()

    # Список пуль
    bullets = []

    running = True
    while running:
        # Обработка событий
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            elif event.type == pygame.KEYDOWN:
                if event.key == player1.controls["shoot"]:
                    bullet = player1.shoot()
                    if bullet:
                        bullets.append(bullet)
                        player1.cooldown = 20
                elif event.key == player2.controls["shoot"]:
                    bullet = player2.shoot()
                    if bullet:
                        bullets.append(bullet)
                        player2.cooldown = 20

        # Получение состояния клавиш
        keys = pygame.key.get_pressed()

        # Обновление танков
        player1.move(keys, walls)
        player2.move(keys, walls)
        player1.update()
        player2.update()

        # Обновление пуль
        for bullet in bullets[:]:
            bullet.move()

            # Проверка выхода за границы
            if bullet.is_out_of_bounds():
                bullets.remove(bullet)
                continue

            # Проверка столкновения со стенами
            for wall in walls:
                if wall.rect.collidepoint(bullet.x, bullet.y):
                    if bullet in bullets:
                        bullets.remove(bullet)
                    break

            # Проверка попадания в танки
            if bullet.owner != player1 and bullet.collides_with(player1):
                player1.health -= 10
                if bullet in bullets:
                    bullets.remove(bullet)
                if player1.health <= 0:
                    player2.score += 1
                    player1.health = 100
                    # Перемещение танков в начальные позиции
                    player1.x, player1.y = 100, 100
                    player2.x, player2.y = SCREEN_WIDTH - 100, SCREEN_HEIGHT - 100

            elif bullet.owner != player2 and bullet.collides_with(player2):
                player2.health -= 10
                if bullet in bullets:
                    bullets.remove(bullet)
                if player2.health <= 0:
                    player1.score += 1
                    player2.health = 100
                    # Перемещение танков в начальные позиции
                    player1.x, player1.y = 100, 100
                    player2.x, player2.y = SCREEN_WIDTH - 100, SCREEN_HEIGHT - 100

        # Отрисовка
        screen.fill(BLACK)

        # Отрисовка стен
        for wall in walls:
            wall.draw()

        # Отрисовка танков
        player1.draw()
        player2.draw()

        # Отрисовка пуль
        for bullet in bullets:
            bullet.draw()

        # Отрисовка счета
        draw_score(player1, player2)

        # Обновление экрана
        pygame.display.flip()
        clock.tick(60)


if __name__ == "__main__":
    main()
    pygame.quit()