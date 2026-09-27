from fastapi import FastAPI, Request, Form
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from pathlib import Path
import os

from sqlalchemy import create_engine, String
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, sessionmaker
from pwdlib import PasswordHash
from fastapi.responses import RedirectResponse

app = FastAPI(title="Credit by Isa")
templates = Jinja2Templates(directory=".")

DATABASE_URL = os.environ.get("DATABASE_URL")

if not DATABASE_URL:
    raise RuntimeError("DATABASE_URL is not configured")

if DATABASE_URL.startswith("postgresql://"):
    DATABASE_URL = DATABASE_URL.replace(
        "postgresql://",
        "postgresql+psycopg://",
        1
    )

engine = create_engine(
    DATABASE_URL,
    pool_pre_ping=True
)

SessionLocal = sessionmaker(
    bind=engine,
    autoflush=False,
    autocommit=False
)


class Base(DeclarativeBase):
    pass


class User(Base):
    __tablename__ = "users"

    id: Mapped[int] = mapped_column(primary_key=True)
    full_name: Mapped[str] = mapped_column(String(150))
    email: Mapped[str] = mapped_column(String(255), unique=True, index=True)
    password_hash: Mapped[str] = mapped_column(String(255))


Base.metadata.create_all(bind=engine)

password_hasher = PasswordHash.recommended()
@app.get("/health")
def health():
    return {"status": "ok", "app": "Credit by Isa"}

@app.get("/", response_class=HTMLResponse)
def home(request: Request):
    return templates.TemplateResponse("index.html", {"request": request})

@app.get("/dashboard", response_class=HTMLResponse)
def dashboard(request: Request):
    return templates.TemplateResponse("dashboard.html", {
        "request": request,
        "isa_progress": 72,
        "funding_readiness": 68,
        "utilization": 31,
        "tasks_done": 6,
        "tasks_total": 9,
    })

@app.get("/disputes", response_class=HTMLResponse)
def disputes(request: Request):
    return templates.TemplateResponse("disputes.html", {"request": request})

@app.post("/disputes/preview", response_class=HTMLResponse)
def dispute_preview(
    request: Request,
    bureau: str = Form(...),
    creditor: str = Form(...),
    issue: str = Form(...),
    facts: str = Form(...)
):
    letter = f"""To: {bureau}

Re: Request for investigation of {creditor}

I am writing to dispute information appearing on my credit file regarding {creditor}.

Issue reported: {issue}

Consumer statement of facts:
{facts}

Please investigate the disputed information and provide the results of your investigation as required by applicable law.

Sincerely,
Consumer
"""
    return templates.TemplateResponse("preview.html", {
        "request": request, "letter": letter, "bureau": bureau, "creditor": creditor
    })

@app.get("/admin", response_class=HTMLResponse)
def admin(request: Request):
    return templates.TemplateResponse("admin.html", {"request": request})
@app.get("/login", response_class=HTMLResponse)
async def login_page(request: Request):
    return templates.TemplateResponse(
        "login.html",
        {"request": request}
    )

@app.get("/signup", response_class=HTMLResponse)
async def signup_page(request: Request):
    return templates.TemplateResponse(
        "signup.html",
        {"request": request}
    )
    
@app.post("/signup")
async def signup(
    full_name: str = Form(...),
    email: str = Form(...),
    password: str = Form(...)
):
    email = email.strip().lower()

    with SessionLocal() as db:
        existing_user = db.query(User).filter(User.email == email).first()

        if existing_user:
            return {"error": "An account with this email already exists."}

        new_user = User(
            full_name=full_name.strip(),
            email=email,
            password_hash=password_hasher.hash(password)
        )

        db.add(new_user)
        db.commit()
        db.refresh(new_user)

        return {
            "status": "success",
            "message": "Welcome to Credit by Isa!",
            "user_id": new_user.id
        }

@app.post("/login")
async def login(
    email: str = Form(...),
    password: str = Form(...)
):
    email = email.strip().lower()

    with SessionLocal() as db:
        user = db.query(User).filter(User.email == email).first()

        if not user:
            return {"error": "Invalid email or password."}

        if not password_hasher.verify(password, user.password_hash):
            return {"error": "Invalid email or password."}

        return RedirectResponse(
            url="/dashboard",
            status_code=303
        )

