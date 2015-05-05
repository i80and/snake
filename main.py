#!/usr/bin/env python3
import tkinter
import math
import random

EMPTY = 0
NORTH = 1
EAST = 2
SOUTH = 3
WEST = 4
NO_DIRECTION = 5
FOOD = 6


def move_point(point, direction):
    x, y = point

    if direction == NORTH:
        return (x, y - 1)

    if direction == EAST:
        return (x + 1, y)

    if direction == SOUTH:
        return (x, y + 1)

    if direction == WEST:
        return (x - 1, y)

    if direction == NO_DIRECTION:
        return point

    raise ValueError('Invalid direction: {0}'.format(direction))


class Map:
    def __init__(self, width, height):
        self.width = width
        self.height = height
        self.grid = []
        self.head = (math.floor(width / 2), math.floor(height / 2))
        self.tail = self.head
        self.length = 1

        for _ in range((width * height) + 1):
            self.grid.append(EMPTY)

        self[self.head] = NO_DIRECTION

        self.place_food()

    def _check_point(self, point):
        x, y = point

        if x < 0 or x >= self.width:
            raise IndexError(point)

        if y < 0 or y >= self.height:
            raise IndexError(point)

    def __getitem__(self, point):
        x, y = point
        self._check_point(point)
        return self.grid[(y * self.width) + x]

    def __setitem__(self, point, value):
        x, y = point
        self._check_point(point)
        self.grid[(y * self.width) + x] = value

    def move(self, direction):
        events = []

        new_point = move_point(self.head, direction)
        if self.check_collision(new_point):
            events.append('die')
            return events

        if self[self.head] == NO_DIRECTION:
            self[self.head] = direction

        self[self.head] = direction
        self.head = new_point

        if self[new_point] == FOOD:
            self.place_food()
            self.length += 1
            events.append('eat')
        else:
            new_tail = move_point(self.tail, self[self.tail])
            self[self.tail] = EMPTY
            self.tail = new_tail

        self[new_point] = direction
        return events

    def random_point(self):
        return (random.randint(0, self.width - 1), random.randint(0, self.height - 1))

    def place_food(self):
        while True:
            point = self.random_point()
            if self[point] != EMPTY:
                continue

            self[point] = FOOD
            return

    def check_collision(self, point):
        try:
            self._check_point(point)
        except IndexError:
            return True

        if self[point] == FOOD:
            return False

        if self[point] != EMPTY:
            return True

        return False


class SnakeGUI:
    def __init__(self):
        self.scale = 20
        self.map = Map(30, 30)
        self.master = tkinter.Tk()
        self.master.wm_title('Snake')
        self.canvas = tkinter.Canvas(
            self.master,
            width=(self.map.width * self.scale),
            height=(self.map.width * self.scale))

        self.pause_button_text = tkinter.StringVar()
        self.pause_button_text.set('Start')
        self.pause_button = tkinter.Button(
            self.master,
            textvariable=self.pause_button_text,
            command=self._on_button)

        self.canvas.pack()
        self.pause_button.pack()

        self.text = ''
        self.__paused = True
        self.reset()

    def reset(self):
        self.direction = NORTH
        self.interval = 500

    @property
    def paused(self):
        return self.__paused

    @paused.setter
    def paused(self, val):
        self.__paused = val
        if self.__paused:
            self.pause_button_text.set('Start')
        else:
            self.pause_button_text.set('Pause')

        self.pause_button.update()

    def loop(self):
        self._tick()
        self.master.bind('<Key>', self._on_key)
        tkinter.mainloop()

    def draw(self):
        self.canvas.delete('all')

        for y in range(-1, (self.map.height + 1)):
            for x in range(-1, (self.map.width + 1)):
                point = (x, y)
                try:
                    value = self.map[point]
                    if value == FOOD:
                        self._draw_food(point)
                    elif value > EMPTY:
                        self._draw_snake(point)
                except IndexError:
                    self._draw_wall(point)

        self.canvas.create_text(
            ((self.map.width * self.scale / 2), 10), text=self.text)

    def on_die(self):
        self.text = 'Game over! Score: {0}'.format(self.map.length - 1)
        self.map = Map(30, 30)
        self.reset()
        self.paused = True
        self.pause_button.config(text='Pause')

    def on_eat(self):
        if self.interval > 10:
            self.interval -= 10

    def _on_button(self):
        self.paused = not self.paused
        self.draw()

    def _on_key(self, event):
        if event.char == 'w' or event.keysym == 'Up':
            self.direction = NORTH
        elif event.char == 'd' or event.keysym == 'Right':
            self.direction = EAST
        elif event.char == 's' or event.keysym == 'Down':
            self.direction = SOUTH
        elif event.char == 'a' or event.keysym == 'Left':
            self.direction = WEST
        elif event.char == ' ':
            self.paused = not self.paused

        self.draw()

    def _tick(self):
        self.master.after(self.interval, self._tick)

        if not self.paused:
            for event in self.map.move(self.direction):
                if event == 'eat':
                    self.on_eat()
                elif event == 'die':
                    self.on_die()
            self.draw()

    def _draw_wall(self, point):
        self._draw_point(point, 'black')

    def _draw_food(self, point):
        self._draw_point(point, 'blue')

    def _draw_snake(self, point):
        self._draw_point(point, 'black')

    def _draw_point(self, point, color):
        x, y = point
        self.canvas.create_rectangle(
            x * self.scale,
            y * self.scale,
            x * self.scale + self.scale,
            y * self.scale + self.scale,
            fill=color)

if __name__ == '__main__':
    game = SnakeGUI()
    game.loop()
