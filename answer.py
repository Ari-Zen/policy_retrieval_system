# Module
from clause import build_clause_prompt, PolicyClause
from pydantic import BaseModel
from policy_data_model import PolicyChunk

# Generation Contract

# Input to generate
class GenerationRequest(BaseModel):
    query: str
    policies: list[PolicyChunk]

# Output to generate
class GenerateAnswer(BaseModel):
    answer: str
    citations: list[str]


# System Prompt
SYSTEM_PROMPT = ''' 
You are a compliance assistant.

Answer the user question using ONLY the provided policy excerpts.
Do NOt add information not explicitly stated.
If the policies do not clearly answer the question, say so.

Every factual statement MUST be supported by a citation.
Citation must refrence policy_id.
'''

# Answer
def generate_answer(
        query: str,
        clauses: list[PolicyClause],
        llm
) -> GenerateAnswer:
    prompt = build_clause_prompt(query, clauses)

    response = llm.invoke(
        system_prompt=SYSTEM_PROMPT,
        user_prompt=prompt
    )

    return GenerateAnswer(
        answer=response.text,
        citations=list({
            c.policy_id for c in clauses
        })
    )