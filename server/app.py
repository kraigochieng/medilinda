import calendar
import datetime
import json
import logging
import math
import os
import random
import shutil
from collections import defaultdict
from contextlib import asynccontextmanager
from typing import List, Tuple
from uuid import uuid4

import africastalking
import boto3
import joblib
import jwt
import mlflow
import numpy as np
import pandas as pd
import shap
from auth import (
    create_access_token,
    create_refresh_token,
    get_current_user,
    get_password_hash,
    verify_password,
)
from basemodels import (
    ActionTakenEnum,
    AdditionalInfoPostRequest,
    ADRGetResponse,
    ADRModel,
    ADRPostRequest,
    ADRReviewCreateRequest,
    ADRReviewGetResponse,
    Base,
    CausalityAssessmentLevelEnum,
    CausalityAssessmentLevelGetResponse,
    CausalityAssessmentLevelModel,
    CriteriaForSeriousnessEnum,
    DechallengeEnum,
    GenderEnum,
    IndividualAlertPostRequest,
    IsSeriousEnum,
    KnownAllergyEnum,
    MedicalInstitutionGetResponse,
    MedicalInstitutionModel,
    MedicalInstitutionPostRequest,
    MedicalInstitutionTelephoneGetResponse,
    MedicalInstitutionTelephoneModel,
    MedicalInstitutionTelephonePostRequest,
    MultipleMedicalInstitutionTelephonePostRequest,
    OutcomeEnum,
    PregnancyStatusEnum,
    RechallengeEnum,
    ReviewGetResponse,
    ReviewModel,
    SeverityEnum,
    SMSMessageGetResponse,
    SMSMessageModel,
    SMSMessageTypeEnum,
    Token,
    UnclassifiablePostRequest,
    UserDetailsBaseModel,
    UserGetResponse,
    UserModel,
    UserSignupBaseModel,
)
from config import settings
from dependencies import get_db
from engines import engine
from fastapi import Depends, FastAPI, HTTPException, Path, Query, status
from fastapi.encoders import jsonable_encoder
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse, Response
from fastapi.security import OAuth2PasswordRequestForm
from fastapi_pagination import Page, add_pagination
from fastapi_pagination.ext.sqlalchemy import paginate
from mlflow.tracking import MlflowClient
from shap import Explainer, Explanation, KernelExplainer
from sklearn.base import BaseEstimator
from sklearn.preprocessing import OneHotEncoder, OrdinalEncoder
from sqlalchemy import case, desc, func, text
from sqlalchemy.engine import Row
from sqlalchemy.orm import Session, joinedload, load_only
from typing_extensions import Annotated, Dict
