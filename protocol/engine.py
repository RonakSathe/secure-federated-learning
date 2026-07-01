class ProtocolEngine:
    def __init__(self):
        self.stages = []
    
    def add_stage(self,stage):
        self.stages.append(stage)
    
    def execute(self,session):
        for stage in self.stages:
            print(f"\n Executing {stage.__class__.__name__} for session {session.session_id}")
            stage.run(session)