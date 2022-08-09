import logging
from io import BytesIO

import uvicorn
from fastapi import FastAPI, Query
from starlette.responses import Response, HTMLResponse
from starlette.middleware.cors import CORSMiddleware
from sqlitedict import SqliteDict
from pybadges import badge
from reportlab.graphics import renderPM
from svglib.svglib import svg2rlg

from entity import Problem

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

db = SqliteDict("data/db.sqlite", autocommit=True)


@app.on_event("startup")
async def startup_event():
    logging.getLogger('svglib').setLevel(logging.ERROR)


@app.get("/")
async def github():
    return Response(status_code=302, headers={"Location": "https://github.com/masterUtils/problemManager"})


@app.get("/fail/{problem_id}")
async def fail(problem_id: str):
    if problem_id not in db:
        return HTMLResponse(f"<h1>{problem_id} not found</h1>", status_code=404)
    problem = db[problem_id]
    problem.fail += 1
    db[problem_id] = problem
    return problem


@app.get("/success/{problem_id}")
async def success(problem_id: str):
    if problem_id not in db:
        return HTMLResponse(f"<h1>{problem_id} not found</h1>", status_code=404)
    problem = db[problem_id]
    problem.success += 1
    db[problem_id] = problem
    return problem


@app.get("/reset/{problem_id}")
async def reset(problem_id: str):
    if problem_id not in db:
        return HTMLResponse(f"<h1>{problem_id} not found</h1>", status_code=404)
    problem = db[problem_id]
    problem.success = 0
    problem.fail = 0
    db[problem_id] = problem
    return problem


@app.get("/stats/_/{section_id}.json")
async def stats_all(section_id: str):
    keys = db.keys()
    keys = [k for k in keys if k.startswith(section_id)]
    ret = {}
    for k in keys:
        ret[k] = db[k]
    return ret


@app.get("/stats/{problem_id}.json")
async def stats_json(problem_id: str):
    if problem_id not in db:
        return HTMLResponse(f"<h1>{problem_id} not found</h1>", status_code=404)
    return db[problem_id]


@app.get("/stats/{problem_id}.txt")
async def stats_txt(problem_id: str):
    if problem_id not in db:
        return HTMLResponse(f"<h1>{problem_id} not found</h1>", status_code=404)
    problem = db[problem_id]

    return Response(f"{problem.success} / {problem.success + problem.fail}", media_type="text/plain")


@app.get("/stats/{problem_id}.png")
async def stats_png(problem_id: str):
    if problem_id not in db:
        return HTMLResponse(f"<h1>{problem_id} not found</h1>", status_code=404)
    problem = db[problem_id]

    color = 'red'
    if problem.success > 0:
        color = 'green'
    b = badge(left_text=problem.name, right_text=f"{problem.success} - {problem.fail}", right_color=color)

    svg_file = BytesIO(b.encode())
    png_file = BytesIO()
    drawing = svg2rlg(svg_file)

    renderPM.drawToFile(drawing, png_file, fmt="PNG")
    img = png_file.getvalue()
    del png_file
    return Response(img, media_type="image/png")


@app.post("/create/{problem_id}")
async def create(problem_id: str, name: str = Query(default="Problem"), onenote_url: str = Query(...)):
    if problem_id not in db:
        db[problem_id] = Problem(0, 0, onenote_url, name)
    else:
        problem = db[problem_id]
        if name != "Problem":
            problem.name = name
        problem.onenote_url = onenote_url
        db[problem_id] = problem
    return {"message": "ok"}


if __name__ == '__main__':
    uvicorn.run(app, host='0.0.0.0', port=8000)
