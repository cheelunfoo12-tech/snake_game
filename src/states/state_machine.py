"""State pattern implementation for deterministic game state transitions."""

from abc import ABC, abstractmethod
import pygame

from src.renderer import NeonRenderer


class BaseState(ABC):
    """Abstract base class for all game states."""

    def __init__(self, state_machine: "StateMachine") -> None:
        self.state_machine: "StateMachine" = state_machine

    def enter(self, params: dict | None = None) -> None:
        """Called upon entering this state."""
        pass

    def exit(self) -> None:
        """Called upon exiting this state."""
        pass

    @abstractmethod
    def handle_event(self, event: pygame.event.Event) -> None:
        """Processes a single Pygame event."""
        pass

    @abstractmethod
    def update(self, dt: float) -> None:
        """Updates internal state logic with delta time in seconds."""
        pass

    @abstractmethod
    def draw(self, renderer: NeonRenderer) -> None:
        """Renders state elements onto the screen."""
        pass


class StateMachine:
    """Manages active state transitions and forwards loop calls."""

    def __init__(self) -> None:
        self.states: dict[str, BaseState] = {}
        self.current_state_name: str | None = None
        self.current_state: BaseState | None = None

    def add_state(self, name: str, state: BaseState) -> None:
        """Registers a named state."""
        self.states[name] = state

    def change_state(self, name: str, params: dict | None = None) -> None:
        """Transitions from current state to the specified state."""
        if self.current_state:
            self.current_state.exit()

        if name not in self.states:
            raise ValueError(f"State '{name}' has not been registered.")

        self.current_state_name = name
        self.current_state = self.states[name]
        self.current_state.enter(params)

    def handle_event(self, event: pygame.event.Event) -> None:
        """Forwards event to active state."""
        if self.current_state:
            self.current_state.handle_event(event)

    def update(self, dt: float) -> None:
        """Forwards update step to active state."""
        if self.current_state:
            self.current_state.update(dt)

    def draw(self, renderer: NeonRenderer) -> None:
        """Forwards draw step to active state."""
        if self.current_state:
            self.current_state.draw(renderer)
