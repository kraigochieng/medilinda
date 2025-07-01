import random
from uuid import uuid4

import pandas as pd
from engines import engine

from models import (
    CausalityAssessmentLevelEnum,
    CausalityAssessmentLevelModel,
    UserModel,
)
from sqlalchemy.orm import Session

# Create user
session = Session(bind=engine)

# Get users and causality assessment levels
users = session.query(UserModel).all()
user_ids = [user.id for user in users]

causality_entries = session.query(CausalityAssessmentLevelModel).limit(20).all()

data = []

# For every causality assessment level
for entry in causality_entries:
    # To keep unique the user for every causality assessment level
    reviewed_users = set()
    # For every review for every causality assessent level
    for _ in range(20):
        # Choose a user id and check if it is already used
        user_id = random.choice(user_ids)
        while user_id in reviewed_users:
            user_id = random.choice(user_ids)
        reviewed_users.add(user_id)

        # Add other properties
        approved = random.choice([True, False])

        proposed_level = (
            random.choice(list(CausalityAssessmentLevelEnum)) if not approved else None
        )

        reason = (
            random.choice(
                [
                    "Sufficient evidence provided.",
                    "Missing key symptom analysis.",
                    "Reviewed and agreed.",
                    "Contradicts known patterns.",
                    "Needs expert second opinion.",
                    "",
                ]
            )
            if not approved
            else None
        )

        data.append(
            {
                "id": str(uuid4()),
                "causality_assessment_level_id": entry.id,
                "user_id": user_id,
                "approved": approved,
                "proposed_causality_level": proposed_level.name
                if proposed_level
                else None,  # to get value within enum
                "reason": reason,
            }
        )

reviews_df = pd.DataFrame(data)
reviews_df.to_csv("reviews.csv", index=False)
print("reviews.csv created with", len(data), "rows.")
