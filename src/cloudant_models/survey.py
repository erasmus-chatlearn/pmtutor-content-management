from typing import List
from .survey_section import SurveySection


class Survey:
    def __init__(self,
                 doc_id,
                 org_id,
                 survey_type,
                 name,
                 description,
                 sections: List[SurveySection],
                 created_at,
                 updated_at):
        self._id = doc_id
        self.orgId = org_id
        self.docType = 'survey'
        self.surveyType = survey_type
        self.name = name
        self.description = description
        self.sections = sections
        self.createdAt = created_at
        self.updatedAt = updated_at
        self.isActive = True
