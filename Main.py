import pygame
import math
import random

# WORLD IMPORTS
from World.Crate import Crate
from World.Cable import Cable
from World.Cloud import Cloud
from World.Terrain import Terrain
from World.Particle import Particle
from World.Helicopter import Helicopter

# ENGINE IMPORTS
from Engine.Mesh import Mesh
from Engine.Camera import Camera
from Engine.Pipeline import Pipeline
from Engine.MatrixMath import Vector3, Matrix4

# --- SETUP ---
pygame.init()
WIDTH, HEIGHT = 800, 600
screen = pygame.display.set_mode((WIDTH, HEIGHT))
clock = pygame.time.Clock()

HUD_font = pygame.font.SysFont("georgia", 25, bold=False)
guide_font = pygame.font.SysFont("georgia", 14, bold=False)

pygame.mouse.set_visible(False)
pygame.event.set_grab(True)

# --- INIT ENGINE OBJECTS ---
camera = Camera()
pipeline = Pipeline(WIDTH, HEIGHT)

# World Generation
terrain = Terrain(width=24, depth=24, scale=10.0)

# Actors
player = Helicopter(0, 15, 0)
crate = Crate(5.0, 10.0, 5.0)
shadow_mesh = Mesh.make_flat_quad(size=2.5)

# Physics Objects
cable = Cable(num_segments=10, total_length=10.0)
rope_stiffness = 600.0
rope_damping = 10.0

# Cloud System
clouds = []
for i in range(4):
    cx = random.uniform(-120, 120)
    cy = random.uniform(100, 120)
    cz = random.uniform(-120, 120)
    clouds.append(Cloud(cx, cy, cz))

# Particle System
dust_particles = []

# Camera Setup
camera.mode = 'chase'
camera.follow_distance = 12.0
camera.pitch = 25.0


def render_mesh(screen, pipeline, mesh, camera, world_matrix, face_color=None, wire_color=(0, 0, 0), draw_wires=True, alpha=255):
    """Helper to render a mesh using the pipeline and Pygame drawing calls."""
    processed_tris = pipeline.process_mesh(
        mesh, camera, world_matrix, base_color=face_color)

    # Create temp surface for alpha blending if needed
    if alpha < 255:
        target_surface = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
    else:
        target_surface = screen

    for tri_data in processed_tris:
        tri_points = tri_data[0]
        tri_color = tri_data[2]
        flags = tri_data[3]

        p1 = (tri_points[0].x, tri_points[0].y)
        p2 = (tri_points[1].x, tri_points[1].y)
        p3 = (tri_points[2].x, tri_points[2].y)

        # Draw faces
        if alpha < 255:
            rgba_color = (tri_color[0], tri_color[1], tri_color[2], alpha)
            pygame.draw.polygon(target_surface, rgba_color, [p1, p2, p3])
        else:
            pygame.draw.polygon(screen, tri_color, [p1, p2, p3])

        # Draw wireframe
        if draw_wires:
            if flags[0]:
                pygame.draw.line(screen, wire_color, p1, p2, 1)
            if flags[1]:
                pygame.draw.line(screen, wire_color, p2, p3, 1)
            if flags[2]:
                pygame.draw.line(screen, wire_color, p3, p1, 1)

    if alpha < 255:
        screen.blit(target_surface, (0, 0))


# --- MAIN LOOP ---
running = True
while running:
    # 1. EVENTS
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_ESCAPE:
                running = False

    # 2. PHYSICS UPDATE
    dt = 1.0 / 60.0

    # Object Updates
    player.update(dt, terrain)
    crate.update(dt, terrain)
    for c in clouds:
        c.update(dt, world_size=24)

    # --- TETHER PHYSICS ---
    heli_anchor = Vector3(player.pos.x, player.pos.y - 1.0, player.pos.z)
    crate_anchor = crate.pos

    # A. Verlet Simulation (Cable Slack)
    cable.update(dt, heli_anchor, crate_anchor)

    # B. Force Calculation (Spring Dynamics)
    diff = crate_anchor - heli_anchor
    dist = diff.magnitude()

    if dist > cable.total_length:
        direction = diff.normalize()
        stretch = dist - cable.total_length

        # Hooke's Law
        spring_force = direction * (stretch * rope_stiffness)

        # Damping
        rel_vel = crate.vel - player.vel
        vel_along_rope = rel_vel.dot(direction)
        damping_force = direction * (vel_along_rope * rope_damping)

        tension = spring_force + damping_force

        # Apply Forces (Newton's 3rd Law)
        accel_heli = tension * (1.0 / player.mass)
        player.vel = player.vel + (accel_heli * dt)

        accel_crate = tension * (-1.0 / crate.mass)
        crate.vel = crate.vel + (accel_crate * dt)

    # --- DUST PARTICLE PHYSICS ---
    # Update existing
    for i in range(len(dust_particles) - 1, -1, -1):
        p = dust_particles[i]
        p.update(dt)
        if p.is_dead():
            dust_particles.pop(i)

    # Spawn Emitter
    ground_h = terrain.get_height(player.pos.x, player.pos.z)
    altitude = player.pos.y - ground_h

    # Trigger: Low Altitude (< 15m) AND High Throttle (> 40%)
    if altitude < 15.0 and player.throttle > 40.0:
        if random.random() < 0.4:  # Spawn limiter
            spawn_count = 2 if altitude < 4.0 else 1

            for _ in range(spawn_count):
                offset_angle = random.uniform(0, 6.28)
                offset_dist = random.uniform(0, 2.0)

                px = player.pos.x + math.sin(offset_angle) * offset_dist
                pz = player.pos.z + math.cos(offset_angle) * offset_dist
                py = ground_h + 0.5

                # Velocity: Shoot OUTWARD from center
                speed = random.uniform(3.0, 6.0)
                vx = math.sin(offset_angle) * speed
                vz = math.cos(offset_angle) * speed
                vy = random.uniform(0.1, 0.5)

                dust_particles.append(
                    Particle(px, py, pz, Vector3(vx, vy, vz)))

    # 3. CAMERA UPDATE
    keys = pygame.key.get_pressed()
    mouse_delta = pygame.mouse.get_rel()
    cam_speed = 2.0

    if keys[pygame.K_UP]:
        camera.pitch += cam_speed
    if keys[pygame.K_DOWN]:
        camera.pitch -= cam_speed
    camera.pitch = max(-89.0, min(89.0, camera.pitch))

    if camera.mode == 'free':
        camera.update(keys, mouse_delta)
    elif camera.mode == 'chase':
        camera.chase(player)
    elif camera.mode == 'follow':
        camera.follow(player, mouse_delta)

    # 4. RENDER
    screen.fill((105, 175, 205))

    # --- PASS 1: TERRAIN & SHADOW ---
    mat_identity = Matrix4()
    render_mesh(screen, pipeline, terrain.mesh, camera, mat_identity,
                face_color=None, wire_color=(0, 50, 0), draw_wires=True)

    ground_y = terrain.get_height(player.pos.x, player.pos.z)
    shadow_pos = Vector3(player.pos.x, ground_y + 0.2, player.pos.z)
    mat_shadow = Matrix4.make_translation(
        shadow_pos.x, shadow_pos.y, shadow_pos.z)

    render_mesh(screen, pipeline, shadow_mesh, camera, mat_shadow,
                face_color=(0, 0, 0), draw_wires=False, alpha=100)

    # --- PASS 2: OBJECT QUEUE (Sorting) ---
    render_queue = []

    # Add Meshes
    d_player = camera.pos.distance_to(player.pos)
    render_queue.append({
        'type': 'mesh', 'dist': d_player, 'mesh': player.mesh,
        'matrix': player.get_world_matrix(), 'color': (100, 100, 100)
    })

    d_crate = camera.pos.distance_to(crate.pos)
    render_queue.append({
        'type': 'mesh', 'dist': d_crate, 'mesh': crate.mesh,
        'matrix': crate.get_world_matrix(), 'color': (255, 140, 0)
    })

    # Add Clouds
    mat_view = camera.get_view_matrix()
    for c in clouds:
        d_cloud = camera.pos.distance_to(c.pos)
        view_pos = mat_view.multiply_vector(c.pos)
        if view_pos.z > 1.0:
            render_queue.append(
                {'type': 'cloud', 'dist': d_cloud, 'obj': c, 'view_pos': view_pos})

    # Add Dust
    for p in dust_particles:
        d_dust = camera.pos.distance_to(p.pos)
        view_pos = mat_view.multiply_vector(p.pos)
        if view_pos.z > 0.5:
            render_queue.append(
                {'type': 'dust', 'dist': d_dust, 'obj': p, 'view_pos': view_pos})

    # Sort (Painter's Algorithm)
    render_queue.sort(key=lambda item: item['dist'], reverse=True)

    # Execute Draw
    for item in render_queue:
        if item['type'] == 'mesh':
            render_mesh(screen, pipeline, item['mesh'], camera, item['matrix'],
                        face_color=item['color'], draw_wires=False)

        elif item['type'] == 'cloud':
            c, view_pos = item['obj'], item['view_pos']
            for puff_offset, puff_size in c.puffs:
                world_puff = c.pos + puff_offset
                proj = pipeline.project_clipped_line(
                    world_puff, world_puff, camera)
                if proj is not None:
                    center_2d = (int(proj[0][0]), int(proj[0][1]))
                    radius = int((puff_size * 400.0) / view_pos.z)
                    if radius > 0:
                        target_rect = pygame.Rect(
                            center_2d[0]-radius, center_2d[1]-radius, radius*2, radius*2)
                        cloud_surf = pygame.Surface(
                            (radius*2, radius*2), pygame.SRCALPHA)
                        pygame.draw.circle(
                            cloud_surf, (255, 255, 255, 100), (radius, radius), radius)
                        screen.blit(cloud_surf, target_rect)

        elif item['type'] == 'dust':
            p, view_pos = item['obj'], item['view_pos']
            proj = pipeline.project_clipped_line(p.pos, p.pos, camera)
            if proj is not None:
                center_2d = (int(proj[0][0]), int(proj[0][1]))
                radius = int((p.base_size * 150.0) / view_pos.z)
                if radius > 0:
                    target_rect = pygame.Rect(
                        center_2d[0]-radius, center_2d[1]-radius, radius*2, radius*2)
                    dust_surf = pygame.Surface(
                        (radius*2, radius*2), pygame.SRCALPHA)
                    alpha = int(p.life * 150)
                    pygame.draw.circle(
                        dust_surf, (100, 90, 70, alpha), (radius, radius), radius)
                    screen.blit(dust_surf, target_rect)

    # --- PASS 3: CABLE & HUD ---
    real_dist = heli_anchor.distance_to(crate_anchor)
    is_taut = real_dist > cable.total_length
    rope_color = (255, 50, 50) if is_taut else (50, 50, 50)
    width = 3 if is_taut else 2

    for i in range(cable.num_segments):
        p1 = cable.nodes[i]
        p2 = cable.nodes[i+1]
        segment = pipeline.project_clipped_line(p1, p2, camera)
        if segment:
            pygame.draw.line(screen, rope_color,
                             (int(segment[0][0]), int(segment[0][1])),
                             (int(segment[1][0]), int(segment[1][1])), width)

    # HUD Stats
    screen.blit(HUD_font.render(
        f"THR: {int(player.throttle)}%", True, (255, 255, 0)), (10, 10))

    alt = player.pos.y - terrain.get_height(player.pos.x, player.pos.z)
    screen.blit(HUD_font.render(
        f"ALT: {int(alt)} m", True, (255, 255, 255)), (10, 40))

    vs = player.vel.y
    vs_color = (0, 255, 0) if vs >= 0 else (255, 100, 100)
    screen.blit(HUD_font.render(
        f"V.SPD: {vs:.1f} m/s", True, vs_color), (10, 70))

    hs = math.sqrt(player.vel.x**2 + player.vel.z**2)
    screen.blit(HUD_font.render(
        f"H.SPD: {hs:.1f} m/s", True, (255, 255, 255)), (10, 100))

    screen.blit(HUD_font.render(
        f"FPS: {int(clock.get_fps())}", True, (0, 0, 0)), (WIDTH - 105, 5))

    # Controls Guide
    guide_lines = [
        "W / S  : Pitch (Nose Down/Up)",
        "A / D  : Roll (Bank Left/Right)",
        "Q / E  : Yaw (Rotate Tail)",
        "SPACE  : Throttle Up (Release to Descend)",
        "ARROWS : Move Camera"
    ]
    guide_y = HEIGHT - (len(guide_lines) * 20) - 10
    screen.blit(guide_font.render("FLIGHT CONTROLS:",
                True, (255, 255, 0)), (10, guide_y - 25))

    for line in guide_lines:
        screen.blit(guide_font.render(
            line, True, (200, 200, 200)), (10, guide_y))
        guide_y += 20

    pygame.display.flip()
    clock.tick(60)

pygame.quit()
