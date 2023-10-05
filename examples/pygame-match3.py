#!/usr/bin/env python3

import wasm3
import os, time, random
import pygame

print("WebAssembly demo file provided by Ben Smith (binji)")
print("Sources: https://github.com/binji/raw-wasm")

scriptpath = os.path.dirname(os.path.realpath(__file__))
wasm_fn = os.path.join(scriptpath, "./wasm/match3.wasm")

# Prepare Wasm3 engine

env = wasm3.Environment()
rt = env.new_runtime(1024)
with open(wasm_fn, "rb") as f:
    mod = env.parse_module(f.read())
    rt.load(mod)
    mod.link_function("Math", "random", lambda: random.random())

wasm_run = rt.find_function("run")
mem = rt.get_memory(0)

# Map memory region to an RGBA image

img_base = 0x1100
img_size = (150, 150)
(img_w, img_h) = img_size
region = mem[img_base : img_base + (img_w * img_h * 4)]
img = pygame.image.frombuffer(region, img_size, "RGBA")

# Prepare PyGame

scr_size = (img_w*4, img_h*4)
pygame.init()
surface = pygame.display.set_mode(scr_size)
pygame.display.set_caption("Wasm3 Match3")
white = (255, 255, 255)

clock = pygame.time.Clock()

prev_input = None
prev_input_time = 0

while True:
    # Process input
    for event in pygame.event.get():
        if (event.type == pygame.QUIT or
            (event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE)):
            pygame.quit()
            quit()

    (mouse_x, mouse_y) = pygame.mouse.get_pos()
    mem[0] = mouse_x // 4
    mem[1] = mouse_y // 4
    mem[2] = 1 if pygame.mouse.get_pressed()[0] else 0

    # Stop rendering if no interaction for 10 seconds
    inp = tuple(mem[:3])
    if inp != prev_input:
        prev_input_time = time.time()
    if time.time() - prev_input_time > 10:
        clock.tick(60)
        continue
    prev_input = inp

    # Render next frame
    wasm_run()

    # Image output
    img_scaled = pygame.transform.scale(img, scr_size)
    surface.fill(white)
    surface.blit(img_scaled, (0, 0))
    pygame.display.flip()

    # Stabilize FPS
    clock.tick(60)
