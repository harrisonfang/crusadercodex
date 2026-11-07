"""Sample reusable layer trajectories at actual Codex frame start times.

Displacements and heights use output-cell pixels, after source scaling. Motion
only changes the sprite's origin-aligned anchor; it never resizes source pixels.
"""

from __future__ import annotations

import math


def finite_number(value, label: str, minimum: float | None = None) -> float:
    if type(value) not in (int, float):
        raise ValueError(f"{label} must be a finite number")
    try:
        value = float(value)
    except (OverflowError, ValueError):
        raise ValueError(f"{label} must be a finite number") from None
    if not math.isfinite(value):
        raise ValueError(f"{label} must be a finite number")
    if minimum is not None and value < minimum:
        raise ValueError(f"{label} must be >= {minimum}")
    return value


def frame_start_times(delays_ms: list[int]) -> list[int]:
    """Return elapsed milliseconds at each displayed frame, excluding its hold."""
    starts, elapsed = [], 0
    for delay in delays_ms:
        if type(delay) is not int or delay <= 0:
            raise ValueError("Frame delays must be positive integer milliseconds")
        starts.append(elapsed)
        elapsed += delay
    return starts


def quantize(value: float, pixel_step: int) -> int:
    # Symmetric half-away-from-zero rounding avoids directional tie bias.
    magnitude = math.floor(abs(value) / pixel_step + 0.5) * pixel_step
    return -magnitude if value < 0 else magnitude


def _exponential_terms(q: float, u: float, rate: float, seconds: float) -> tuple[float, float, float]:
    """Return normalized progress and its first two time derivatives.

    The numerator and denominator both vanish quadratically as q -> 0.
    Factoring out q**2 and summing their Taylor series avoids cancellation and
    underflow. Thirteen terms have ample float precision throughout q <= 0.1.
    """
    if q == 0:
        return u * (2 - u), 2 * (1 - u) / seconds, -2 / seconds / seconds
    if q <= 0.1:
        denominator = math.fsum((-q) ** n * (n + 1) / math.factorial(n + 2) for n in range(13))
        numerator = math.fsum((-q) ** n * (u / math.factorial(n + 1) - u ** (n + 2) / math.factorial(n + 2))
                              for n in range(13))
        # Factoring 1-u also avoids subtracting nearly equal powers at the end.
        speed = (1 - u) * math.fsum((-q) ** n * math.fsum(u ** j for j in range(n + 1)) / math.factorial(n + 1)
                                   for n in range(13))
        return (numerator / denominator, speed / denominator / seconds,
                -math.exp(-q * u) / denominator / seconds / seconds)
    tail = math.exp(-q)
    decay = math.exp(-q * u)
    denominator = -math.expm1(-q) - q * tail
    progress = (-math.expm1(-q * u) - q * u * tail) / denominator
    # Using rate directly avoids squaring q or duration, which can overflow
    # even when the physical derivatives remain representable.
    speed = rate * decay * -math.expm1(-q * (1 - u)) / denominator
    acceleration = -(rate * decay) * rate / denominator
    return progress, speed, acceleration


def motion_state(motion: dict, sample_ms: float, label: str = "motion") -> dict[str, list[float]]:
    """Evaluate an unrounded trajectory in pixels, pixels/s, and pixels/s².

    Return offset_px, velocity_px_s, and acceleration_px_s2, each as [x, y].
    Before start and at/after finish, position is held and both derivatives are
    zero. At start, derivatives describe the outgoing motion. Screen y is down.

    Decelerate defaults to exponent 2. Exponential-stop uses decay_rate_per_s
    and reaches zero speed at duration_ms; rate 0 is the quadratic limit.
    """
    kinds = ("ballistic", "decelerate", "exponential-stop")
    if not isinstance(motion, dict) or motion.get("type") not in kinds:
        raise ValueError(f"{label}.type must be ballistic, decelerate, or exponential-stop")
    start = finite_number(motion.get("start_ms", 0), f"{label}.start_ms", 0)
    duration = finite_number(motion.get("duration_ms"), f"{label}.duration_ms", 0)
    if duration == 0:
        raise ValueError(f"{label}.duration_ms must be > 0")
    seconds = duration / 1000
    if seconds == 0:
        raise ValueError(f"{label}.duration_ms is too small to represent in seconds")
    displacement = motion.get("displacement")
    if not isinstance(displacement, (tuple, list)) or len(displacement) != 2:
        raise ValueError(f"{label}.displacement must contain two coordinates")
    dx, dy = [finite_number(value, f"{label}.displacement") for value in displacement]
    step = motion.get("pixel_step", 1)
    if type(step) is not int or step < 1:
        raise ValueError(f"{label}.pixel_step must be a positive integer")
    elapsed = finite_number(sample_ms, f"{label} sample time")
    u = min(1.0, max(0.0, (elapsed - start) / duration))
    active = elapsed >= start and u < 1
    vx = vy = ax = ay = 0.0
    if motion["type"] == "ballistic":
        height = finite_number(motion.get("height_px"), f"{label}.height_px", 0)
        x, y = dx * u, dy * u - 4 * height * u * (1 - u)
        if active:
            vx, vy = dx / seconds, (dy - 4 * height + 8 * height * u) / seconds
            ay = 8 * height / seconds / seconds
    elif motion["type"] == "decelerate":
        exponent = finite_number(motion.get("exponent", 2), f"{label}.exponent")
        if exponent <= 1:
            raise ValueError(f"{label}.exponent must be > 1")
        # Preserve legacy floating-point arithmetic, including pixel rounding
        # boundaries, for both the omitted exponent and an explicit value of 2.
        progress = u * (2 - u) if exponent == 2 else 1 - (1 - u) ** exponent
        x, y = dx * progress, dy * progress
        if active:
            speed = exponent * (1 - u) ** (exponent - 1) / seconds
            acceleration = -exponent * (exponent - 1) * (1 - u) ** (exponent - 2) / seconds / seconds
            vx, vy = dx * speed, dy * speed
            ax, ay = dx * acceleration, dy * acceleration
    else:
        rate = finite_number(motion.get("decay_rate_per_s"), f"{label}.decay_rate_per_s", 0)
        q = finite_number(rate * seconds, f"{label} rate × duration")
        if active:
            progress, speed, acceleration = _exponential_terms(q, u, rate, seconds)
            vx, vy = dx * speed, dy * speed
            ax, ay = dx * acceleration, dy * acceleration
        else:
            progress = u
        x, y = dx * progress, dy * progress
    state = {"offset_px": [x, y], "velocity_px_s": [vx, vy], "acceleration_px_s2": [ax, ay]}
    if not all(math.isfinite(value) for vector in state.values() for value in vector):
        raise ValueError(f"{label} produces unrepresentable motion values")
    return state


def sample_motion(motion: dict, sample_ms: float, label: str = "motion") -> list[int]:
    """Round an analytical motion offset to the requested output pixel grid."""
    state = motion_state(motion, sample_ms, label)
    return [quantize(value, motion.get("pixel_step", 1)) for value in state["offset_px"]]


def motion_offsets(motion: dict, delays_ms: list[int], label: str = "motion") -> list[list[int]]:
    return [sample_motion(motion, elapsed, label) for elapsed in frame_start_times(delays_ms)]
