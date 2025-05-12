from fastapi import FastAPI

from routes.notes import router as notes_router


def create_app() -> FastAPI:
    entrypoint = FastAPI(
        title="FastAPI test",
        description="A test with the FastAPI library"
    )
    entrypoint.include_router(notes_router)

    return entrypoint


app: FastAPI = create_app()
