class CaseStudyConfig:
    def __init__(
            self,
            _id,
            organization_name,
            org_id,
            spread_sheet_ref_id,
            name,
            description,
            objectives,
            tags):
        self.docType = 'caseStudyConfig'
        self._id = _id
        self.organizationName = organization_name
        self.orgId = org_id
        self.spreadSheetRefId = spread_sheet_ref_id
        self.name = name
        self.description = description
        self.objectives = objectives
        self.tags = tags

