
"""
╔══════════════════════════════════════════════════════════════╗
║          PINGPONG BOUNCE MANIA  –  Basketball Edition        ║
║                                                              ║
║  Developer  : [Your Name Here]                               ║
║  Course     : Computer Graphics Programming                  ║
║  Library    : Pygame                                         ║
║  Modes      : Player vs Player  |  Player vs Bot             ║
╚══════════════════════════════════════════════════════════════╝
"""

import pygame
import sys
import math
import random

# ─────────────────────────────────────────────────────────────
#  INITIALIZE
# ─────────────────────────────────────────────────────────────
pygame.init()

SCREEN_W, SCREEN_H = 900, 600
FPS                = 60
WIN_SCORE          = 7          # First to this score wins

# ─────────────────────────────────────────────────────────────
#  COLOR PALETTE
# ─────────────────────────────────────────────────────────────
BG_DARK   = ( 10,  15,  25)
COURT_CLR = ( 20,  30,  46)
LINE_CLR  = ( 38,  54,  78)
WHITE     = (255, 255, 255)
ORANGE    = (226, 104,  25)
ORG_DARK  = (155,  60,   8)
ORG_LIGHT = (255, 148,  55)
BLUE      = ( 54, 145, 255)
GOLD      = (255, 195,  38)
RED       = (255,  68,  68)
GREY      = (155, 168, 185)
DIM       = ( 75,  85, 105)

# ─────────────────────────────────────────────────────────────
#  DISPLAY & CLOCK
# ─────────────────────────────────────────────────────────────
screen = pygame.display.set_mode((SCREEN_W, SCREEN_H))
pygame.display.set_caption("PingPong Bounce Mania  –  Basketball Edition")
clock  = pygame.time.Clock()

# ─────────────────────────────────────────────────────────────
#  FONTS  (fallback to default if Impact/Arial unavailable)
# ─────────────────────────────────────────────────────────────
def _load_font(name, size, bold=False):
    try:
        return pygame.font.SysFont(name, size, bold=bold)
    except Exception:
        return pygame.font.SysFont(None, size)

F_TITLE = _load_font("Impact", 68)
F_BIG   = _load_font("Arial",  46, bold=True)
F_MED   = _load_font("Arial",  32, bold=True)
F_SM    = _load_font("Arial",  22)
F_XS    = _load_font("Arial",  17)


# ═════════════════════════════════════════════════════════════
#  DRAWING HELPERS
# ═════════════════════════════════════════════════════════════

def blit_center(surf, cy):
    """Blit *surf* centered horizontally at vertical position *cy*."""
    screen.blit(surf, surf.get_rect(center=(SCREEN_W // 2, cy)))


def draw_basketball(cx, cy, radius):
    """
    Draw a realistic-looking basketball at pixel (cx, cy).
    Uses circles + ellipses for the seam lines + a highlight.
    """
    cx, cy, r = int(cx), int(cy), int(radius)
    if r < 3:
        return

    # ── Base orange fill
    pygame.draw.circle(screen, ORANGE, (cx, cy), r)

    # ── Seam lines  (dark brown ellipses at ±offset)
    sw  = max(2, r // 7)          # seam stroke width
    sc  = (22, 10, 2)             # seam color

    # Horizontal seam (thin horizontal ellipse)
    hrect = pygame.Rect(cx - r, cy - int(r * 0.22), r * 2, int(r * 0.44))
    pygame.draw.ellipse(screen, sc, hrect, sw)

    # Vertical seam (thin vertical ellipse)
    vrect = pygame.Rect(cx - int(r * 0.25), cy - r, int(r * 0.50), r * 2)
    pygame.draw.ellipse(screen, sc, vrect, sw)

    # ── Specular highlight (top-left)
    hr   = max(3, r // 3)
    hx   = cx - r // 3
    hy   = cy - r // 3
    hs   = pygame.Surface((hr * 2, hr * 2), pygame.SRCALPHA)
    pygame.draw.circle(hs, (255, 205, 145, 110), (hr, hr), hr)
    screen.blit(hs, (hx - hr, hy - hr))

    # ── Dark outline
    pygame.draw.circle(screen, ORG_DARK, (cx, cy), r, max(2, r // 9))


def draw_court():
    """Render the basketball-court-inspired background."""
    screen.fill(BG_DARK)

    court = pygame.Rect(20, 15, SCREEN_W - 40, SCREEN_H - 30)
    pygame.draw.rect(screen, COURT_CLR, court, border_radius=10)

    # Dashed center divider line
    cx = SCREEN_W // 2
    y  = court.top + 6
    while y < court.bottom - 6:
        pygame.draw.line(screen, LINE_CLR,
                         (cx, y), (cx, min(y + 14, court.bottom - 6)), 2)
        y += 26

    # Center circle
    pygame.draw.circle(screen, LINE_CLR, (SCREEN_W // 2, SCREEN_H // 2), 65, 2)
    pygame.draw.circle(screen, LINE_CLR, (SCREEN_W // 2, SCREEN_H // 2),  4)

    # Left three-point arc
    pygame.draw.arc(screen, LINE_CLR,
                    pygame.Rect(court.left + 10, SCREEN_H // 2 - 118, 160, 236),
                    math.radians(-90), math.radians(90), 2)

    # Right three-point arc
    pygame.draw.arc(screen, LINE_CLR,
                    pygame.Rect(court.right - 170, SCREEN_H // 2 - 118, 160, 236),
                    math.radians(90), math.radians(270), 2)

    # Court outer border
    pygame.draw.rect(screen, LINE_CLR, court, 2, border_radius=10)


def draw_hud(lname, rname, ls, rs, mode):
    """Draw the scoreboard strip and control hints."""
    # Score bar background
    bar = pygame.Rect(SCREEN_W // 2 - 172, 5, 344, 50)
    pygame.draw.rect(screen, (16, 24, 38), bar, border_radius=10)
    pygame.draw.rect(screen, LINE_CLR, bar, 1, border_radius=10)

    # Main score
    blit_center(F_BIG.render(f"{ls}  :  {rs}", True, WHITE), 32)

    # Player name tags
    screen.blit(F_XS.render(lname, True, BLUE),    (SCREEN_W // 2 - 158, 12))
    screen.blit(F_XS.render(rname, True, RED),     (SCREEN_W // 2 +  90, 12))
    blit_center(F_XS.render(f"First to {WIN_SCORE}", True, GOLD), 47)

    # Control hints (left side)
    screen.blit(F_XS.render("W / S", True, DIM), (35, 25))

    # Control hints (right side)
    right_hint = "UP / DOWN" if mode == "pvp" else "BOT"
    rh = F_XS.render(right_hint, True, DIM)
    screen.blit(rh, (SCREEN_W - 30 - rh.get_width(), 25))

    # ESC hint
    esc = F_XS.render("ESC = Menu", True, (65, 75, 92))
    screen.blit(esc, (SCREEN_W - 115, SCREEN_H - 20))


# ═════════════════════════════════════════════════════════════
#  GAME OBJECTS
# ═════════════════════════════════════════════════════════════

class Ball:
    RADIUS = 18

    def __init__(self):
        self.trail = []
        self.reset()

    def reset(self):
        self.x = float(SCREEN_W // 2)
        self.y = float(SCREEN_H // 2)

        # Random launch angle ±28°, random left/right direction
        angle     = random.uniform(-28, 28)
        base_spd  = 5.5
        direction = random.choice([-1, 1])
        self.vx   = direction * base_spd * math.cos(math.radians(angle))
        self.vy   =            base_spd * math.sin(math.radians(angle))
        self.trail = []

    def update(self):
        # Store position for motion trail
        self.trail.append((self.x, self.y))
        if len(self.trail) > 7:
            self.trail.pop(0)

        self.x += self.vx
        self.y += self.vy

        # Bounce off top/bottom court walls (with small margin)
        if self.y - self.RADIUS <= 15:
            self.y  = 15 + self.RADIUS
            self.vy = abs(self.vy)
        elif self.y + self.RADIUS >= SCREEN_H - 15:
            self.y  = SCREEN_H - 15 - self.RADIUS
            self.vy = -abs(self.vy)

    def speed_up(self):
        """Slightly accelerate after each paddle hit (cap at 14 px/frame)."""
        spd = math.hypot(self.vx, self.vy)
        if spd < 14:
            self.vx *= 1.06
            self.vy *= 1.06

    def draw(self):
        # Draw fading motion trail
        for i, (tx, ty) in enumerate(self.trail):
            alpha = int(90 * i / max(len(self.trail), 1))
            r     = max(3, self.RADIUS - (len(self.trail) - i) * 2)
            ts    = pygame.Surface((r * 2, r * 2), pygame.SRCALPHA)
            pygame.draw.circle(ts, (ORG_DARK[0], ORG_DARK[1], ORG_DARK[2], alpha),
                               (r, r), r)
            screen.blit(ts, (int(tx - r), int(ty - r)))

        # Draw the basketball
        draw_basketball(self.x, self.y, self.RADIUS)

    def get_rect(self):
        return pygame.Rect(
            self.x - self.RADIUS, self.y - self.RADIUS,
            self.RADIUS * 2,      self.RADIUS * 2
        )


class Paddle:
    W   = 14   # pixel width
    H   = 88   # pixel height
    SPD = 7    # pixels per frame

    def __init__(self, side):
        """side: 'left' or 'right'"""
        self.side    = side
        self.x       = 50 if side == "left" else SCREEN_W - 50
        self.y       = float(SCREEN_H // 2 - self.H // 2)
        self.score   = 0
        self.flash_t = 0   # hit-flash timer

    # ── Human control ───────────────────────────────────────
    def move_human(self, up, down):
        if up:   self.y -= self.SPD
        if down: self.y += self.SPD
        self._clamp()

    # ── Bot control ─────────────────────────────────────────
    def move_bot(self, target_y, difficulty=0.80):
        """
        Move toward target_y at a fraction of full speed.
        difficulty (0.0–1.0) controls reaction speed.
        A small dead-zone prevents jitter.
        """
        center = self.y + self.H / 2
        error  = target_y - center
        if abs(error) > 4:
            step   = self.SPD * difficulty * min(1.0, abs(error) / 50.0)
            self.y += math.copysign(step, error)
        self._clamp()

    def _clamp(self):
        self.y = max(15.0, min(float(SCREEN_H - 15 - self.H), self.y))

    def trigger_flash(self):
        self.flash_t = 10

    def draw(self):
        if self.flash_t > 0:
            self.flash_t -= 1
            color = BLUE if self.side == "left" else RED
        else:
            color = (218, 224, 234)

        rect = pygame.Rect(self.x - self.W // 2, int(self.y), self.W, self.H)
        pygame.draw.rect(screen, color, rect, border_radius=7)

        # Inner highlight stripe
        inner = rect.inflate(-4, -10)
        hi    = tuple(min(255, c + 48) for c in color)
        pygame.draw.rect(screen, hi, inner, border_radius=5)

        # Edge outline
        pygame.draw.rect(screen, (88, 100, 116), rect, 2, border_radius=7)

    def get_rect(self):
        return pygame.Rect(self.x - self.W // 2, int(self.y), self.W, self.H)


# ═════════════════════════════════════════════════════════════
#  COLLISION DETECTION
# ═════════════════════════════════════════════════════════════

def handle_collision(ball, paddle):
    """
    Detect ball-paddle overlap and redirect the ball.
    The angle of reflection depends on WHERE on the paddle the ball hits:
      - Center hit  → nearly horizontal
      - Edge hit    → up to ±55° angle
    """
    if not ball.get_rect().colliderect(paddle.get_rect()):
        return

    # Fraction along paddle height where ball hit (0 = top, 1 = bottom)
    hit_frac = (ball.y - paddle.y) / paddle.H
    hit_frac = max(0.0, min(1.0, hit_frac))

    angle = (hit_frac - 0.5) * 110     # maps 0-1 → ±55 degrees
    spd   = math.hypot(ball.vx, ball.vy)

    if paddle.side == "left":
        ball.vx =  abs(spd * math.cos(math.radians(angle)))
        ball.x  = paddle.x + paddle.W // 2 + ball.RADIUS + 2   # push out
    else:
        ball.vx = -abs(spd * math.cos(math.radians(angle)))
        ball.x  = paddle.x - paddle.W // 2 - ball.RADIUS - 2

    ball.vy = spd * math.sin(math.radians(angle))
    ball.speed_up()
    paddle.trigger_flash()


# ═════════════════════════════════════════════════════════════
#  SCREEN: MAIN MENU
# ═════════════════════════════════════════════════════════════

def screen_menu():
    """
    Show the mode-selection menu.
    Returns 'pvp', 'pvbot', or None (quit).
    """
    sel   = 0     # currently highlighted option
    theta = 0.0   # animation timer

    while True:
        theta += 0.04
        draw_court()

        # Animated floating basketballs
        draw_basketball(SCREEN_W // 2 - 235,
                        200 + int(math.sin(theta) * 9), 28)
        draw_basketball(SCREEN_W // 2 + 235,
                        200 + int(math.sin(theta + 1.2) * 9), 28)

        # Title
        ty = 97 + int(math.sin(theta * 0.7) * 4)
        blit_center(F_TITLE.render("PINGPONG BOUNCE MANIA", True, ORG_LIGHT), ty)
        blit_center(F_SM.render("Basketball Edition", True, GOLD), ty + 72)

        # Section label
        blit_center(F_MED.render("SELECT GAME MODE", True, GREY), 268)

        # Mode option buttons
        options = [
            ("PLAYER  vs  PLAYER",
             "Left: W / S       Right: UP / DOWN"),
            ("PLAYER  vs  BOT",
             "Left: W / S       Right: AI-controlled"),
        ]
        for i, (title, hint) in enumerate(options):
            br     = pygame.Rect(SCREEN_W // 2 - 245, 310 + i * 108, 490, 80)
            active = (i == sel)

            pygame.draw.rect(screen, BLUE if active else COURT_CLR,
                             br, border_radius=14)
            pygame.draw.rect(screen, WHITE if active else LINE_CLR,
                             br, 2, border_radius=14)

            blit_center(F_MED.render(title, True,
                                     WHITE if active else GREY),
                        br.centery - 12)
            blit_center(F_XS.render(hint, True,
                                    (225, 235, 245) if active else (82, 94, 112)),
                        br.centery + 24)

        # ── Student info panel (bottom of menu) ─────────────
        info_lines = [
            ("Name    :", "Addymen Salim"),
            ("Section :", "BSIT3 - PM"),
            ("Project :", "PingPong Bounce Mania"),
        ]
        panel_w, panel_h = 310, 60
        panel_x = SCREEN_W // 2 - panel_w // 2
        panel_y = SCREEN_H - 88
        info_panel = pygame.Rect(panel_x, panel_y, panel_w, panel_h)
        pygame.draw.rect(screen, (14, 21, 34), info_panel, border_radius=9)
        pygame.draw.rect(screen, LINE_CLR,     info_panel, 1, border_radius=9)

        for row, (label, value) in enumerate(info_lines):
            row_y = panel_y + 8 + row * 17
            lbl_s = F_XS.render(label, True, GOLD)
            val_s = F_XS.render(value, True, WHITE)
            screen.blit(lbl_s, (panel_x + 12,                   row_y))
            screen.blit(val_s, (panel_x + 12 + lbl_s.get_width() + 5, row_y))

        # Nav hint — sits just below the panel
        blit_center(F_XS.render(
            "UP / DOWN  select   |   ENTER  confirm   |   ESC  quit",
            True, (72, 84, 105)), SCREEN_H - 8)

        pygame.display.flip()
        clock.tick(FPS)

        # Event handling
        for ev in pygame.event.get():
            if ev.type == pygame.QUIT:
                return None

            if ev.type == pygame.KEYDOWN:
                if ev.key == pygame.K_ESCAPE:
                    return None

                if ev.key in (pygame.K_UP, pygame.K_w):
                    sel = (sel - 1) % 2
                if ev.key in (pygame.K_DOWN, pygame.K_s):
                    sel = (sel + 1) % 2

                if ev.key == pygame.K_RETURN:
                    return "pvp" if sel == 0 else "pvbot"


# ═════════════════════════════════════════════════════════════
#  SCREEN: WINNER ANNOUNCEMENT
# ═════════════════════════════════════════════════════════════

def screen_winner(winner_name, left_score, right_score):
    """
    Show the winner screen.
    Returns 'replay', 'menu', or 'quit'.
    """
    theta = 0.0
    while True:
        theta += 0.04
        draw_court()

        # Dark overlay
        ov = pygame.Surface((SCREEN_W, SCREEN_H), pygame.SRCALPHA)
        ov.fill((0, 0, 0, 165))
        screen.blit(ov, (0, 0))

        # Panel
        panel = pygame.Rect(SCREEN_W // 2 - 295, SCREEN_H // 2 - 195, 590, 390)
        pygame.draw.rect(screen, (16, 24, 38), panel, border_radius=20)
        pygame.draw.rect(screen, GOLD, panel, 3, border_radius=20)

        # Content
        blit_center(F_BIG.render("WINNER!", True, GOLD),                       SCREEN_H // 2 - 148)
        blit_center(F_BIG.render(winner_name, True, WHITE),                    SCREEN_H // 2 -  92)
        blit_center(F_BIG.render(f"{left_score}  —  {right_score}", True, GREY), SCREEN_H // 2 -  38)

        # Animated basketball decorations
        draw_basketball(SCREEN_W // 2 - 215,
                        SCREEN_H // 2 - 90 + int(math.sin(theta) * 7), 24)
        draw_basketball(SCREEN_W // 2 + 215,
                        SCREEN_H // 2 - 90 + int(math.sin(theta + 1.1) * 7), 24)

        # Action options
        blit_center(F_MED.render("ENTER   — Play Again",  True, BLUE),         SCREEN_H // 2 + 58)
        blit_center(F_MED.render("M       — Main Menu",   True, GREY),         SCREEN_H // 2 + 104)
        blit_center(F_MED.render("ESC     — Quit Game",   True, (128,140,155)),SCREEN_H // 2 + 148)

        pygame.display.flip()
        clock.tick(FPS)

        for ev in pygame.event.get():
            if ev.type == pygame.QUIT:     return "quit"
            if ev.type == pygame.KEYDOWN:
                if ev.key == pygame.K_RETURN: return "replay"
                if ev.key == pygame.K_m:      return "menu"
                if ev.key == pygame.K_ESCAPE: return "quit"


# ═════════════════════════════════════════════════════════════
#  POINT-SCORED FLASH
# ═════════════════════════════════════════════════════════════

def flash_point(player_name, color):
    """Briefly show '+1 <name>' in the center of the screen."""
    txt = F_BIG.render(f"+1  {player_name}!", True, color)
    screen.blit(txt, txt.get_rect(center=(SCREEN_W // 2, SCREEN_H // 2)))
    pygame.display.flip()
    pygame.time.wait(680)


# ═════════════════════════════════════════════════════════════
#  MAIN GAMEPLAY LOOP
# ═════════════════════════════════════════════════════════════

def run_game(mode):
    """
    Run one full match.
    mode: 'pvp' or 'pvbot'
    Returns 'replay', 'menu', or 'quit'.
    """
    left_name  = "PLAYER 1" if mode == "pvp" else "PLAYER"
    right_name = "PLAYER 2" if mode == "pvp" else "BOT"

    paddle_L = Paddle("left")
    paddle_R = Paddle("right")
    ball     = Ball()

    # Bot difficulty  (0.0 = very easy, 1.0 = near-perfect)
    # 0.80 gives a challenging but beatable opponent
    BOT_DIFFICULTY = 0.80

    while True:
        # ── Event handling ──────────────────────────────────
        for ev in pygame.event.get():
            if ev.type == pygame.QUIT:
                return "quit"
            if ev.type == pygame.KEYDOWN:
                if ev.key == pygame.K_ESCAPE:
                    return "menu"

        # ── Input / movement ────────────────────────────────
        keys = pygame.key.get_pressed()
        paddle_L.move_human(keys[pygame.K_w], keys[pygame.K_s])

        if mode == "pvp":
            paddle_R.move_human(keys[pygame.K_UP], keys[pygame.K_DOWN])
        else:
            # Bot AI: predict where ball will cross the right paddle's x-line
            if ball.vx > 0.5:
                # Time until ball reaches paddle_R.x
                dt       = (paddle_R.x - ball.x) / ball.vx
                pred_y   = ball.y + ball.vy * dt

                # Simulate bounces off top/bottom walls
                arena_h  = SCREEN_H - 30   # playable height
                pred_y  -= 15              # normalize to 0-based
                pred_y   = pred_y % (arena_h * 2)
                if pred_y > arena_h:
                    pred_y = arena_h * 2 - pred_y
                pred_y  += 15              # restore offset

            else:
                # Ball moving away – drift bot back toward center
                pred_y = float(SCREEN_H // 2)

            paddle_R.move_bot(pred_y, BOT_DIFFICULTY)

        # ── Physics update ──────────────────────────────────
        ball.update()

        # ── Collision detection ─────────────────────────────
        handle_collision(ball, paddle_L)
        handle_collision(ball, paddle_R)

        # ── Scoring check ───────────────────────────────────
        if ball.x - Ball.RADIUS <= 20:
            # Ball passed left wall → right player scores
            paddle_R.score += 1
            draw_court()
            draw_hud(left_name, right_name, paddle_L.score, paddle_R.score, mode)
            paddle_L.draw(); paddle_R.draw(); ball.draw()
            flash_point(right_name, RED)
            ball.reset()

        elif ball.x + Ball.RADIUS >= SCREEN_W - 20:
            # Ball passed right wall → left player scores
            paddle_L.score += 1
            draw_court()
            draw_hud(left_name, right_name, paddle_L.score, paddle_R.score, mode)
            paddle_L.draw(); paddle_R.draw(); ball.draw()
            flash_point(left_name, BLUE)
            ball.reset()

        # ── Win condition ────────────────────────────────────
        if paddle_L.score >= WIN_SCORE:
            return screen_winner(left_name,  paddle_L.score, paddle_R.score)
        if paddle_R.score >= WIN_SCORE:
            return screen_winner(right_name, paddle_L.score, paddle_R.score)

        # ── Render frame ─────────────────────────────────────
        draw_court()
        draw_hud(left_name, right_name, paddle_L.score, paddle_R.score, mode)
        paddle_L.draw()
        paddle_R.draw()
        ball.draw()

        pygame.display.flip()
        clock.tick(FPS)


# ═════════════════════════════════════════════════════════════
#  ENTRY POINT
# ═════════════════════════════════════════════════════════════

def main():
    mode = screen_menu()
    if mode is None:
        pygame.quit()
        sys.exit()

    while True:
        outcome = run_game(mode)

        if outcome == "replay":
            # Restart the same mode immediately
            continue
        elif outcome == "menu":
            # Go back to main menu to possibly pick a different mode
            mode = screen_menu()
            if mode is None:
                break
        else:
            # "quit" or window closed
            break

    pygame.quit()
    sys.exit()


if __name__ == "__main__":
    main()
