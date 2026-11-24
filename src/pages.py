import streamlit as st
import pandas as pd
from datetime import date, timedelta
from collections import Counter
from src.db import (tasks, add_task, update_task_status, attempts, save_attempt, add_mistake,
                    mistakes, add_revision, revisions, review_revision, documents, save_document,
                    get_document, add_focus, focus_total, counts, update_profile)
from src.content import QUIZ_BANK
from src.ai import generate, tutor_fallback

def title(h, sub=None):
    st.title(h)
    if sub: st.caption(sub)

def dashboard_page(user, profile):
    title(f"Welcome back, {user['name'].split()[0]} 👋", "Your learning workspace, all in one place.")
    c=counts(user["id"]); a=attempts(user["id"]); t=tasks(user["id"])
    avg=round(sum(x["score"] for x in a)/len(a),1) if a else 0
    cols=st.columns(4)
    cols[0].metric("Quiz attempts",c["attempts"])
    cols[1].metric("Average score",f"{avg}%")
    cols[2].metric("Tasks completed",c["done"],f"of {c['tasks']}")
    cols[3].metric("Focus time",f"{focus_total(user['id'])//60}h {focus_total(user['id'])%60}m")
    st.subheader("Your next steps")
    pending=[x for x in t if x["status"]!="Completed"]
    if pending:
        for task in pending[:5]:
            st.write(f"• **{task['title']}** — {task['subject'] or 'General'} · due {task['due_date']}")
    else: st.info("No pending tasks. Add a study task in Study Planner.")
    st.subheader("Recent learning activity")
    if a:
        df=pd.DataFrame(a[:10]); st.line_chart(df.set_index("created_at")["score"])
    else: st.info("Complete a quiz to start building your learning history.")
    st.subheader("Suggested actions")
    x,y,z=st.columns(3)
    x.info("📘 Upload course material in PDF Lab.")
    y.info("🧠 Take a diagnostic quiz in Exam Center.")
    z.info("🗓️ Add your next study session in Study Planner.")

def tutor_page(user):
    title("AI Personal Tutor","Ask questions, request examples, or learn a concept step by step.")
    if "chat_history" not in st.session_state: st.session_state.chat_history=[]
    for m in st.session_state.chat_history:
        with st.chat_message(m["role"]): st.markdown(m["content"])
    q=st.chat_input("Ask a study question...")
    if q:
        st.session_state.chat_history.append({"role":"user","content":q})
        with st.chat_message("user"): st.markdown(q)
        context=""
        docs=documents(user["id"])
        if docs:
            context="Available uploaded documents: "+", ".join(d["filename"] for d in docs)
        answer=generate(q + ("\n"+context if context else ""))
        if answer is None: answer=tutor_fallback(q)
        st.session_state.chat_history.append({"role":"assistant","content":answer})
        with st.chat_message("assistant"): st.markdown(answer)
    with st.expander("How to enable AI-generated answers"):
        st.write("Set OPENAI_API_KEY, OPENAI_MODEL and optionally OPENAI_BASE_URL in your local .env or Streamlit Cloud Secrets.")

def pdf_lab_page(user):
    title("Smart PDF Lab","Extract text from course documents and ask questions grounded in the selected file.")
    up=st.file_uploader("Upload a PDF, TXT or Markdown file",type=["pdf","txt","md"])
    if up and st.button("Process document"):
        try:
            if up.name.lower().endswith(".pdf"):
                import fitz
                doc=fitz.open(stream=up.getvalue(),filetype="pdf")
                text="\n".join(p.get_text() for p in doc)
            else: text=up.getvalue().decode("utf-8",errors="replace")
            if not text.strip(): st.error("No selectable text found. Scanned PDFs need OCR before they can be searched.")
            else:
                did=save_document(user["id"],up.name,text)
                st.success(f"Saved {up.name} ({len(text):,} characters). Document ID: {did}")
        except Exception as e: st.error(f"Could not process file: {e}")
    docs=documents(user["id"])
    if docs:
        st.subheader("Your documents")
        labels={f"{d['filename']} (#{d['id']})":d["id"] for d in docs}
        selected=st.selectbox("Choose a document",list(labels))
        doc=get_document(user["id"],labels[selected])
        query=st.text_input("Ask a question about this document")
        if st.button("Find answer",disabled=not query):
            text=doc["extracted_text"]
            # Lightweight local retrieval: rank paragraphs by query-term overlap.
            terms=set(query.lower().split())
            paras=[p.strip() for p in text.splitlines() if len(p.strip())>35]
            ranked=sorted(paras,key=lambda p:sum(w in p.lower() for w in terms),reverse=True)[:5]
            excerpts="\n\n".join(ranked)
            prompt=f"Answer only from the source excerpts. If the answer is not present, say so. Cite a page only if supplied.\nQuestion: {query}\nSource excerpts:\n{excerpts}"
            answer=generate(prompt,system="You answer questions using only supplied document excerpts.")
            if answer is None: answer="**Relevant extracted passages:**\n\n"+(excerpts or "No matching passage found. Try different keywords.")
            st.markdown(answer)
        with st.expander("Preview extracted text"): st.text(doc["extracted_text"][:12000])
    else: st.caption("Uploaded documents will appear here.")

def quiz_page(user):
    title("Exam Center","Practice topic-wise questions and automatically record mistakes.")
    topic=st.selectbox("Choose a subject",list(QUIZ_BANK))
    count=st.slider("Number of questions",3,5,5)
    questions=QUIZ_BANK[topic][:count]
    with st.form("quiz_form"):
        answers=[]
        for i,(q,opts,correct,cat) in enumerate(questions):
            st.markdown(f"**Q{i+1}. {q}**")
            answers.append(st.radio("Choose an answer",opts,key=f"q_{topic}_{i}",index=None))
        submitted=st.form_submit_button("Submit quiz")
    if submitted:
        if any(x is None for x in answers): st.warning("Answer every question before submitting.")
        else:
            correct_count=0; detail=[]
            for i,((q,opts,correct,cat),chosen) in enumerate(zip(questions,answers)):
                ok=chosen==correct; correct_count+=int(ok)
                detail.append({"question":q,"chosen":chosen,"correct":correct,"result":"Correct" if ok else "Incorrect"})
                if not ok: add_mistake(user["id"],topic,q,chosen,correct,cat)
            save_attempt(user["id"],topic,len(questions),correct_count,detail)
            st.session_state.last_quiz={"topic":topic,"correct":correct_count,"total":len(questions),"detail":detail}
    if "last_quiz" in st.session_state:
        r=st.session_state.last_quiz
        st.subheader("Latest result")
        st.metric("Score",f"{r['correct']}/{r['total']}",f"{round(r['correct']/r['total']*100)}%")
        for d in r["detail"]:
            st.write(("✅ " if d["result"]=="Correct" else "❌ ")+d["question"])
            if d["result"]=="Incorrect": st.caption(f"Your answer: {d['chosen']} · Correct: {d['correct']}")

def planner_page(user):
    title("AI Study Planner","Create manageable tasks and track your progress.")
    with st.form("task_form"):
        a,b=st.columns(2)
        name=a.text_input("Task title",placeholder="Revise BFS and DFS")
        subject=b.text_input("Subject",placeholder="Artificial Intelligence")
        c,d,e=st.columns(3)
        due=c.date_input("Due date",value=date.today())
        minutes=d.number_input("Duration (minutes)",15,480,45,step=15)
        priority=e.selectbox("Priority",["Low","Medium","High"])
        submit=st.form_submit_button("Add task")
    if submit:
        if name.strip(): add_task(user["id"],name.strip(),subject,due,int(minutes),priority); st.success("Task added."); st.rerun()
        else: st.error("Enter a task title.")
    st.subheader("Your tasks")
    ts=tasks(user["id"])
    if not ts: st.info("No tasks yet.")
    for t in ts:
        cols=st.columns([4,2,2,2])
        cols[0].write(f"**{t['title']}**")
        cols[0].caption(t["subject"])
        cols[1].write(t["due_date"])
        cols[2].write(t["priority"])
        if t["status"]=="Completed": cols[3].success("Done")
        elif cols[3].button("Complete",key=f"done_{t['id']}"):
            update_task_status(t["id"],user["id"],"Completed"); st.rerun()

def learning_dna_page(user):
    title("Learning DNA","A transparent profile built from your actual activity—not a personality label.")
    a=attempts(user["id"]); ms=mistakes(user["id"])
    if not a: st.info("Take quizzes to generate your first learning profile."); return
    avg=sum(x["score"] for x in a)/len(a)
    total=sum(x["total"] for x in a); correct=sum(x["correct"] for x in a)
    c1,c2,c3=st.columns(3); c1.metric("Observed accuracy",f"{100*correct/max(total,1):.1f}%"); c2.metric("Quiz attempts",len(a)); c3.metric("Recorded mistakes",len(ms))
    df=pd.DataFrame(a)
    st.subheader("Score history"); st.line_chart(df.iloc[::-1].set_index("created_at")["score"])
    st.subheader("Subject performance")
    st.bar_chart(df.groupby("topic")["score"].mean())
    st.info("Profile limitation: this is an activity-based baseline. Reliable retention and comprehension estimates require repeated delayed tests and explanation assessments.")

def mistake_page(user):
    title("Mistake DNA","Review errors and identify patterns worth practising.")
    ms=mistakes(user["id"])
    if not ms: st.info("No mistakes recorded yet. Complete a quiz to populate this page."); return
    counts={}
    for m in ms: counts[m["category"]]=counts.get(m["category"],0)+1
    st.bar_chart(pd.Series(counts))
    for m in ms[:30]:
        with st.expander(f"{m['topic']} · {m['category']} · {m['created_at'][:10]}"):
            st.write("**Question:**",m["question"])
            st.write("Your answer:",m["chosen"])
            st.success("Correct answer: "+m["correct_answer"])
    st.caption("Current quiz bank uses transparent question-level categories. Automated free-text error classification is an extension point, not yet trained.")

def revision_page(user):
    title("Memory & Revision","Create review cards and use a simple spaced-repetition schedule.")
    with st.form("revision_add"):
        topic=st.text_input("Topic to revise",placeholder="OSI model layers")
        due=st.date_input("First review date",value=date.today())
        submit=st.form_submit_button("Add to revision queue")
    if submit and topic.strip():
        add_revision(user["id"],topic.strip(),due); st.success("Added to revision queue."); st.rerun()
    rs=revisions(user["id"])
    st.subheader("Revision queue")
    if not rs: st.info("Your queue is empty.")
    for r in rs:
        c1,c2,c3=st.columns([3,2,3])
        c1.write("**"+r["topic"]+"**"); c2.write("Due: "+r["due_date"])
        quality=c3.select_slider("Recall quality",options=[0,1,2,3,4,5],value=3,key=f"quality_{r['id']}")
        if c3.button("Review & schedule next",key=f"review_{r['id']}"):
            review_revision(user["id"],r["id"],quality); st.success("Next review scheduled."); st.rerun()

def career_page(user,profile):
    title("Career Intelligence","Connect your current skills and goals to a practical learning plan.")
    with st.form("career_form"):
        target=st.text_input("Target role",placeholder="Python Developer / Data Analyst / ML Engineer")
        skills=st.text_area("Current skills (comma separated)",placeholder="Python, SQL, HTML, statistics")
        submit=st.form_submit_button("Generate skill-gap plan")
    if submit:
        prompt=f"Create a realistic beginner-to-job-ready skill roadmap for target role: {target}. Current skills: {skills}. Return skill gaps, learning sequence, 3 portfolio projects and interview topics. Be honest about assumptions."
        result=generate(prompt)
        if result: st.markdown(result)
        else:
            st.info("Local roadmap template")
            st.markdown(f"**Target:** {target}\n\n**Suggested sequence:** Python fundamentals → Git/GitHub → SQL → role-specific tools → portfolio projects → interview practice.\n\n**Portfolio ideas:**\n1. Data cleaning and visualization project.\n2. End-to-end application using your target stack.\n3. Domain-specific capstone with documentation and tests.")
    st.caption("Opportunity listings are not fetched in this offline-first version. Verify internships and jobs on official employer websites.")

def focus_page(user):
    title("Focus Room","Record focused study sessions. Use a timer on your device and log the session when complete.")
    mins=st.number_input("Focused minutes",min_value=5,max_value=240,value=25,step=5)
    note=st.text_input("What did you work on?")
    if st.button("Log completed focus session"):
        add_focus(user["id"],int(mins),note); st.success("Focus session saved.")
    st.metric("Total recorded focus time",f"{focus_total(user['id'])} minutes")
    st.caption("This page records completed sessions; it does not run a background timer.")

def reports_page(user):
    title("Progress Reports","A summary of activity recorded in your account.")
    a=attempts(user["id"]); t=tasks(user["id"]); m=mistakes(user["id"])
    c1,c2,c3=st.columns(3)
    c1.metric("Quizzes",len(a)); c2.metric("Tasks completed",sum(x["status"]=="Completed" for x in t)); c3.metric("Mistakes",len(m))
    if a:
        df=pd.DataFrame(a)
        st.subheader("Quiz history")
        st.dataframe(df[["created_at","topic","correct","total","score"]],use_container_width=True)
        csv=df.to_csv(index=False).encode("utf-8")
        st.download_button("Download quiz history CSV",csv,"studigence_quiz_history.csv","text/csv")
    else: st.info("Reports will appear after you complete learning activities.")

def settings_page(user,profile):
    title("Settings & Profile","Manage your learning profile.")
    with st.form("profile_form"):
        name=st.text_input("Full name",profile.get("name",""))
        level=st.selectbox("Education level",["School","College","University","Competitive exam","Lifelong learner"],
                           index=["School","College","University","Competitive exam","Lifelong learner"].index(profile.get("education_level","College")) if profile.get("education_level","College") in ["School","College","University","Competitive exam","Lifelong learner"] else 1)
        goal=st.text_area("Learning goal",profile.get("goal",""))
        if st.form_submit_button("Save profile"):
            update_profile(user["id"],name,level,goal)
            st.success("Profile updated. Sign out and back in to refresh sidebar details.")
    st.markdown("### Privacy")
    st.write("Your study records are stored in the app's SQLite database. On Streamlit Community Cloud, the local filesystem may be ephemeral. For durable multi-user production use, connect managed PostgreSQL and object storage.")
    st.markdown("### AI configuration")
    st.write("Configure `OPENAI_API_KEY`, `OPENAI_MODEL` and optionally `OPENAI_BASE_URL` in your environment or Streamlit secrets.")
