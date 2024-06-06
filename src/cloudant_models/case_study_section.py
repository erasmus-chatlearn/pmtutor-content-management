class CaseStudySection:
    def __init__(self,
                 _id,
                 parent_id,
                 spread_sheet_ref_id,
                 name,
                 description,
                 objectives,
                 has_exercises,
                 content_elements):
        self.docType = "caseStudySection"
        self._id = _id
        self.parentId = parent_id
        self.spreadSheetRefId = spread_sheet_ref_id
        self.name = name
        self.description = description
        self.objectives = objectives
        self.hasExercises = has_exercises
        self.contentElements = content_elements
