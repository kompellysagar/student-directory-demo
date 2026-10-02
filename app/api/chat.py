from fastapi import APIRouter, Depends
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.config import settings
from app.database import get_db
from app.models import Student
from app.schemas import ChatRequest, ChatResponse

router = APIRouter(prefix="/chat", tags=["AI Chatbot"])


@router.post("", response_model=ChatResponse)
def chat(payload: ChatRequest, db: Session = Depends(get_db)):
    students = db.scalars(select(Student).order_by(Student.id).limit(500)).all()
    records = "\n".join(
        f"ID {student.id}: {student.name} | {student.email} | "
        f"{student.course} | year {student.year}"
        for student in students
    )

    if not settings.gemini_api_key:
        return ChatResponse(
            answer=(
                "Gemini is not configured. There are "
                f"{len(students)} student record(s) in the database."
            ),
            mode="local",
        )

    try:
        from langchain_google_genai import ChatGoogleGenerativeAI
        from langgraph.graph import END, START, StateGraph
        from typing_extensions import TypedDict

        class State(TypedDict):
            question: str
            records: str
            answer: str

        def generate(state: State):
            model = ChatGoogleGenerativeAI(
                model=settings.gemini_model,
                google_api_key=settings.gemini_api_key,
                temperature=0,
            )
            prompt = (
                "Answer using only the student records below. If the answer is "
                "unknown, say so. Do not invent data.\n\n"
                f"{state['records'] or 'No student records.'}\n\n"
                f"Question: {state['question']}"
            )
            response = model.invoke(prompt)
            return {"answer": str(response.content)}

        graph = StateGraph(State)
        graph.add_node("generate", generate)
        graph.add_edge(START, "generate")
        graph.add_edge("generate", END)
        result = graph.compile().invoke(
            {"question": payload.message, "records": records, "answer": ""}
        )
        return ChatResponse(answer=result["answer"], mode="langgraph-gemini")
    except Exception as exc:
        return ChatResponse(
            answer=(
                f"Chatbot is unavailable ({type(exc).__name__}); database has "
                f"{len(students)} student record(s)."
            ),
            mode="local",
        )
