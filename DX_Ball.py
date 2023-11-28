import sys
import random
from OpenGL.GL import *
from OpenGL.GLUT import *
from OpenGL.GLU import *
import math

# Global variables
bx = 400        # Ball x-coordinate
by = 50         # Ball y-coordinate
br = 10         # Ball radius
bdx = 2         # Ball x-axis velocity
bdy = 2         # Ball y-axis velocity

px = 350        # Paddle x-coordinate
py = 20         # Paddle y-coordinate
pw = 100        # Paddle width
ph = 10         # Paddle height

ww = 800        # Window width
wh = 600        # Window height

n_blocks_x = 10     # Number of blocks in x-direction
n_blocks_y = 6      # Number of blocks in y-direction
bw = ww // n_blocks_x   # Block width
bh = 30         # Block height

blx = [[1 for _ in range(n_blocks_x)] for _ in range(n_blocks_y)]  # 2D array representing the state of blocks (1: active, 0: destroyed)

pc = [           # Paddle colors
   (0.0, 1.0, 0.0),  # Green
   (1.0, 0.0, 0.0),  # Red
   (0.0, 0.0, 1.0),  # Blue
   (1.0, 1.0, 0.0),  # Yellow
]

cp_color = random.choice(pc)   # Current paddle color

game_over = False   # Flag indicating whether the game is over
is_paused = False   # Flag indicating whether the game is paused
scr = 0             # Player's score

def initialize():
   """
   Initialize the OpenGL environment and set up the window.
   """
   glutInit(sys.argv)
   glutInitDisplayMode(GLUT_DOUBLE | GLUT_RGB)
   glutInitWindowSize(ww, wh)
   glutCreateWindow(b"DX-Ball")
   glutDisplayFunc(draw)
   glutKeyboardFunc(keyboard)
   glutTimerFunc(16, update, 0)
   glClearColor(0.0, 0.0, 0.0, 0.0)
   gluOrtho2D(0, ww, 0, wh)

def draw_circle(x, y, r):
   """
   Draw a circle at the specified coordinates with the given radius.
   """
   num_segments = 100
   angle_increment = 2.0 * math.pi / num_segments

   glBegin(GL_TRIANGLE_FAN)

   for i in range(num_segments + 1):
       angle = i * angle_increment
       dx = r * math.cos(angle)
       dy = r * math.sin(angle)
       glVertex2f(x + dx, y + dy)

   glEnd()

def draw_rectangle(x, y, w, h, color):
   """
   Draw a rectangle at the specified coordinates with the given width, height, and color.
   """
   glColor3f(*color)
   glBegin(GL_QUADS)

   glVertex2f(x, y)
   glVertex2f(x + w, y)
   glVertex2f(x + w, y + h)
   glVertex2f(x, y + h)

   glEnd()

def draw_blocks():
   """
   Draw the blocks on the screen based on their state.
   """
   for i in range(n_blocks_y):
       for j in range(n_blocks_x):
           if blx[i][j]:
               if i == 0 or i == 5 or j == 0 or j == 9 or (1 < i < 4 and 3 <= j <= 6):
                   draw_rectangle(j * bw, wh - (i + 1) * bh, bw, bh, (0.5, 0.3, 1.7))  # Active blocks
               else:
                   draw_rectangle(j * bw, wh - (i + 1) * bh, bw, bh, (0.0, 0.0, 1.0))  # Other blocks

def draw_text(x, y, text):
   """
   Draw text at the specified coordinates.
   """
   glRasterPos2f(x, y)
   for char in text:
       glutBitmapCharacter(GLUT_BITMAP_HELVETICA_18, ord(char))

def draw_score():
   """
   Draw the player's score on the screen.
   """
   glColor3f(1.0, 1.0, 1.0)
   draw_text(ww - 100, wh - 30, f"Score: {scr}")

def draw():
   """
   The main draw function that renders the game elements on the screen.
   """
   global game_over

   glClear(GL_COLOR_BUFFER_BIT)

   glColor3f(1.0, 1.0, 1.0)
   draw_circle(bx, by, br)   # Draw the ball

   global cp_color
   draw_rectangle(px, py, pw, ph, cp_color)   # Draw the paddle

   draw_blocks()   # Draw the blocks

   draw_score()    # Draw the player's score

   if game_over:
       glColor3f(1.0, 0.0, 0.0)
       draw_text(ww // 2 - 50, wh // 2, "Game Over")
       glutSwapBuffers()
       return

   glutSwapBuffers()

def update(value):
   """
   Update the game state based on time.
   """
   global bx, by, bdx, bdy, game_over, scr

   if game_over:
       return

   if not is_paused:
       # Update ball position
       if scr > 10 and scr <= 20:
           bx += bdx + bdx // 4
           by += bdy + bdy // 4
       elif 20 < scr <= 40:
           bx += bdx + bdx // 2
           by += bdy + bdy // 2
       elif scr > 40:
           bx += bdx + bdx
           by += bdy + bdy
       else:
           bx += bdx
           by += bdy

       # Check for collisions with walls
       if bx + br > ww or bx - br < 0:
           bdx *= -1

       if by + br > wh:
           game_over = True
           bdy *= -1

       if by - br < 0:
           bdy *= -1

       # Check for collision with the paddle
       if (
           bx >= px
           and bx <= px + pw
           and by - br <= py + ph
       ):
           bdy *= -1
           change_paddle_color()

       # Check for collision with blocks
       hit_block_y = (wh - by) // bh
       hit_block_x = bx // bw
       if hit_block_y >= 0 and hit_block_y < n_blocks_y and hit_block_x >= 0 and hit_block_x < n_blocks_x and blx[hit_block_y][hit_block_x]:
           bdy *= -1
           blx[hit_block_y][hit_block_x] = 0
           scr += 2

       # Check for game over condition
       if by - br < 0:
           game_over = True

   glutPostRedisplay()
   glutTimerFunc(16, update, 0)

def change_paddle_color():
   """
   Change the color of the paddle randomly.
   """
   global cp_color
   cp_color = random.choice(pc)

def keyboard(key, x, y):
   """
   Handle keyboard inputs.
   """
   global px, is_paused

   if key == b'q':
       sys.exit(0)
   elif key == b'a' and px > 0:
       px -= 20
   elif key == b'd' and px + pw < ww:
       px += 20
   elif key == b'p':
       is_paused = not is_paused

if __name__ == "__main__":
   initialize()
   glutMainLoop()
