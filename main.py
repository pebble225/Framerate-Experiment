import pygame
import numpy as np
from screeninfo import get_monitors
import time

class Controller:
	def __init__(self):
		self.UP = False
		self.DOWN = False
		self.LEFT = False
		self.RIGHT = False

		self.interpolation = False
		self.rounding = False
		self.precisionTiming = False

	def RegisterEvent(self, e: pygame.event):
		if e.type == pygame.KEYDOWN:
			if e.key == pygame.K_w or e.key == pygame.K_UP:
				self.UP = True
			elif e.key == pygame.K_s or e.key == pygame.K_DOWN:
				self.DOWN = True
			if e.key == pygame.K_a or e.key == pygame.K_LEFT:
				self.LEFT = True
			elif e.key == pygame.K_d or e.key == pygame.K_RIGHT:
				self.RIGHT = True
		elif e.type == pygame.KEYUP:
			if e.key == pygame.K_w or e.key == pygame.K_UP:
				self.UP = False
			elif e.key == pygame.K_s or e.key == pygame.K_DOWN:
				self.DOWN = False
			if e.key == pygame.K_a or e.key == pygame.K_LEFT:
				self.LEFT = False
			elif e.key == pygame.K_d or e.key == pygame.K_RIGHT:
				self.RIGHT = False

			if e.key == pygame.K_1:
				self.interpolation = not self.interpolation
			elif e.key == pygame.K_2:
				self.rounding = not self.rounding
			elif e.key == pygame.K_3:
				self.precisionTiming = not self.precisionTiming
			

class GameInstance:
	def __init__(self):
		self.running = True
		self.window = None
		self.dim = (1600, 900)

		self.controller = Controller()

		self.font = None

		self.lastPos = None
		self.pos = [0, 0]
		self.speed = 30

	def Input(self):
		for e in pygame.event.get():
			if e.type == pygame.QUIT:
				self.running = False
			self.controller.RegisterEvent(e)

	def FixedUpdate(self):
		if self.lastPos is None:
			self.lastPos = list(self.pos)
		else:
			self.lastPos[0] = self.pos[0]
			self.lastPos[1] = self.pos[1]
		
		if self.controller.UP:
			self.pos[1] -= self.speed
		elif self.controller.DOWN:
			self.pos[1] += self.speed

		if self.controller.LEFT:
			self.pos[0] -= self.speed
		elif self.controller.RIGHT:
			self.pos[0] += self.speed

	def DrawText(self, string: str, pos: list[float, float], color: tuple[int, int, int] = (255, 255, 255)):
		surface = self.font.render(string, True, color)
		self.window.blit(surface, pos)

	def Render(self, delta: float):
		self.window.fill((80, 80, 80))

		self.DrawText(f"Interpolation (Press 1): {self.controller.interpolation}", (0, 0))
		self.DrawText(f"Rounding (Press 2): {self.controller.rounding}", (0, 30))
		self.DrawText(f"Precision Timing (Press 3): {self.controller.precisionTiming}", (0, 60))

		if self.controller.interpolation and self.lastPos is not None:
			pos = [
				self.lastPos[0] + (self.pos[0] - self.lastPos[0]) * delta,
				self.lastPos[1] + (self.pos[1] - self.lastPos[1]) * delta
			]
			if self.controller.rounding:
				pos[0] = np.round(pos[0])
				pos[1] = np.round(pos[1])

			pygame.draw.rect(self.window, (255, 255, 255), (pos[0] + self.dim[0]//2, pos[1]+self.dim[1]//2, 100, 100))
		else:
			pygame.draw.rect(self.window, (255, 255, 255), (self.pos[0] + self.dim[0]//2, self.pos[1]+self.dim[1]//2, 100, 100))

		pygame.display.flip()

	def main(self):
		pygame.init()
		pygame.font.init()

		self.font = pygame.font.SysFont("freesans", 30)

		for m in get_monitors():
			if m.is_primary:
				self.dim = (m.width, m.height)
		
		self.window = pygame.display.set_mode(self.dim, pygame.NOFRAME | pygame.SCALED, display = 0, vsync = 1)

		tps = 60.0
		tickMS = 1000.0 / tps

		tickDelta = 0

		lastTick_pygame = pygame.time.get_ticks()
		lastTick_time = time.perf_counter()*1000

		while self.running:
			self.Input()

			nowTick_pygame = pygame.time.get_ticks()
			nowTick_time = time.perf_counter()*1000
			if not self.controller.precisionTiming:
				tickDelta += float(nowTick_pygame-lastTick_pygame)/tickMS
			else:
				tickDelta += float(nowTick_time-lastTick_time)/tickMS
			lastTick_pygame = nowTick_pygame
			lastTick_time = nowTick_time

			while not tickDelta < 1.0:
				self.FixedUpdate()
				tickDelta -= 1.0

			self.Render(tickDelta)

if __name__ == "__main__":
	g = GameInstance()
	g.main()