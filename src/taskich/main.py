from taskich.cli import run_cli
from taskich.data import create_demo_tasks
from taskich.storage import InMemoryFilterRepository


def main() -> None:
    """Запускает консольное приложение Taskich."""

    run_cli(
        create_demo_tasks(),
        InMemoryFilterRepository(),
    )


if __name__ == "__main__":
    main()
