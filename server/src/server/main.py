import logging

from fastapi import FastAPI, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi_pagination import add_pagination

from server.api.v1.endpoints import (
    adverse_drug_reaction_reports as adverse_drug_reaction_report_v1,
)
from server.api.v1.endpoints import (
    adverse_drug_reaction_reports_details as adverse_drug_reaction_report_details_v1,
)
from server.api.v1.endpoints import auth as auth_v1
from server.api.v1.endpoints import (
    causality_assessment_levels as causality_assessment_level_v1,
)
from server.api.v1.endpoints import (
    causality_assessment_levels_actions as causality_assessment_levels_actions_v1,
)
from server.api.v1.endpoints import (
    causality_assessment_levels_details as causality_assessment_levels_details_v1,
)
from server.api.v1.endpoints import dashboard as dashboard_v1
from server.api.v1.endpoints import medical_institution as medical_institution_v1
from server.api.v1.endpoints import reviews as reviews_v1
from server.api.v1.endpoints import reviews_details as reviews_details_v1
from server.api.v1.endpoints import sms as sms_v1
from server.api.v1.endpoints import sms_actions as sms_actions_v1
from server.api.v1.endpoints import sms_details as sms_details_v1
from server.api.v1.endpoints import telephones as telephones_v1
from server.api.v1.endpoints import users as users_v1
from server.lifespan.lifespan import lifespan
from server.settings import settings

logging.basicConfig(level=logging.INFO)
logging.getLogger("shap").setLevel(logging.WARNING)

app = FastAPI(lifespan=lifespan)

app.add_middleware(
    CORSMiddleware,
    allow_origins=[settings.nuxt_public_api_base],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

add_pagination(app)

app.include_router(auth_v1.router)
app.include_router(adverse_drug_reaction_report_v1.router)
app.include_router(adverse_drug_reaction_report_details_v1.router)
app.include_router(causality_assessment_level_v1.router)
app.include_router(causality_assessment_levels_actions_v1.router)
app.include_router(causality_assessment_levels_details_v1.router)
app.include_router(dashboard_v1.router)
app.include_router(medical_institution_v1.router)
app.include_router(reviews_v1.router)
app.include_router(reviews_details_v1.router)
app.include_router(sms_v1.router)
app.include_router(sms_actions_v1.router)
app.include_router(sms_details_v1.router)
app.include_router(telephones_v1.router)
app.include_router(users_v1.router)


@app.get("/", status_code=status.HTTP_200_OK)
async def root():
    return "Medilinda Running!"
