from typing import TypedDict, Optional
import pandas as pd

class AgentState(TypedDict):
    question: str               
    schema: str                
    sql_v1: str                 
    sql_current: str            
    df_result: Optional[object] 
    error: Optional[str]        
    feedback: str             
    retries: int               
    final_answer: str           