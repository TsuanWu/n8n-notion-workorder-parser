import csv
import io
from pathlib import Path
from tempfile import NamedTemporaryFile

from fastapi import FastAPI, HTTPException, Request
from markitdown import MarkItDown

app = FastAPI(title="Jetsea PDF extractor")
converter = MarkItDown()
PERSONNEL_MAP_PATH = Path("/app/personnel-map.csv")


@app.get("/health")
def health():
    return {"ok": True}


@app.post("/map-personnel")
async def map_personnel(request: Request):
    """Map names extracted from a dispatch form to the personnel CSV."""
    body = await request.json()
    names = body.get("people_names")
    if not isinstance(names, list):
        raise HTTPException(status_code=400, detail="people_names must be an array")
    if not PERSONNEL_MAP_PATH.exists():
        raise HTTPException(status_code=500, detail="personnel-map.csv is not mounted")

    raw_csv = PERSONNEL_MAP_PATH.read_bytes()
    try:
        csv_text = raw_csv.decode("utf-8-sig")
    except UnicodeDecodeError:
        # Excel on Traditional Chinese Windows commonly exports CSV as CP950.
        csv_text = raw_csv.decode("cp950")

    index: dict[str, dict[str, str]] = {}
    for row in csv.DictReader(io.StringIO(csv_text)):
            if row.get("active", "").strip().lower() in {"false", "0", "no"}:
                continue
            email = (row.get("aliases") or "").strip()
            if not email:
                continue
            entry = {
                "name": (row.get("Name") or "").strip(),
                "canonical_name": (row.get("canonical_name") or "").strip(),
                "email": email,
                "notion_user_id": (
                    row.get("notion_user_id")
                    or row.get("Notion user ID")
                    or ""
                ).strip(),
            }
            for key in (entry["name"], entry["canonical_name"]):
                if key:
                    index[key] = entry

    matched = []
    unmatched = []
    seen_emails = set()
    for raw_name in names:
        name = str(raw_name).strip()
        entry = index.get(name)
        if not entry:
            unmatched.append(name)
            continue
        if entry["email"] not in seen_emails:
            matched.append(entry)
            seen_emails.add(entry["email"])

    return {
        "matched": matched,
        "emails": [entry["email"] for entry in matched],
        "unmatched": unmatched,
        "all_matched": not unmatched,
    }


@app.post("/convert")
async def convert(request: Request):
    pdf = await request.body()
    if not pdf:
        raise HTTPException(status_code=400, detail="Empty PDF body")
    if len(pdf) > 25 * 1024 * 1024:
        raise HTTPException(status_code=413, detail="PDF is larger than 25 MB")

    temp_path = None
    try:
        with NamedTemporaryFile(suffix=".pdf", delete=False) as temp_file:
            temp_file.write(pdf)
            temp_path = Path(temp_file.name)
        result = converter.convert(str(temp_path))
        return {"text": result.text_content, "method": "markitdown"}
    except Exception as exc:
        raise HTTPException(status_code=422, detail=f"Unable to extract PDF: {exc}") from exc
    finally:
        if temp_path:
            temp_path.unlink(missing_ok=True)
