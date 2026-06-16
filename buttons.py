import pygame

class MusicButton:
    def __init__(self, x: int, y: int, width: int, height: int, 
                 idle_image: str, pushed_image: str, action: str):
        self.rect = pygame.Rect(x, y, width, height)
        self.action = action
        self.is_pushed = False
        try:
            self.idle_image = pygame.image.load(idle_image).convert_alpha()
            self.idle_image = pygame.transform.scale(self.idle_image, (width, height))
            self.pushed_image = pygame.image.load(pushed_image).convert_alpha()
            self.pushed_image = pygame.transform.scale(self.pushed_image, (width, height))
        except:
            self.idle_image = pygame.Surface((width, height))
            self.idle_image.fill((150, 150, 150))
            self.pushed_image = pygame.Surface((width, height))
            self.pushed_image.fill((100, 100, 100))
        
        self.current_image = self.idle_image
        self.pressed_timer = 0

    def draw(self, screen: pygame.Surface) -> None:
        if self.is_pushed and pygame.time.get_ticks() - self.pressed_timer > 100:
            self.is_pushed = False
            self.current_image = self.idle_image
        screen.blit(self.current_image, self.rect)

    def handle_event(self, event: pygame.event.Event) -> bool:
        if event.type == pygame.MOUSEBUTTONDOWN:
            if self.rect.collidepoint(event.pos):
                self.is_pushed = True
                self.pressed_timer = pygame.time.get_ticks()
                self.current_image = self.pushed_image
                return True
        return False
    
    def set_idle_image(self, image_path: str) -> None:
        try:
            self.idle_image = pygame.image.load(image_path).convert_alpha()
            self.idle_image = pygame.transform.scale(self.idle_image, 
                                                    (self.rect.width, self.rect.height))
            if not self.is_pushed:
                self.current_image = self.idle_image
        except:
            pass

class SpeedButton:
    def __init__(self, x: int, y: int, width: int, height: int, text: str, speed_multiplier: float):
        self.rect = pygame.Rect(x, y, width, height)
        self.text = text
        self.speed_multiplier = speed_multiplier
        self.is_active = False
        self.color_normal = (100, 100, 100)
        self.color_hover = (150, 150, 150)
        self.color_active = (255, 105, 180)
        self.current_color = self.color_normal
        self.font = pygame.font.SysFont(None, 28)

    def draw(self, screen: pygame.Surface) -> None:
        pygame.draw.rect(screen, self.current_color, self.rect, border_radius=5)
        pygame.draw.rect(screen, (0, 0, 0), self.rect, 2, border_radius=5)
        text_surface = self.font.render(self.text, True, (255, 255, 255))
        text_rect = text_surface.get_rect(center=self.rect.center)
        screen.blit(text_surface, text_rect)

    def handle_event(self, event: pygame.event.Event) -> bool:
        if event.type == pygame.MOUSEMOTION:
            if self.rect.collidepoint(event.pos):
                self.current_color = self.color_hover if not self.is_active else self.color_active
            else:
                self.current_color = self.color_active if self.is_active else self.color_normal
        elif event.type == pygame.MOUSEBUTTONDOWN:
            if self.rect.collidepoint(event.pos):
                return True
        return False

    def set_active(self, active: bool) -> None:
        self.is_active = active
        self.current_color = self.color_active if active else self.color_normal