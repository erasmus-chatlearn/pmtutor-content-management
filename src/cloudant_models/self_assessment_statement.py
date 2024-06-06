class SelfAssessmentStatement:
    def __init__(self, doc_id, statement, scope, scope_ref_id, scope_name, created_at, updated_at, is_active):
        self._id = doc_id
        self.docType = 'selfAssessmentStatement'
        self.description = statement
        self.scope = scope
        self.scopeRefId = scope_ref_id
        self.scopeName = scope_name
        self.createdAt = created_at
        self.updatedAt = updated_at
        self.isActive = is_active
