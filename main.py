import logging
from io import BytesIO

import uvicorn
from fastapi import FastAPI
from starlette.responses import Response, HTMLResponse
from starlette.middleware.cors import CORSMiddleware
from sqlitedict import SqliteDict
from pybadges import badge
from reportlab.graphics import renderPDF, renderPM
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

db = SqliteDict("db.sqlite", autocommit=True)


@app.get("/")
async def github():
    return Response(status_code=302, headers={"Location": "https://github.com/masterUtils/problemManager"})


@app.get("/fail/{problem_id}")
async def fail(problem_id: str):
    if problem_id not in db:
        db[problem_id] = Problem(0, 0)
    problem = db[problem_id]
    problem.fail += 1
    db[problem_id] = problem
    return HTMLResponse(f"<h1>{problem_id}</h1>")


@app.get("/success/{problem_id}")
async def success(problem_id: str):
    if problem_id not in db:
        db[problem_id] = Problem(0, 0)
    problem = db[problem_id]
    problem.success += 1
    db[problem_id] = problem
    return HTMLResponse(f"<h1>{problem_id}</h1>")


@app.get("/stats/{problem_id}")
async def stats(problem_id: str):
    if problem_id not in db:
        db[problem_id] = Problem(0, 0)
    problem = db[problem_id]

    color = 'red'
    if problem.success > 0:
        color = 'green'
    b = badge(left_text="Problem", right_text=f"{problem.success} - {problem.fail}", right_color=color)

    svg_file = BytesIO(b.encode())
    png_file = BytesIO()
    drawing = svg2rlg(svg_file)

    scale = 5
    drawing.scale(scale, scale)
    drawing.width *= scale
    drawing.height *= scale

    renderPM.drawToFile(drawing, png_file, fmt="PNG")
    img = png_file.getvalue()
    return Response(img, media_type="image/png")


if __name__ == '__main__':
    logger = logging.getLogger('svglib')
    logger.setLevel(logging.ERROR)
    uvicorn.run(app, host='0.0.0.0', port=8000, debug=True)
