import numpy as np
import matplotlib.pyplot as plt
from matplotlib.animation import FuncAnimation

# Simulation parameters
N = 30                     # Number of chain segments
g = 9.81                   # Gravity (adjust this value)
total_length = 2.0         # Total length of the chain
dt = 0.01                  # Time step size
iterations = 10            # Constraint iterations per frame
d = total_length / (N - 1) # Distance between masses

# Initialize positions
positions = np.zeros((N, 2))
for i in range(N):
    positions[i] = [0, -i * d]
previous_positions = np.copy(positions)

# Drag variables
selected_point = None
dragging = False
drag_offset = np.zeros(2)

# Set up figure and axes
fig, ax = plt.subplots()
line, = ax.plot([], [], 'o-', lw=2, markersize=4)
ax.set_xlim(-total_length, total_length)
ax.set_ylim(-total_length*1.5, 0.5)
ax.set_aspect('equal')
ax.grid(True)
ax.set_title(f"Draggable Falling Chain (g = {g} m/s²)")

# Mouse handlers
def on_press(event):
    global selected_point, dragging, drag_offset
    if event.inaxes != ax or event.button != 1:
        return
    
    # Find closest point
    click_pos = np.array([event.xdata, event.ydata])
    distances = np.linalg.norm(positions - click_pos, axis=1)
    closest = np.argmin(distances)
    
    if distances[closest] < 0.1:  # Selection threshold
        selected_point = closest
        drag_offset = positions[selected_point] - click_pos
        dragging = True

def on_motion(event):
    global positions, selected_point, drag_offset
    if not dragging or event.inaxes != ax or event.xdata is None:
        return
    
    # Update dragged point position
    positions[selected_point] = [event.xdata, event.ydata] + drag_offset

def on_release(event):
    global selected_point, dragging
    selected_point = None
    dragging = False

# Update mouse handlers
fig.canvas.mpl_connect('button_press_event', on_press)
fig.canvas.mpl_connect('motion_notify_event', on_motion)
fig.canvas.mpl_connect('button_release_event', on_release)

# Animation update function
def animate(_):
    global positions, previous_positions
    
    if not dragging:
        # Verlet integration for non-dragged points
        new_positions = 2*positions - previous_positions + np.array([0, -g]) * dt**2
        
        # Keep first point fixed if not being dragged
        if selected_point != 0:
            new_positions[0] = positions[0]
    else:
        new_positions = np.copy(positions)
    
    # Apply constraints
    for _ in range(iterations):
        for i in range(N - 1):
            p1 = new_positions[i]
            p2 = new_positions[i+1]
            dx, dy = p2 - p1
            distance = np.hypot(dx, dy)
            
            if distance == 0:
                continue
                
            if i == 0 and not dragging:  # Fixed first point when not dragging
                scale = d / distance
                new_positions[i+1] = p1 + np.array([dx, dy]) * scale
            else:
                correction = (distance - d) / (2 * distance)
                new_positions[i] += correction * np.array([dx, dy])
                new_positions[i+1] -= correction * np.array([dx, dy])
    
    # Update positions
    previous_positions = np.copy(positions)
    positions = np.copy(new_positions)
    
    # Update visualization
    line.set_data(positions[:,0], positions[:,1])
    return line,

# Start animation
ani = FuncAnimation(fig, animate, interval=dt*1000, blit=True)
plt.show()
