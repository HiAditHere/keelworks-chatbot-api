from fastapi import FastAPI, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from . import database, chatbot, schemas, crud

app = FastAPI()

# Endpoint for the initial startup message
@app.get('/')
async def home():
    return {'message': 'Welcome to the KeelWorks Chatbot. Ask me anything about KeelWorks!'}

# Endpoint for user inputted question and, based on the threshold match, either returns a response using chatbot model or saves the question in a database
@app.post('/ask')
async def ask_question(query: schemas.Query, db: AsyncSession = Depends(database.get_session)):
    user_query = query.query
    answer, is_above_threshold = chatbot.get_best_answer(user_query)

    if is_above_threshold:
        response = schemas.UnansweredQuestion(question=user_query, answer=answer, id=None, created_at=None)
    else:
        created_question = await crud.create_unanswered_question(db, question=schemas.UnansweredQuestionCreate(question=user_query))
        response = schemas.UnansweredQuestion.model_validate(created_question)
    
    return response
    
# To start the server:
# uvicorn app.main:app --host 0.0.0.0 --port 80

# Before running server:
# 1. Make sure there is a chatbot_model pickle file in model/: 'python -m scripts.save_model'