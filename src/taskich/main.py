"""Единая точка запуска веб-приложения Taskich."""
import uvicorn


def main() -> None:
    uvicorn.run("taskich.web:app", host="127.0.0.1", port=8000, reload=False)


if __name__ == "__main__":
    main()
