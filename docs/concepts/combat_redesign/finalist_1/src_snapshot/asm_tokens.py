"""asm_tokens: the ONE token table of the E10 design assembly (BRIEF 3.3 + R2 decisions Y1, Y2, Y6).  Every cluster module that had its own colour literal now reads this."""
HARM = (255, 68, 51)
HARM_UP = (255, 100, 82)         # fix 2: L1 threat marks lifted one value step (squint luminance 0.42 -> 0.52)
PENCIL_THREAT = (255, 28, 44)
GAIN = (123, 224, 123)
NET_CYAN = (92, 225, 255)
PENCIL_PLAN = (255, 226, 0)
SCHEDULE_ORANGE = (255, 140, 26)
SOAK = (58, 126, 243)            # fix 6: #3A7EF3 (Y1 #464EFF failed protan vs TRACE_VIOLET dE 2.4); sweep: dE76 >= 10 vs TRACE_VIOLET and LANE_PLUS1 in normal+deutan+protan+tritan
CRT_AMBER = (255, 176, 0)
BOSS_GOLD = (255, 196, 40)
RESIST_GOLD = (255, 210, 77)
CREAM = (255, 244, 214)
LANE_PLUS1 = (120, 170, 255)
LANE_PLUS2 = (236, 240, 255)
RIDER_LAV = (190, 160, 255)
TRACE_VIOLET = (160, 60, 255)
STEEL = (150, 162, 182)
STEEL_HI = (226, 233, 246)
INK = (12, 10, 22)
TERMINAL_BG = (5, 13, 28)
TEXT_HI = (242, 246, 255)
TEXT_MID = (175, 192, 214)
TEXT_LO = (122, 136, 156)
SCRIM = (2, 3, 10)
# Y6 kind colour set R (wave_rings): washes; token / arc-disc colour = wash x 1.40
KIND_WASH_R = {'Packet': (137, 63, 108), 'Worm': (95, 59, 122), 'Jammer': (57, 103, 164), 'Payload': (98, 51, 66), 'Ring': (113, 109, 149)}
KIND_TOKEN_F = 1.40
# HP grammar (BRIEF 3.11 / R1 X10): rounded segment r3, lost-now = HARM + 2 px white slash + ink, gone = dark socket + hairline
HP_R = 3.0
HP_SLASH_W = 2.0
HP_INK_W = 4.4
HP_GONE_HAIRLINE = 1.4
