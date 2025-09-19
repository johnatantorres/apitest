from sqlalchemy.orm import Session, joinedload
from datetime import datetime
from app.chat import models
from fastapi import HTTPException, status
from langchain_google_genai import ChatGoogleGenerativeAI
import os
from dotenv import load_dotenv
from langchain_core.prompts import ChatPromptTemplate
from langgraph.checkpoint.memory import MemorySaver
from langgraph.prebuilt import create_react_agent

from langchain.schema import AIMessage, HumanMessage

from app.chat.schemas import Preferences
from app.chat.tools import _initialize_tools


load_dotenv()


GENAI_API_KEY = os.getenv("GENAI_API_KEY")

async def get_users_service(db: Session):
    users = db.query(models.Users).all()
    return users


async def initiate_thread_service(user_id: int, db: Session):
    user = db.query(models.Users).filter(models.Users.id == user_id).first()

    if user:
        new_thread = models.Threads(user_id=user_id)
        db.add(new_thread)
        db.commit()
        db.refresh(new_thread)
        return {"thread_id": new_thread.id}
    else:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")


async def _get_list_history_chat(thread_id, db):
    history_records = db.query(models.History).filter(
        models.History.thread_id == thread_id
    ).order_by(models.History.timestamp.desc()).limit(10).all()

    # The history is loaded for the agent, so it should be in chronological order.
    # The query gets the last 10 messages in reverse chronological order,
    # so we reverse it back.
    history_list = [
        {
            "id": record.id,
            "thread_id": record.thread_id,
            "input_message": record.input_message,
            "output_message": record.output_message,
            "timestamp": record.timestamp,
        }
        for record in reversed(history_records)
    ]
    return history_list

async def _load_chat_history(agent_executor, config: dict, thread_id: int, db):
    """Carga el historial del chat y actualiza el estado del agente."""
    chat_history = await _get_list_history_chat(thread_id, db)
    for message in chat_history:
        if message.get('input_message'):
            agent_executor.update_state(config, {"messages": [HumanMessage(content=message.get('input_message'))]})
        if message.get('output_message'):
            agent_executor.update_state(config, {"messages": [AIMessage(content=message.get('output_message'))]})

async def _save_chat_to_history(thread_id, input_message, output_message, db):
    new_history = models.History(
        thread_id=thread_id,
        input_message=input_message,
        output_message=output_message
    )
    db.add(new_history)
    db.commit()
    db.refresh(new_history)
    return new_history


async def initiate_chat_service(query: str, thread_id: int, db: Session):
    register_thread = db.query(models.Threads).filter(models.Threads.id == thread_id).first()
    user_id = register_thread.user_id
    user = db.query(models.Users).options(joinedload(models.Users.sport)).filter(models.Users.id == user_id).first()
    if user.sport:
        Preferences.favorite_sport = user.sport.name
        Preferences.sport_id = user.sport.id
    else:
        Preferences.favorite_sport = None
        Preferences.sport_id = None
    name = user.name

    llm = ChatGoogleGenerativeAI(model="gemini-2.5-flash", google_api_key=GENAI_API_KEY)
    tools = await _initialize_tools()

    base_prompt = f"""
    You are ChatBet, an AI assistant that helps users manage their bets and provides information about sports events.
    The user's name is {name}.
    The user's favorite sport is {Preferences.favorite_sport}.
    Use the tools below to get information about sports events and manage bets.
    Be proactive in offering help with betting management.
    When giving details about a bet, consider all possibilities of betting odds and suggest the best option.
    Not only focus on 1x2 odds, but also consider other odds that might be more advantageous for the user.
    The odds are:  both_teams_to_score, double_chance, over_under, handicap, half_time_total, half_time_result, etc
    If you don't know the answer to a question, you should ask the user for more information.
    Take into account today's date when providing information about sports events.
    Current date: {datetime.now().strftime('%A, %Y-%m-%d')}
    Examples of interactions:
    User: "Which team has the best odds tomorrow?"
    ChatBet: (uses tool to check_odd_by_dates)
    ChatBet: The term "best odds" can mean two different things:

    The Highest Potential Payout: The biggest number, which represents the riskiest bet but offers the largest reward.

    The Most Likely Outcome: The smallest number, which represents the safest bet with the highest probability of happening, but offers the smallest reward.
    Let's break it down based on the data we found for tomorrow:
    
    ...
    User: Give me a recommendation for Sunday
    ChatBet: (uses tool to check_odd_by_date)
    ChatBet: Based on the fixtures and odds available for Sunday, here are some recommendations based on risk levels:
    1. Conservative Option: (details of low-risk bets)
    2. Moderate Value Option: (details of medium-risk bets)
    3. Risky Option -Higher Payout: (details of high-risk bets)
    """
    
    prompt = ChatPromptTemplate.from_messages([
        ("system", base_prompt),
        ("placeholder", "{messages}"),
    ])

    memory = MemorySaver()

    agent_executor = create_react_agent(
        model=llm,
        tools=tools,
        prompt=prompt,
        checkpointer=memory
    )

    config_invocation = {"configurable": {"thread_id": f"thread_{thread_id}"}}

    await _load_chat_history(agent_executor, config_invocation, thread_id, db)

    result = agent_executor.invoke({"messages": [HumanMessage(content=query)]},
                                   config_invocation) 
    
    await _save_chat_to_history(thread_id, query, result["messages"][-1].content, db)
    
    return result["messages"][-1].content