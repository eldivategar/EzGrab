from fastapi.middleware.cors import CORSMiddleware

def add_cors_middleware(app):
    origins = [
        'http://localhost:5173',
        'https://ezgrab.eldivategar.tech',
        ]
    app.add_middleware(
        CORSMiddleware,
        allow_origins=origins,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*", "X-Requested-With", "Content-Type", "Access-Control-Allow-Origin"],
        expose_headers=["Content-Disposition"],
    )