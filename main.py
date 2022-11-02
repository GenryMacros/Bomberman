from game import Game

if __name__ == '__main__':
    screen_resolution = (704, 704)
    game = Game(screen_resolution, frames_per_second=30)
    game.run()
