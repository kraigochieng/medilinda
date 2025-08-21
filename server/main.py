import logging

from fastapi import FastAPI, status
from fastapi_pagination import add_pagination

from server.api.v1.endpoints import (
    adverse_drug_reaction_reports as adverse_drug_reaction_report_v1,
)
from server.api.v1.endpoints import auth as auth_v1
from server.api.v1.endpoints import (
    causality_assessment_levels as causality_assessment_level_v1,
)
from server.api.v1.endpoints import dashboard as dashboard_v1
from server.api.v1.endpoints import medical_institution as medical_institution_v1
from server.api.v1.endpoints import reviews as reviews_v1
from server.api.v1.endpoints import sms as sms_v1
from server.api.v1.endpoints import users as users_v1
from server.lifespan import lifespan

logging.basicConfig(level=logging.INFO)
logging.getLogger("shap").setLevel(logging.WARNING)

app = FastAPI(lifespan=lifespan)

add_pagination(app)

app.include_router(auth_v1.router)
app.include_router(adverse_drug_reaction_report_v1.router)
app.include_router(causality_assessment_level_v1.router)
app.include_router(dashboard_v1.router)
app.include_router(medical_institution_v1.router)
app.include_router(reviews_v1.router)
app.include_router(sms_v1.router)
app.include_router(users_v1.router)


@app.get("/", status_code=status.HTTP_200_OK)
async def root():
    return "Medilinda Running!"
