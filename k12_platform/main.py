"""K12智慧教育平台 - 主应用"""
import os
import json
import base64
from datetime import datetime
from fastapi import FastAPI, Request, Depends, HTTPException, Form, UploadFile, File
from fastapi.responses import HTMLResponse, RedirectResponse, JSONResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from sqlalchemy.orm import Session
from sqlalchemy import func

from models.database import init_db, get_db, User, Question, Answer, Essay, WrongQuestion, ChatSession, ChatMessage
from services.auth_service import hash_password, verify_password, create_access_token, get_current_user, require_auth
from services.llm_service import llm_service

app = FastAPI(title="K12智慧教育平台")

# 静态文件和模板
app.mount("/static", StaticFiles(directory="static"), name="static")
templates = Jinja2Templates(directory="templates")

# 初始化数据库
init_db()


# ==================== 页面路由 ====================

@app.get("/", response_class=HTMLResponse)
async def home(request: Request, user=Depends(get_current_user)):
    """首页"""
    if not user:
        return RedirectResponse(url="/login", status_code=302)
    return templates.TemplateResponse("index.html", {"request": request, "user": user})


@app.get("/login", response_class=HTMLResponse)
async def login_page(request: Request):
    """登录页面"""
    return templates.TemplateResponse("login.html", {"request": request})


@app.get("/register", response_class=HTMLResponse)
async def register_page(request: Request):
    """注册页面"""
    return templates.TemplateResponse("register.html", {"request": request})


@app.get("/question", response_class=HTMLResponse)
async def question_page(request: Request, user=Depends(require_auth)):
    """提问页面"""
    return templates.TemplateResponse("question.html", {"request": request, "user": user})


@app.get("/essay", response_class=HTMLResponse)
async def essay_page(request: Request, user=Depends(require_auth)):
    """作文批改页面"""
    return templates.TemplateResponse("essay.html", {"request": request, "user": user})


@app.get("/chat", response_class=HTMLResponse)
async def chat_page(request: Request, user=Depends(require_auth)):
    """聊天助手页面"""
    return templates.TemplateResponse("chat.html", {"request": request, "user": user})


@app.get("/wrong-book", response_class=HTMLResponse)
async def wrong_book_page(request: Request, user=Depends(require_auth)):
    """错题本页面"""
    return templates.TemplateResponse("wrong_book.html", {"request": request, "user": user})


@app.get("/practice", response_class=HTMLResponse)
async def practice_page(request: Request, user=Depends(require_auth)):
    """错题练习页面"""
    return templates.TemplateResponse("practice.html", {"request": request, "user": user})


@app.get("/statistics", response_class=HTMLResponse)
async def statistics_page(request: Request, user=Depends(require_auth)):
    """学习统计页面"""
    return templates.TemplateResponse("statistics.html", {"request": request, "user": user})


@app.get("/profile", response_class=HTMLResponse)
async def profile_page(request: Request, user=Depends(require_auth)):
    """个人信息页面"""
    return templates.TemplateResponse("profile.html", {"request": request, "user": user})


# ==================== 英文版页面路由 ====================

@app.get("/en", response_class=HTMLResponse)
async def home_en(request: Request, user=Depends(get_current_user)):
    """首页 - 英文"""
    if not user:
        return RedirectResponse(url="/login-en", status_code=302)
    return templates.TemplateResponse("index-en.html", {"request": request, "user": user})


@app.get("/login-en", response_class=HTMLResponse)
async def login_page_en(request: Request):
    """登录页面 - 英文"""
    return templates.TemplateResponse("login-en.html", {"request": request})


@app.get("/register-en", response_class=HTMLResponse)
async def register_page_en(request: Request):
    """注册页面 - 英文"""
    return templates.TemplateResponse("register-en.html", {"request": request})


@app.get("/question-en", response_class=HTMLResponse)
async def question_page_en(request: Request, user=Depends(require_auth)):
    """提问页面 - 英文"""
    return templates.TemplateResponse("question-en.html", {"request": request, "user": user})


@app.get("/essay-en", response_class=HTMLResponse)
async def essay_page_en(request: Request, user=Depends(require_auth)):
    """作文批改页面 - 英文"""
    return templates.TemplateResponse("essay-en.html", {"request": request, "user": user})


@app.get("/chat-en", response_class=HTMLResponse)
async def chat_page_en(request: Request, user=Depends(require_auth)):
    """聊天助手页面 - 英文"""
    return templates.TemplateResponse("chat-en.html", {"request": request, "user": user})


@app.get("/wrong-book-en", response_class=HTMLResponse)
async def wrong_book_page_en(request: Request, user=Depends(require_auth)):
    """错题本页面 - 英文"""
    return templates.TemplateResponse("wrong_book-en.html", {"request": request, "user": user})


@app.get("/practice-en", response_class=HTMLResponse)
async def practice_page_en(request: Request, user=Depends(require_auth)):
    """错题练习页面 - 英文"""
    return templates.TemplateResponse("practice-en.html", {"request": request, "user": user})


@app.get("/statistics-en", response_class=HTMLResponse)
async def statistics_page_en(request: Request, user=Depends(require_auth)):
    """学习统计页面 - 英文"""
    return templates.TemplateResponse("statistics-en.html", {"request": request, "user": user})


@app.get("/profile-en", response_class=HTMLResponse)
async def profile_page_en(request: Request, user=Depends(require_auth)):
    """个人信息页面 - 英文"""
    return templates.TemplateResponse("profile-en.html", {"request": request, "user": user})


# ==================== API路由 ====================

@app.post("/api/register")
async def register(
    username: str = Form(...),
    password: str = Form(...),
    email: str = Form(""),
    grade: str = Form(""),
    subjects: str = Form(""),
    db: Session = Depends(get_db)
):
    """用户注册"""
    # 检查用户名是否存在
    existing = db.query(User).filter(User.username == username).first()
    if existing:
        raise HTTPException(status_code=400, detail="用户名已存在")
    
    # 创建用户
    user = User(
        username=username,
        password_hash=hash_password(password),
        email=email,
        grade=grade,
        subjects=subjects
    )
    db.add(user)
    db.commit()
    db.refresh(user)
    
    # 创建token
    token = create_access_token({"sub": str(user.id), "username": user.username})
    
    response = JSONResponse({"message": "注册成功", "user_id": user.id})
    response.set_cookie(key="access_token", value=token, httponly=True, max_age=60*60*24*7)
    return response


@app.post("/api/login")
async def login(
    username: str = Form(...),
    password: str = Form(...),
    db: Session = Depends(get_db)
):
    """用户登录"""
    user = db.query(User).filter(User.username == username).first()
    if not user or not verify_password(password, user.password_hash):
        raise HTTPException(status_code=400, detail="用户名或密码错误")
    
    # 更新最后登录时间
    user.last_login = datetime.now()
    db.commit()
    
    # 创建token
    token = create_access_token({"sub": str(user.id), "username": user.username})
    
    response = JSONResponse({"message": "登录成功"})
    response.set_cookie(key="access_token", value=token, httponly=True, max_age=60*60*24*7)
    return response


@app.post("/api/logout")
async def logout():
    """退出登录"""
    response = JSONResponse({"message": "已退出"})
    response.delete_cookie("access_token")
    return response


@app.post("/api/question")
async def submit_question(
    request: Request,
    content: str = Form(""),
    subject: str = Form("数学"),
    image: UploadFile = File(None),
    user=Depends(require_auth),
    db: Session = Depends(get_db)
):
    """提交问题"""
    image_base64 = None
    image_url = None
    
    if image and image.filename:
        # 读取图片并转base64
        image_data = await image.read()
        image_base64 = base64.b64encode(image_data).decode()
        # 保存图片
        os.makedirs("static/uploads", exist_ok=True)
        image_path = f"static/uploads/{datetime.now().strftime('%Y%m%d%H%M%S')}_{image.filename}"
        with open(image_path, "wb") as f:
            f.write(image_data)
        image_url = "/" + image_path
    
    # 调用LLM解答
    result = llm_service.solve_math_question(content, image_base64)
    
    if "error" in result:
        raise HTTPException(status_code=500, detail=result["error"])
    
    # 保存到数据库
    question = Question(
        user_id=int(user["sub"]),
        content=content,
        image_url=image_url,
        subject=subject,
        knowledge_point=",".join(result.get("knowledge_points", []))
    )
    db.add(question)
    db.commit()
    db.refresh(question)
    
    # 保存答案
    answer = Answer(
        question_id=question.id,
        content=result.get("answer", ""),
        steps=json.dumps(result.get("steps", []), ensure_ascii=False)
    )
    db.add(answer)
    db.commit()
    
    return {
        "question_id": question.id,
        "answer": result.get("answer"),
        "steps": result.get("steps", []),
        "knowledge_points": result.get("knowledge_points", []),
        "tips": result.get("tips", "")
    }


@app.post("/api/essay")
async def submit_essay(
    title: str = Form(...),
    content: str = Form(...),
    essay_type: str = Form("记叙文"),
    user=Depends(require_auth),
    db: Session = Depends(get_db)
):
    """提交作文批改"""
    # 调用LLM批改
    result = llm_service.review_essay(title, content, essay_type)
    
    if "error" in result:
        raise HTTPException(status_code=500, detail=result["error"])
    
    # 保存到数据库
    essay = Essay(
        user_id=int(user["sub"]),
        title=title,
        content=content,
        essay_type=essay_type,
        overall_score=result.get("overall_score", 0),
        structure_feedback=json.dumps(result.get("structure", {}), ensure_ascii=False),
        grammar_feedback=json.dumps(result.get("grammar", {}), ensure_ascii=False),
        vocabulary_feedback=json.dumps(result.get("vocabulary", {}), ensure_ascii=False),
        suggestions=json.dumps(result.get("suggestions", []), ensure_ascii=False),
        topic_analysis=json.dumps(result.get("topic_analysis", {}), ensure_ascii=False)
    )
    db.add(essay)
    db.commit()
    
    return result


@app.post("/api/chat")
async def chat(
    request: Request,
    user=Depends(require_auth),
    db: Session = Depends(get_db)
):
    """聊天"""
    data = await request.json()
    message = data.get("message", "")
    session_id = data.get("session_id")
    
    # 获取或创建会话
    if session_id:
        session = db.query(ChatSession).filter(ChatSession.id == session_id).first()
    else:
        session = ChatSession(user_id=int(user["sub"]), title=message[:20])
        db.add(session)
        db.commit()
        db.refresh(session)
    
    # 保存用户消息
    user_msg = ChatMessage(session_id=session.id, role="user", content=message)
    db.add(user_msg)
    db.commit()
    
    # 获取历史消息
    history = db.query(ChatMessage).filter(ChatMessage.session_id == session.id).order_by(ChatMessage.created_at).all()
    messages = [{"role": m.role, "content": m.content} for m in history]
    
    # 调用LLM
    response = llm_service.chat(messages)
    
    # 保存助手回复
    assistant_msg = ChatMessage(session_id=session.id, role="assistant", content=response)
    db.add(assistant_msg)
    db.commit()
    
    return {"session_id": session.id, "response": response}


@app.get("/api/chat/sessions")
async def get_chat_sessions(user=Depends(require_auth), db: Session = Depends(get_db)):
    """获取聊天会话列表"""
    sessions = db.query(ChatSession).filter(
        ChatSession.user_id == int(user["sub"])
    ).order_by(ChatSession.created_at.desc()).limit(20).all()
    
    return [{"id": s.id, "title": s.title, "created_at": s.created_at.isoformat()} for s in sessions]


@app.get("/api/chat/messages/{session_id}")
async def get_chat_messages(session_id: int, user=Depends(require_auth), db: Session = Depends(get_db)):
    """获取聊天消息"""
    messages = db.query(ChatMessage).filter(
        ChatMessage.session_id == session_id
    ).order_by(ChatMessage.created_at).all()
    
    return [{"role": m.role, "content": m.content, "created_at": m.created_at.isoformat()} for m in messages]


@app.post("/api/wrong-book/add")
async def add_to_wrong_book(
    request: Request,
    user=Depends(require_auth),
    db: Session = Depends(get_db)
):
    """添加到错题本"""
    data = await request.json()
    question_id = data.get("question_id")
    error_reason = data.get("error_reason", "")
    
    # 检查是否已存在
    existing = db.query(WrongQuestion).filter(
        WrongQuestion.user_id == int(user["sub"]),
        WrongQuestion.question_id == question_id
    ).first()
    
    if existing:
        return {"message": "已在错题本中"}
    
    wrong = WrongQuestion(
        user_id=int(user["sub"]),
        question_id=question_id,
        error_reason=error_reason
    )
    db.add(wrong)
    db.commit()
    
    return {"message": "已添加到错题本"}


@app.get("/api/wrong-book")
async def get_wrong_book(user=Depends(require_auth), db: Session = Depends(get_db), include_mastered: bool = False):
    """获取错题本"""
    if include_mastered:
        wrongs = db.query(WrongQuestion).filter(
            WrongQuestion.user_id == int(user["sub"])
        ).order_by(WrongQuestion.created_at.desc()).all()
    else:
        wrongs = db.query(WrongQuestion).filter(
            WrongQuestion.user_id == int(user["sub"]),
            WrongQuestion.is_mastered == False
        ).order_by(WrongQuestion.created_at.desc()).all()
    
    result = []
    for w in wrongs:
        q = db.query(Question).filter(Question.id == w.question_id).first()
        a = db.query(Answer).filter(Answer.question_id == w.question_id).first()
        if q:
            result.append({
                "id": w.id,
                "question_id": w.question_id,
                "content": q.content,
                "image_url": q.image_url,
                "subject": q.subject,
                "answer": a.content if a else "",
                "steps": json.loads(a.steps) if a and a.steps else [],
                "error_reason": w.error_reason,
                "practice_count": w.practice_count,
                "created_at": w.created_at.isoformat()
            })
    
    return result


@app.post("/api/wrong-book/practice/{wrong_id}")
async def practice_wrong(wrong_id: int, user=Depends(require_auth), db: Session = Depends(get_db)):
    """练习错题"""
    wrong = db.query(WrongQuestion).filter(
        WrongQuestion.id == wrong_id,
        WrongQuestion.user_id == int(user["sub"])
    ).first()
    
    if wrong:
        wrong.practice_count += 1
        db.commit()
    
    return {"message": "已记录练习"}


@app.post("/api/wrong-book/master/{wrong_id}")
async def master_wrong(wrong_id: int, user=Depends(require_auth), db: Session = Depends(get_db)):
    """标记为已掌握"""
    wrong = db.query(WrongQuestion).filter(
        WrongQuestion.id == wrong_id,
        WrongQuestion.user_id == int(user["sub"])
    ).first()
    
    if wrong:
        wrong.is_mastered = True
        db.commit()
    
    return {"message": "已标记为掌握"}


@app.get("/api/wrong-book/mastered")
async def get_mastered_questions(user=Depends(require_auth), db: Session = Depends(get_db)):
    """获取已掌握的题目"""
    wrongs = db.query(WrongQuestion).filter(
        WrongQuestion.user_id == int(user["sub"]),
        WrongQuestion.is_mastered == True
    ).order_by(WrongQuestion.created_at.desc()).all()
    
    result = []
    for w in wrongs:
        q = db.query(Question).filter(Question.id == w.question_id).first()
        a = db.query(Answer).filter(Answer.question_id == w.question_id).first()
        if q:
            result.append({
                "id": w.id,
                "question_id": q.id,
                "content": q.content,
                "image_url": q.image_url,
                "subject": q.subject,
                "knowledge_point": q.knowledge_point,
                "answer": a.content if a else "",
                "steps": json.loads(a.steps) if a and a.steps else [],
                "practice_count": w.practice_count,
                "created_at": w.created_at.isoformat()
            })
    
    return result


@app.get("/api/statistics")
async def get_statistics(user=Depends(require_auth), db: Session = Depends(get_db)):
    """获取学习统计"""
    user_id = int(user["sub"])
    
    # 总题目数
    total_questions = db.query(Question).filter(Question.user_id == user_id).count()
    
    # 错题数
    wrong_count = db.query(WrongQuestion).filter(
        WrongQuestion.user_id == user_id,
        WrongQuestion.is_mastered == False
    ).count()
    
    # 已掌握数
    mastered_count = db.query(WrongQuestion).filter(
        WrongQuestion.user_id == user_id,
        WrongQuestion.is_mastered == True
    ).count()
    
    # 作文数
    essay_count = db.query(Essay).filter(Essay.user_id == user_id).count()
    
    # 平均作文分数
    avg_score = db.query(func.avg(Essay.overall_score)).filter(
        Essay.user_id == user_id
    ).scalar() or 0
    
    # 薄弱知识点（从错题中统计）
    wrongs = db.query(WrongQuestion).filter(
        WrongQuestion.user_id == user_id,
        WrongQuestion.is_mastered == False
    ).all()
    
    knowledge_points = {}
    for w in wrongs:
        q = db.query(Question).filter(Question.id == w.question_id).first()
        if q and q.knowledge_point:
            for kp in q.knowledge_point.split(","):
                kp = kp.strip()
                if kp:
                    knowledge_points[kp] = knowledge_points.get(kp, 0) + 1
    
    weak_points = sorted(knowledge_points.items(), key=lambda x: -x[1])[:5]
    
    # 最近7天的题目数
    from datetime import timedelta
    week_ago = datetime.now() - timedelta(days=7)
    recent_questions = db.query(Question).filter(
        Question.user_id == user_id,
        Question.created_at >= week_ago
    ).count()
    
    return {
        "total_questions": total_questions,
        "wrong_count": wrong_count,
        "mastered_count": mastered_count,
        "essay_count": essay_count,
        "avg_essay_score": round(avg_score, 1),
        "weak_points": [{"name": wp[0], "count": wp[1]} for wp in weak_points],
        "recent_questions": recent_questions,
        "accuracy_rate": round((1 - wrong_count / max(total_questions, 1)) * 100, 1)
    }


@app.get("/api/recommend")
async def get_recommendations(user=Depends(require_auth), db: Session = Depends(get_db)):
    """获取推荐练习"""
    user_id = int(user["sub"])
    
    # 获取薄弱知识点
    wrongs = db.query(WrongQuestion).filter(
        WrongQuestion.user_id == user_id,
        WrongQuestion.is_mastered == False
    ).all()
    
    knowledge_points = set()
    subject = "数学"
    for w in wrongs:
        q = db.query(Question).filter(Question.id == w.question_id).first()
        if q:
            subject = q.subject or "数学"
            if q.knowledge_point:
                for kp in q.knowledge_point.split(","):
                    knowledge_points.add(kp.strip())
    
    if not knowledge_points:
        knowledge_points = ["基础运算"]
    
    # 调用LLM生成推荐题目
    exercises = llm_service.recommend_exercises(list(knowledge_points)[:3], subject)
    
    return exercises


@app.get("/api/profile")
async def get_profile(user=Depends(require_auth), db: Session = Depends(get_db)):
    """获取用户信息"""
    db_user = db.query(User).filter(User.id == int(user["sub"])).first()
    if not db_user:
        raise HTTPException(status_code=404, detail="用户不存在")
    
    return {
        "id": db_user.id,
        "username": db_user.username,
        "email": db_user.email,
        "grade": db_user.grade,
        "subjects": db_user.subjects,
        "created_at": db_user.created_at.isoformat() if db_user.created_at else None
    }


@app.post("/api/profile")
async def update_profile(
    email: str = Form(""),
    grade: str = Form(""),
    subjects: str = Form(""),
    user=Depends(require_auth),
    db: Session = Depends(get_db)
):
    """更新用户信息"""
    db_user = db.query(User).filter(User.id == int(user["sub"])).first()
    if not db_user:
        raise HTTPException(status_code=404, detail="用户不存在")
    
    db_user.email = email
    db_user.grade = grade
    db_user.subjects = subjects
    db.commit()
    
    return {"message": "更新成功"}


@app.get("/api/history")
async def get_history(
    page: int = 1,
    limit: int = 10,
    user=Depends(require_auth),
    db: Session = Depends(get_db)
):
    """获取学习历史"""
    user_id = int(user["sub"])
    offset = (page - 1) * limit
    
    questions = db.query(Question).filter(
        Question.user_id == user_id
    ).order_by(Question.created_at.desc()).offset(offset).limit(limit).all()
    
    result = []
    for q in questions:
        a = db.query(Answer).filter(Answer.question_id == q.id).first()
        result.append({
            "id": q.id,
            "content": q.content,
            "image_url": q.image_url,
            "subject": q.subject,
            "answer": a.content if a else "",
            "created_at": q.created_at.isoformat()
        })
    
    total = db.query(Question).filter(Question.user_id == user_id).count()
    
    return {"items": result, "total": total, "page": page, "limit": limit}


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
