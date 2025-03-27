import click
import subprocess

# Constants for transform boundaries
MINIMUM_TRANSFORM = 0
MAX_ALLOWED_TRANSFORM = 3


def execute_command(command):
    """Executes a command-line program and returns its output."""
    try:
        result = subprocess.run(
            command,
            shell=True,
            check=True,
            text=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
        )
        return result.stdout.strip()
    except subprocess.CalledProcessError as e:
        return f"Error executing command: {e.stderr.strip()}"


def get_transform(monitor) -> int:
    """Retrieves the current transform value for a given monitor."""
    command = f"hyprctl monitors | awk -v monitor=\"{monitor}\" '$0 ~ monitor {{found=1}} found && /transform/ {{print $2; exit}}'"
    output = execute_command(command)
    print(f"Getting the current transform for monitor {monitor}: {output}")
    return int(output)


def get_direction(monitor, direction="right") -> int:
    """Determines the next transform value based on the direction within 0–3."""
    current_transform = get_transform(monitor)

    if direction == "right":
        next_transform = current_transform + 1
        if next_transform > MAX_ALLOWED_TRANSFORM:  # Wrap around from 3 to 0
            next_transform = MINIMUM_TRANSFORM
        print(f"Monitor {monitor}: Moving right (Next transform: {next_transform})")
    elif direction == "left":
        next_transform = current_transform - 1
        if next_transform < MINIMUM_TRANSFORM:  # Wrap around from 0 to 3
            next_transform = MAX_ALLOWED_TRANSFORM
        print(f"Monitor {monitor}: Moving left (Next transform: {next_transform})")
    else:
        raise ValueError("Invalid direction! Use 'right' or 'left'.")

    return next_transform


def rotate_left(monitor):
    """Rotates the monitor to the left, restricted to transforms 0–3."""
    next_transform = get_direction(monitor, direction="left")
    command = (
        f"hyprctl keyword monitor {monitor},preferred,auto,1,transform,{next_transform}"
    )
    output = execute_command(command)
    print(f"Rotating left for monitor {monitor}: {output}")


def rotate_right(monitor):
    """Rotates the monitor to the right, restricted to transforms 0–3."""
    next_transform = get_direction(monitor, direction="right")
    command = (
        f"hyprctl keyword monitor {monitor},preferred,auto,1,transform,{next_transform}"
    )
    output = execute_command(command)
    print(f"Rotating right for monitor {monitor}: {output}")


def reset_transform(monitor):
    """Resets the monitor's transform to the minimum value (0)."""
    command = f"hyprctl keyword monitor {monitor},preferred,auto,1,transform,{MINIMUM_TRANSFORM}"
    output = execute_command(command)
    print(f"Resetting transform for monitor {monitor}: {output}")


@click.command()
@click.option("--left", is_flag=True, help="Rotate left.")
@click.option("--right", is_flag=True, help="Rotate right.")
@click.option("--reset", is_flag=True, help="Reset transform back to transform: 0.")
@click.option(
    "--monitor", type=str, default="eDP-1", help="Specify the monitor (default: eDP-1)."
)
def main(left, right, reset, monitor):
    """Main function to handle CLI options and actions."""
    # Ensure 'reset' can only be used by itself
    if reset and (left or right):
        raise click.UsageError("'--reset' cannot be used with other options.")

    if reset:
        reset_transform(monitor)
    elif left:
        rotate_left(monitor)
    elif right:
        rotate_right(monitor)
    else:
        transform = get_transform(monitor)
        print(f"Current transform for monitor {monitor}: {transform}")


if __name__ == "__main__":
    main()
