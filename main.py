from fastapi import FastAPI, Request, Form
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from pathlib import Path

app = FastAPI(title="Credit by Isa")
templates = Jinja2Templates(directory=".")

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
