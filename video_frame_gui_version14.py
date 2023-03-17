import cv2
import sys
import pygame
from pygame.locals import *
import tkinter as tk
from tkinter import filedialog
import numpy as np

ONION_SKIN_ALPHA = 100  # The opacity of the onion skin layers (0-255)

class Drawing:
    def __init__(self, width, height):
        self.width = width
        self.height = height
        self.layers = []

    def add_layer(self, layer=None):
        if layer is None:
            layer = pygame.Surface((self.width, self.height), pygame.SRCALPHA, 32)
        self.layers.append(layer)

    def remove_layer(self, index):
        if 0 <= index < len(self.layers):
            self.layers.pop(index)

    def draw(self, screen, current_frame, onion_skin=True):
        if onion_skin:
            # Draw the previous frame's onion skin
            if current_frame > 0:
                prev_frame = self.layers[current_frame - 1].copy()
                prev_frame.set_alpha(ONION_SKIN_ALPHA)
                screen.blit(prev_frame, (0, 0))

            # Draw the next frame's onion skin
            if current_frame < len(self.layers) - 1:
                next_frame = self.layers[current_frame + 1].copy()
                next_frame.set_alpha(ONION_SKIN_ALPHA)
                screen.blit(next_frame, (0, 0))

        # Draw the current frame
        screen.blit(self.layers[current_frame], (0, 0))

    def get_empty_image(self):
        return pygame.Surface((self.width, self.height), pygame.SRCALPHA, 32)


def display_frame(screen, frame, x, y, window_width, window_height):
    frame = cv2.resize(frame, (window_width, window_height), interpolation=cv2.INTER_AREA)
    frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
    frame = pygame.surfarray.make_surface(frame.swapaxes(0, 1))
    screen.blit(frame, (x, y))


def open_file():
    root = tk.Tk()
    root.withdraw()
    file_path = filedialog.askopenfilename()
    root.destroy()
    return file_path
    
def forward_click(current_frame, total_frames):
    if current_frame < total_frames - 1:
        return current_frame + 1
    return current_frame

def rewind_click(current_frame):
    if current_frame > 0:
        return current_frame - 1
    return current_frame



def main():
    pygame.init()

    window_width, window_height = 800, 600
    screen = pygame.display.set_mode((window_width, window_height), 0, 32)
    pygame.display.set_caption("Video Frame Viewer")

    video_file = None
    cap = None
    paused = True
    current_frame = 0
    last_frame = None

    font = pygame.font.Font(None, 36)
    label_paused = font.render('Paused', 1, (255, 255, 255))

    drawing = Drawing(window_width, window_height)
    drawing.add_layer()

    drawing_mode = False
    drawing_color = (255, 0, 0)
    drawing_radius = 5
    
    running = True
    while running:
        screen.fill((255, 255, 255))

        display_frame(original_frame, screen)
        draw_button(screen, forward_button, "Forward")
        draw_button(screen, rewind_button, "Rewind")
        draw_frame_number(screen, current_frame)

        pygame.display.flip()

        for event in pygame.event.get():
            if event.type == QUIT:
                running = False
            elif event.type == MOUSEBUTTONDOWN:
                if forward_button.collidepoint(event.pos):
                    current_frame = forward_click(current_frame, total_frames)
                    original_frame = get_frame(video, current_frame)
                elif rewind_button.collidepoint(event.pos):
                    current_frame = rewind_click(current_frame)
                    original_frame = get_frame(video, current_frame)

    while True:
        for event in pygame.event.get():
            if event.type == QUIT or (event.type == KEYDOWN and event.key == K_ESCAPE):
                pygame.quit()
                sys.exit()

            if event.type == KEYDOWN:
                if event.key == K_SPACE:
                    paused = not paused

                if event.key == K_o:
                    video_file = open_file()
                    if cap is not None:
                        cap.release()
                    cap = cv2.VideoCapture(video_file)
                    paused = True

                if event.key == K_d:
                    drawing_mode = not drawing_mode

                if event.key == K_RIGHT:
                    if current_frame < len(drawing.layers) - 1:
                        current_frame += 1

                if event.key == K_LEFT:
                    if current_frame > 0:
                        current_frame -= 1

            if drawing_mode and event.type == MOUSEBUTTONDOWN and event.button == 1:
                pygame.draw.circle(drawing.layers[current_frame], drawing_color, event.pos, drawing_radius)

            if drawing_mode and event.type == MOUSEMOTION and event.buttons[0] == 1:
                start_pos = event.pos
                end_pos = (event.pos[0] - event.rel[0], event.pos[1] - event.rel[1])
                pygame.draw.line(drawing.layers[current_frame], drawing_color, start_pos, end_pos, 2 * drawing_radius)

        screen.fill((0, 0, 0))

        if cap is not None:
            if not paused:
                ret, frame = cap.read()
                if ret:
                    current_frame = int(cap.get(cv2.CAP_PROP_POS_FRAMES))
                    if current_frame >= len(drawing.layers):
                        drawing.add_layer(drawing.get_empty_image())
                    display_frame(screen, frame, 0, 0, window_width, window_height)
                    last_frame = frame.copy()
                else:
                    # If the video reaches the end, rewind it and pause
                    cap.set(cv2.CAP_PROP_POS_FRAMES, 0)
                    paused = True

            elif last_frame is not None:
                display_frame(screen, last_frame, 0, 0, window_width, window_height)

            if paused:
                screen.blit(label_paused, (10, 50))
                

        drawing.draw(screen, current_frame)
        pygame.display.update()

    video.release()
    cv2.destroyAllWindows()
    pygame.quit()

if __name__ == "__main__":
    main()