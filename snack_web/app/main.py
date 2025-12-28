from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.core.database import engine, Base
from app.modules.users.router import router as users_router
from app.modules.snacks.router import router as snacks_router
from app.modules.sales.router import router as sales_router
from app.modules.stock.router import router as stock_router

# Create database tables
Base.metadata.create_all(bind=engine)

app = FastAPI(title="Snack POS API")

# CORS middleware - allow React to call API
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:5173",
        "http://127.0.0.1:5173",
    ],
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(users_router)
app.include_router(snacks_router)
app.include_router(sales_router)
app.include_router(stock_router)


@app.get("/")
def root():
    return {"message": "Snack POS API", "status": "running"}
