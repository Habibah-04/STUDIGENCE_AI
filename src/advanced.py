"""Feature pages for the 15-module STUDIGENCE AI learning platform."""
from __future__ import annotations
import os, re, json, textwrap, sqlite3, time
from datetime import date, datetime, timedelta
from pathlib import Path
from urllib.parse import quote_plus
import streamlit as st
import pandas as pd
from src.db import (conn, add_task, tasks, update_task_status, save_attempt, attempts,
                    add_mistake, mistakes, add_revision, revisions, review_revision,
                    delete_revision, save_document, documents, get_document, add_focus,
                    focus_total, counts)
from src.ai import generate, tutor_fallback


def ensure_extra_tables():
    with conn() as c:
        c.executescript("""
        CREATE TABLE IF NOT EXISTS study_notes(
            id INTEGER PRIMARY KEY AUTOINCREMENT, user_id INTEGER NOT NULL,
            title TEXT NOT NULL, body TEXT NOT NULL, tags TEXT DEFAULT '', created_at TEXT NOT NULL);
        CREATE TABLE IF NOT EXISTS skill_records(
            id INTEGER PRIMARY KEY AUTOINCREMENT, user_id INTEGER NOT NULL, skill TEXT NOT NULL,
            current_level INTEGER NOT NULL, target_level INTEGER NOT NULL, updated_at TEXT NOT NULL,
            UNIQUE(user_id,skill));
        CREATE TABLE IF NOT EXISTS resume_data(
            user_id INTEGER PRIMARY KEY, name TEXT DEFAULT '', email TEXT DEFAULT '', phone TEXT DEFAULT '',
            linkedin TEXT DEFAULT '', github TEXT DEFAULT '', portfolio TEXT DEFAULT '', objective TEXT DEFAULT '',
            skill_summary TEXT DEFAULT '', projects TEXT DEFAULT '', education TEXT DEFAULT '',
            training TEXT DEFAULT '', internships TEXT DEFAULT '', certifications TEXT DEFAULT '',
            test_scores TEXT DEFAULT '', achievements TEXT DEFAULT '', updated_at TEXT NOT NULL);
        CREATE TABLE IF NOT EXISTS learning_goals(
            id INTEGER PRIMARY KEY AUTOINCREMENT,user_id INTEGER NOT NULL,title TEXT NOT NULL,
            target_date TEXT NOT NULL,progress INTEGER DEFAULT 0,created_at TEXT NOT NULL);
        """)
        # Add newer resume fields to existing databases without deleting saved data.
        existing = {row[1] for row in c.execute("PRAGMA table_info(resume_data)").fetchall()}
        additions = {
            'linkedin': "TEXT DEFAULT ''", 'github': "TEXT DEFAULT ''",
            'portfolio': "TEXT DEFAULT ''", 'objective': "TEXT DEFAULT ''",
            'skill_summary': "TEXT DEFAULT ''", 'training': "TEXT DEFAULT ''",
            'internships': "TEXT DEFAULT ''", 'test_scores': "TEXT DEFAULT ''",
            'achievements': "TEXT DEFAULT ''"
        }
        for col, definition in additions.items():
            if col not in existing:
                c.execute(f"ALTER TABLE resume_data ADD COLUMN {col} {definition}")
        c.commit()

def _delete_note(uid, note_id):
    with conn() as c:
        c.execute("DELETE FROM study_notes WHERE id=? AND user_id=?", (note_id, uid))
        c.commit()

def _save_note(uid,title,body,tags):
    with conn() as c: c.execute('INSERT INTO study_notes(user_id,title,body,tags,created_at) VALUES(?,?,?,?,?)',(uid,title,body,tags,datetime.utcnow().isoformat()))
def _notes(uid):
    with conn() as c: return [dict(r) for r in c.execute('SELECT * FROM study_notes WHERE user_id=? ORDER BY created_at DESC',(uid,))]
def _skills(uid):
    with conn() as c: return [dict(r) for r in c.execute('SELECT * FROM skill_records WHERE user_id=? ORDER BY skill',(uid,))]
def _save_skill(uid,skill,level,target):
    with conn() as c: c.execute('INSERT INTO skill_records(user_id,skill,current_level,target_level,updated_at) VALUES(?,?,?,?,?) ON CONFLICT(user_id,skill) DO UPDATE SET current_level=excluded.current_level,target_level=excluded.target_level,updated_at=excluded.updated_at',(uid,skill,level,target,datetime.utcnow().isoformat()))
def _get_resume(uid):
    with conn() as c:
        row = c.execute("SELECT * FROM resume_data WHERE user_id=?", (uid,)).fetchone()
        return dict(row) if row else {}

def _save_resume(uid, data):
    fields = ['name','email','phone','linkedin','github','portfolio','objective',
              'skill_summary','projects','education','training','internships',
              'certifications','test_scores','achievements']
    values = [str(data.get(k, '') or '').strip() for k in fields]
    with conn() as c:
        c.execute(
            'INSERT INTO resume_data(user_id,' + ','.join(fields) + ',updated_at) VALUES(' +
            ','.join(['?'] * (len(fields)+1)) + ',?) ON CONFLICT(user_id) DO UPDATE SET ' +
            ','.join(f'{k}=excluded.{k}' for k in fields) + ',updated_at=excluded.updated_at',
            [uid, *values, datetime.utcnow().isoformat()]
        )
        c.commit()

def _header(title,subtitle):
    st.title(title); st.caption(subtitle); st.divider()
def _ai(prompt, context=''):
    full_prompt=(prompt + ('\n\nSOURCE MATERIAL:\n'+context if context else ''))
    result=generate(full_prompt)
    if result is None:
        return tutor_fallback(prompt)
    return result
def _download_text(label,content,filename): st.download_button(label,content,file_name=filename,mime='text/plain')


def focus_timer(uid):
    """Show the status of automatic website focus tracking."""
    st.caption("⏱️ Automatic focus tracking is active while STUDIGENCE AI is open. Your time is saved when you close or leave the website.")


def dashboard(uid, user):
    _header(
        'Your Learning Overview',
        'A clear snapshot of your learning activity and what needs attention.'
    )

    c = counts(uid)
    ts = tasks(uid)
    at = attempts(uid)
    focus_minutes = focus_total(uid)

    # Dashboard overview metrics.
    cols = st.columns(4)

    cols[0].metric(
        'Tasks completed',
        c['done'],
        f"of {c['tasks']}"
    )

    cols[1].metric(
        'Quiz attempts',
        c['attempts']
    )

    cols[2].metric(
        'Focus time',
        f'{focus_minutes // 60}h {focus_minutes % 60}m'
    )

    cols[3].metric(
        'Mistakes logged',
        c['mistakes']
    )

    # Optional collapsible timer.
    focus_timer(uid)

    st.divider()

    # Upcoming study tasks.
    pending = [
        task for task in ts
        if task['status'] != 'Completed'
    ]

    st.subheader('Upcoming study tasks')

    if pending:
        for task in pending[:5]:
            st.markdown(
                f"**{task['title']}**  \n"
                f"{task['subject'] or 'General'} · "
                f"due {task['due_date']} · "
                f"{task['priority']} priority"
            )
    else:
        st.info(
            'No pending tasks. Open Study Planner to add your next task.'
        )

    # Quiz performance: use readable quiz labels instead of a timestamp
    # index, which can produce confusing axis labels in Streamlit charts.
    st.subheader('Quiz performance')
    if at:
        df = pd.DataFrame(at).copy()
        df['score'] = pd.to_numeric(df.get('score'), errors='coerce')
        df['created_at'] = pd.to_datetime(df.get('created_at'), errors='coerce')
        df = df.dropna(subset=['score']).sort_values('created_at').reset_index(drop=True)

        if not df.empty:
            # Scores are stored as percentages by save_attempt() (0–100).
            df['score'] = df['score'].clip(0, 100)
            df['quiz_label'] = [
                f"Quiz {i + 1} · {str(row.get('topic') or 'General')[:22]}"
                for i, (_, row) in enumerate(df.iterrows())
            ]

            avg_score = float(df['score'].mean())
            latest_score = float(df.iloc[-1]['score'])
            best_score = float(df['score'].max())
            m1, m2, m3 = st.columns(3)
            m1.metric('Average score', f'{avg_score:.0f}%')
            m2.metric('Latest score', f'{latest_score:.0f}%')
            m3.metric('Best score', f'{best_score:.0f}%')

            chart_df = df[['quiz_label', 'score']].rename(
                columns={'quiz_label': 'Quiz', 'score': 'Score (%)'}
            )
            st.caption(
               "Your quiz performance is calculated "
               "from your completed quiz attempts."
            )
            st.caption('Each bar shows your percentage score in one quiz. Higher bars mean better performance.')

            with st.expander('View quiz history'):
                history = df[['topic', 'created_at', 'score']].copy()
                history['created_at'] = history['created_at'].dt.strftime('%d %b %Y, %I:%M %p')
                history = history.rename(columns={
                    'topic': 'Subject / topic',
                    'created_at': 'Attempt date',
                    'score': 'Score (%)',
                })
                history['Score (%)'] = history['Score (%)'].round(1)
                st.dataframe(history.iloc[::-1], use_container_width=True, hide_index=True)
        else:
            st.info('Quiz attempts were found, but they do not contain readable score values yet.')
    else:
        st.info('No quiz results yet. Open Exam Center, complete a quiz, and submit it. Your score history will appear here.')

def tutor(uid):
    _header('AI Tutor', 'Learn a topic clearly or check how well you can explain it.')
    learn_tab, check_tab = st.tabs(['Learn Something', 'Check My Understanding'])
    with learn_tab:
        with st.form('tutor_learn_form'):
            topic = st.text_area('What would you like to learn?', placeholder='Explain gradient descent with a simple numerical example.', height=110)
            level, style = st.columns(2)
            learner_level = level.selectbox('Learning level', ['Beginner','School','Undergraduate','MCA / University','Advanced'])
            teaching_style = style.selectbox('Explanation style', ['Step-by-step','Simple analogy','Exam-focused','Worked example','Code walkthrough'])
            subject = st.text_input('Subject (optional)')
            submitted = st.form_submit_button('Learn Something', type='primary')
        if submitted:
            if not topic.strip(): st.warning('Enter a topic or question first.')
            else:
                prompt = (f'Explain {topic} to a {learner_level} learner using a {teaching_style} approach. '
                          f'Subject: {subject or "not specified"}. Include a definition, clear explanation, '
                          'a relevant example, important points, and a short recap. Be accurate and do not invent facts.')
                with st.spinner('Preparing your explanation…'):
                    answer = _ai(prompt)
                st.session_state['tutor_lesson'] = answer
            if st.session_state.get('tutor_lesson'):
                st.markdown(st.session_state['tutor_lesson'])
                _download_text('Download explanation', st.session_state['tutor_lesson'], 'studigence_lesson.txt')
    with check_tab:
        topic = st.text_input('Topic you studied', key='understanding_topic')
        explanation = st.text_area('Explain the topic in your own words', height=150, key='understanding_text')
        if st.button('Check My Understanding', type='primary'):
            if not topic.strip() or not explanation.strip(): st.warning('Enter the topic and your explanation.')
            else:
                prompt = (f'Review this student explanation of {topic}: {explanation}. Give feedback under '
                          'What is correct, What is missing or unclear, Suggested correction, and One follow-up question. '
                          'Do not invent facts or assign a validated mastery score.')
                with st.spinner('Reviewing your explanation…'):
                    feedback = _ai(prompt)
                st.markdown(feedback)
    st.caption('AI-generated explanations should be checked against your course material.')

def pdf_lab(uid):
    _header('PDF Lab','Turn your study documents into searchable text, summaries, and question prompts.')
    up=st.file_uploader('Upload a text-based PDF',type=['pdf'])
    if up and st.button('Extract and save PDF',type='primary'):
        try:
            import fitz
            doc=fitz.open(stream=up.getvalue(),filetype='pdf'); txt='\n'.join(p.get_text() for p in doc)
            if not txt.strip(): st.warning('No selectable text found. This may be a scanned PDF; OCR is not included in this build.')
            else:
                did=save_document(uid,up.name,txt); st.success(f'Extracted {len(txt):,} characters and saved document #{did}.'); st.session_state['active_doc']=did
        except Exception as ex: st.error(f'Could not read this PDF: {ex}')
    docs=documents(uid)
    if docs:
        chosen=st.selectbox('Saved documents',docs,format_func=lambda x:f"{x['filename']} · {x['created_at'][:10]}")
        row=get_document(uid,chosen['id'])
        if row:
            txt=row['extracted_text']; st.text_area('Extracted text preview',txt[:12000],height=220)
            col1,col2=st.columns(2)
            if col1.button('Generate summary'):
                with st.spinner('Summarising…'): st.markdown(_ai('Create structured revision notes from this material. Include headings, key terms, formulas if any, and a concise recap.',txt[:18000]))
            if col2.button('Generate practice questions'):
                with st.spinner('Creating questions…'): st.markdown(_ai('Create 10 exam-style questions from this content, with answers and brief explanations at the end.',txt[:18000]))
            _download_text('Download extracted text',txt,Path(row['filename']).stem+'_extracted.txt')
    else: st.info('Upload a PDF to begin. Only selectable text is extracted; scanned-page OCR is not built in.')

QUIZ_BANK={
 'Python': [('Which data type is immutable?',['list','dictionary','tuple','set'],'tuple','Tuples cannot be modified after creation.'),('What does len([2,4,6]) return?',['2','3','6','Error'],'3','There are three elements.'),('Which keyword defines a function?',['func','define','def','lambda'],'def','The def keyword declares a function.')],
 'Artificial Intelligence': [('Which search algorithm uses a heuristic?',['BFS','DFS','A*','Uniform Cost'],'A*','A* combines path cost and heuristic estimate.'),('What does NLP stand for?',['Neural Logic Process','Natural Language Processing','Network Learning Protocol','Numeric Language Program'],'Natural Language Processing','NLP studies computational processing of human language.'),('A rational agent selects actions to:',['Maximise expected performance','Use more memory','Avoid sensors','Always repeat'],'Maximise expected performance','Rationality is defined relative to a performance measure.')],
 'Data Science': [('Which is commonly used for tabular data analysis?',['pandas','pygame','turtle','tkinter'],'pandas','pandas provides DataFrame structures.'),('What is overfitting?',['Model too simple','Model learns noise in training data','Missing values','Feature scaling'],'Model learns noise in training data','Overfit models generalise poorly.'),('Which metric is suitable for classification?',['MAE only','Accuracy','R-squared only','MSE only'],'Accuracy','Accuracy is a common classification metric.')],
 'Mathematics': [('Derivative of x²?',['x','2x','x³','2'],'2x','Apply the power rule.'),('What is 15% of 200?',['15','20','30','35'],'30','0.15 × 200 = 30.'),('A prime number has:',['Exactly two positive divisors','One divisor','Three divisors','No divisors'],'Exactly two positive divisors','A prime has 1 and itself as divisors.')],
 'Computer Networks': [('Which layer routes packets?',['Physical','Network','Session','Presentation'],'Network','The network layer handles logical addressing and routing.'),('TCP is:',['Connection-oriented','Connectionless','A physical cable','An IP address'],'Connection-oriented','TCP establishes a connection before reliable transfer.'),('DNS primarily maps:',['Names to IP addresses','MAC to ports','Files to folders','Users to passwords'],'Names to IP addresses','DNS resolves domain names to records such as IP addresses.')]
}
def _parse_quiz_response(raw):
    if not raw: return None
    cleaned = re.sub(r'^```(?:json)?\s*|\s*```$', '', raw.strip(), flags=re.I)
    try: data = json.loads(cleaned)
    except Exception:
        match = re.search(r'\{.*\}', cleaned, flags=re.S)
        if not match: return None
        try: data = json.loads(match.group(0))
        except Exception: return None
    questions = data.get('questions') if isinstance(data, dict) else None
    if not isinstance(questions, list) or len(questions) < 10: return None
    valid = []
    for item in questions[:10]:
        if not isinstance(item, dict): return None
        q = str(item.get('question','')).strip(); opts = item.get('options'); ans = str(item.get('answer','')).strip(); exp = str(item.get('explanation','')).strip()
        if not q or not isinstance(opts,list) or len(opts) != 4 or not exp: return None
        opts = [str(x).strip() for x in opts]
        if ans not in opts: return None
        valid.append({'question':q,'options':opts,'answer':ans,'explanation':exp,'category':str(item.get('category','Conceptual'))})
    return valid

def exam(uid):
    _header('Exam Center', 'Enter any topic and practise with exactly 10 multiple-choice questions.')
    with st.form('dynamic_exam_form'):
        topic = st.text_input('Enter any subject or topic', placeholder='e.g. Operating System deadlocks, Python OOP, Photosynthesis')
        level = st.selectbox('Difficulty', ['Mixed','Beginner','Intermediate','Advanced'])
        submitted = st.form_submit_button('Generate 10 Questions', type='primary')
    if submitted:
        if not topic.strip(): st.warning('Enter a topic first.')
        else:
            prompt = f"""Create exactly 10 accurate multiple-choice questions about: {topic}. Difficulty: {level}.
Return ONLY valid JSON in this shape: {{"questions":[{{"question":"...","options":["A","B","C","D"],"answer":"exact option text","explanation":"brief explanation","category":"Conceptual"}}]}}.
Every question must have exactly four distinct options and one unambiguous correct answer. Cover varied subtopics. No markdown."""
            with st.spinner('Generating your 10-question exam…'):
                generated = _ai(prompt)
            parsed = _parse_quiz_response(generated)
            if parsed:
                st.session_state['dynamic_exam'] = {'topic':topic.strip(),'questions':parsed,'level':level,'token':datetime.utcnow().strftime('%Y%m%d%H%M%S%f')}
                st.session_state.pop('dynamic_exam_result', None)
            else:
                st.error('The AI response did not contain 10 valid questions. Please try again with a more specific topic.')
    exam_data = st.session_state.get('dynamic_exam')
    if exam_data:
        st.subheader(f"{exam_data['topic']} — 10 Questions")
        with st.form('dynamic_exam_answers'):
            answers=[]
            for i, q in enumerate(exam_data['questions']):
                st.markdown(f"**Question {i+1}. {q['question']}**")
                answers.append(st.radio('Choose one answer', q['options'], index=None, key=f"dyn_exam_{exam_data['token']}_{i}"))
            submitted_answers = st.form_submit_button('Submit Exam', type='primary')
        if submitted_answers:
            if any(x is None for x in answers): st.warning('Please answer all 10 questions before submitting.')
            else:
                details=[]; correct_count=0
                for q, chosen in zip(exam_data['questions'], answers):
                    ok = chosen == q['answer']; correct_count += int(ok)
                    details.append({'question':q['question'],'chosen':chosen,'correct':q['answer'],'explanation':q['explanation'],'result':'Correct' if ok else 'Incorrect'})
                    if not ok: add_mistake(uid, exam_data['topic'], q['question'], chosen, q['answer'], q['category'])
                save_attempt(uid, exam_data['topic'], 10, correct_count, details)
                st.session_state['dynamic_exam_result']={'correct':correct_count,'details':details,'topic':exam_data['topic']}
        result=st.session_state.get('dynamic_exam_result')
        if result:
            st.metric('Your score', f"{result['correct']}/10", f"{result['correct']*10}%")
            for i, item in enumerate(result['details'],1):
                with st.expander(f"Q{i}. {item['result']} — {item['question']}"):
                    st.write('Your answer:', item['chosen'])
                    st.write('Correct answer:', item['correct'])
                    st.write('Explanation:', item['explanation'])

def planner(uid):
    _header('Study Planner', 'Organise your workload and track every task from pending to completed.')
    with st.form('task_form'):
        a,b=st.columns(2); title_text=a.text_input('Task title',placeholder='Revise database normalisation'); subject=b.text_input('Subject',placeholder='DBMS')
        c,d,e=st.columns(3); due=c.date_input('Due date',value=date.today()); minutes=d.number_input('Duration (minutes)',15,480,45,step=15); priority=e.selectbox('Priority',['Low','Medium','High'])
        submitted=st.form_submit_button('Add study task',type='primary')
    if submitted:
        if title_text.strip(): add_task(uid,title_text.strip(),subject.strip(),due,int(minutes),priority); st.success('Task added.'); st.rerun()
        else: st.warning('Enter a task title.')
    items=tasks(uid); total=len(items); done=sum(x['status']=='Completed' for x in items); pending=total-done
    st.subheader('Your progress')
    x,y,z=st.columns(3); x.metric('Total tasks',total); y.metric('Completed',done); z.metric('Remaining',pending)
    st.progress(done/total if total else 0, text=f'{round(done/total*100) if total else 0}% completed')
    if not items: st.info('Your planner is empty. Add your first study task above.'); return
    for item in items:
        with st.container(border=True):
            left, mid, right = st.columns([4,2,2])
            left.markdown(f"**{item['title']}**")
            left.caption(f"{item['subject'] or 'General'} · {item['minutes']} min · Due {item['due_date']}")
            status_color = 'success' if item['status']=='Completed' else 'warning' if item['priority']=='High' else 'info'
            if item['status']=='Completed': mid.success('Completed')
            else: mid.info(item['status'])
            right.caption(f"{item['priority']} priority")
            if item['status'] != 'Completed':
                if right.button('Mark complete', key=f"complete_{item['id']}", use_container_width=True):
                    update_task_status(item['id'], uid, 'Completed'); st.rerun()

def learning_dna(uid):
    _header('Learning DNA','A descriptive view of your learning patterns—not a validated psychometric or predictive score.')
    hist=attempts(uid)
    if not hist: st.info('Complete quizzes to build your learning profile.'); return
    df=pd.DataFrame(hist); agg=df.groupby('topic').agg(attempts=('score','count'),average_score=('score','mean')).reset_index(); st.dataframe(agg,use_container_width=True,hide_index=True); st.bar_chart(agg.set_index('topic')['average_score'])
    best=agg.sort_values('average_score',ascending=False).iloc[0]; low=agg.sort_values('average_score').iloc[0]; st.success(f"Strongest recorded topic: {best['topic']} ({best['average_score']:.0f}%).") ; st.warning(f"Topic to revisit: {low['topic']} ({low['average_score']:.0f}%).")

def mistake_dna(uid):
    _header('Mistake DNA','Review incorrect answers and identify recurring topics and error categories.')
    ms=mistakes(uid)
    if not ms: st.info('No mistakes logged yet. Submit a quiz with an incorrect answer to start.'); return
    df=pd.DataFrame(ms); st.metric('Recorded mistakes',len(df)); st.bar_chart(df.groupby('topic').size()); st.dataframe(df[['topic','question','chosen','correct_answer','category','created_at']],use_container_width=True,hide_index=True)
    if st.button('Add all mistake topics to revision queue'):
        for topic in sorted(set(df['topic'])): add_revision(uid,f'Revisit: {topic}',date.today()+timedelta(days=1))
        st.success('Topics added to revision queue.')

def revision(uid):
    _header('Memory Revision', 'Build a revision queue and use recall quality to schedule your next review.')
    with st.form('revision_add'):
        topic=st.text_input('Topic to revise',placeholder='OSI model layers'); due=st.date_input('First review date',value=date.today()); ok=st.form_submit_button('Add to revision queue')
    if ok and topic.strip(): add_revision(uid,topic.strip(),due); st.success('Added to revision queue.'); st.rerun()
    rows=revisions(uid)
    if not rows: st.info('Your revision queue is empty.'); return
    for item in rows:
        with st.container(border=True):
            a,b,c,d=st.columns([3,1.5,2,1])
            a.markdown(f"**{item['topic']}**"); b.caption(f"Due {item['due_date']}")
            quality=c.selectbox('Recall quality',list(range(6)),index=3,key=f"quality_{item['id']}")
            if c.button('Record review',key=f"review_{item['id']}"): review_revision(uid,item['id'],quality); st.success('Next review scheduled.'); st.rerun()
            if d.button('Delete',key=f"delete_revision_{item['id']}"): delete_revision(uid,item['id']); st.rerun()

def career(uid,profile):
    _header('Career Intelligence','Explore role requirements and build a practical learning roadmap.')
    role=st.selectbox('Target role',['Data Analyst','Data Scientist','Machine Learning Engineer','Python Developer','Frontend Developer','AI Engineer','Cybersecurity Analyst','Cloud Engineer']); level=st.selectbox('Current stage',['Beginner','Intermediate','Advanced']); weeks=st.slider('Roadmap duration (weeks)',4,32,12)
    if st.button('Generate career roadmap',type='primary'):
        prompt=f'Create a {weeks}-week realistic roadmap for a {level} learner targeting {role}. Include skills, weekly milestones, 3 portfolio projects, interview preparation, and measurable outcomes. Do not invent guaranteed placement outcomes.'
        with st.spinner('Building roadmap…'): ans=_ai(prompt)
        st.markdown(ans); _download_text('Download roadmap',ans,f'{role.lower().replace(" ","_")}_roadmap.txt')
    st.markdown('**Role research shortcuts**')
    st.link_button('Search current job descriptions',f'https://www.google.com/search?q={quote_plus(role+" job description skills India")}',use_container_width=False)

def _resume_text(data):
    sections = [
        ('OBJECTIVE', 'objective'), ('SKILL SUMMARY', 'skill_summary'),
        ('PROJECTS', 'projects'), ('EDUCATION', 'education'),
        ('TRAINING', 'training'), ('INTERNSHIPS', 'internships'),
        ('CERTIFICATIONS', 'certifications'), ('TEST SCORES', 'test_scores'),
        ('ACHIEVEMENTS', 'achievements')
    ]
    contact = ' | '.join(x for x in [data.get('phone',''),data.get('email','')] if x)
    links = ' | '.join(x for x in [data.get('linkedin',''),data.get('github',''),data.get('portfolio','')] if x)
    parts=[data.get('name','').upper(), contact, links]
    for heading,key in sections:
        if data.get(key,'').strip(): parts.extend(['',heading,data[key].strip()])
    return '\n'.join(x for x in parts if x is not None)

def _resume_docx_bytes(data):
    from io import BytesIO
    from docx import Document
    from docx.shared import Inches, Pt, RGBColor
    from docx.enum.text import WD_ALIGN_PARAGRAPH
    doc=Document(); sec=doc.sections[0]
    sec.top_margin=Inches(.55); sec.bottom_margin=Inches(.55); sec.left_margin=Inches(.7); sec.right_margin=Inches(.7)
    normal=doc.styles['Normal']; normal.font.name='Calibri'; normal.font.size=Pt(9.5); normal.font.color.rgb=RGBColor(45,45,45)
    name=doc.add_paragraph(); name.alignment=WD_ALIGN_PARAGRAPH.CENTER
    run=name.add_run(data.get('name','YOUR NAME').upper()); run.bold=True; run.font.size=Pt(18); run.font.color.rgb=RGBColor(45,45,45)
    contact=' | '.join(x for x in [data.get('phone',''),data.get('email','')] if x)
    if contact:
        p=doc.add_paragraph(contact); p.alignment=WD_ALIGN_PARAGRAPH.CENTER
    links=' | '.join(x for x in [data.get('linkedin',''),data.get('github',''),data.get('portfolio','')] if x)
    if links:
        p=doc.add_paragraph(links); p.alignment=WD_ALIGN_PARAGRAPH.CENTER
    for heading,key in [('OBJECTIVE','objective'),('SKILL SUMMARY','skill_summary'),('PROJECTS','projects'),('EDUCATION','education'),('TRAINING','training'),('INTERNSHIPS','internships'),('CERTIFICATIONS','certifications'),('TEST SCORES','test_scores'),('ACHIEVEMENTS','achievements')]:
        value=data.get(key,'').strip()
        if not value: continue
        p=doc.add_paragraph(); p.paragraph_format.space_before=Pt(5); p.paragraph_format.space_after=Pt(2)
        r=p.add_run(heading); r.bold=True; r.font.size=Pt(10); r.font.color.rgb=RGBColor(142,121,62)
        for line in value.splitlines():
            q=doc.add_paragraph(line.strip()); q.paragraph_format.space_after=Pt(1)
    out=BytesIO(); doc.save(out); return out.getvalue()

def resume(uid):
    _header('Resume Studio', 'Build an ATS-friendly resume using the section order and clean layout of your uploaded resume.')
    d=_get_resume(uid)
    with st.form('resume_form'):
        st.subheader('Contact information')
        a,b=st.columns(2); name=a.text_input('Full name',d.get('name','')); email=b.text_input('Email',d.get('email',''))
        a,b,c=st.columns(3); phone=a.text_input('Phone',d.get('phone','')); linkedin=b.text_input('LinkedIn URL',d.get('linkedin','')); github=c.text_input('GitHub URL',d.get('github',''))
        portfolio=st.text_input('Portfolio URL',d.get('portfolio',''))
        st.subheader('Resume sections')
        objective=st.text_area('Objective',d.get('objective',''),height=85)
        skill_summary=st.text_area('Skill Summary',d.get('skill_summary',''),height=150,help='Use category-based lines, e.g. Programming Languages:, AI/ML:, Frontend:, Backend:, Database:, Tools:, Design:, Soft Skills:.')
        projects=st.text_area('Projects',d.get('projects',''),height=150)
        education=st.text_area('Education',d.get('education',''),height=150)
        training=st.text_area('Training',d.get('training',''),height=90)
        internships=st.text_area('Internships',d.get('internships',''),height=110)
        certifications=st.text_area('Certifications',d.get('certifications',''),height=110)
        test_scores=st.text_area('Test Scores',d.get('test_scores',''),height=80)
        achievements=st.text_area('Achievements',d.get('achievements',''),height=80)
        saved=st.form_submit_button('Save Resume',type='primary')
    if saved:
        _save_resume(uid,locals()); st.success('Resume saved successfully.'); d=_get_resume(uid)
    if d and any(str(d.get(k,'')).strip() for k in ['name','objective','skill_summary','projects','education']):
        preview=_resume_text(d)
        st.subheader('Resume preview')
        st.text_area('Preview',preview,height=420)
        c1,c2=st.columns(2)
        c1.download_button('Download editable Word resume',_resume_docx_bytes(d),file_name='studigence_resume.docx',mime='application/vnd.openxmlformats-officedocument.wordprocessingml.document')
        c2.download_button('Download plain-text resume',preview,file_name='studigence_resume.txt',mime='text/plain')
        if st.button('Review Resume with AI'):
            feedback=_ai('Review this resume for clarity, ATS readability, consistency, and missing evidence. Suggest improvements without fabricating details.',preview)
            st.markdown(feedback)

def video_finder(uid):
    _header('YouTube Learning Finder','Generate focused YouTube searches for a topic and learning level.')
    topic=st.text_input('What do you want to learn?',placeholder='SQL joins, neural networks, calculus…'); level=st.selectbox('Level',['Beginner','Intermediate','Advanced']); lang=st.selectbox('Preferred language',['English','Hindi','Any']); kind=st.selectbox('Content type',['Complete course','Concept explanation','Practical project','Interview preparation','Revision']);
    if topic.strip():
        query=f'{topic} {level} {lang} {kind} tutorial'; st.link_button('Search YouTube',f'https://www.youtube.com/results?search_query={quote_plus(query)}',use_container_width=True); st.caption('This opens live YouTube search results; videos are not independently ranked or verified by this app.')
        if st.button('Create a watch checklist'): st.session_state['watchlist']=[f'Understand fundamentals of {topic}',f'Practise 3 examples of {topic}',f'Build a mini-project using {topic}',f'Summarise key takeaways from the {kind.lower()}']
    for item in st.session_state.get('watchlist',[]): st.checkbox(item,key='watch_'+item)

def notes_studio(uid):
    _header('Notes Studio', 'Save, download, and manage your personal study notes.')
    tab1,tab2=st.tabs(['My Notes','Assignment Outline'])
    with tab1:
        with st.form('note_form'):
            note_title=st.text_input('Note title'); tags=st.text_input('Tags'); body=st.text_area('Write your notes',height=180); save=st.form_submit_button('Save Note')
        if save:
            if note_title.strip() and body.strip(): _save_note(uid,note_title.strip(),body,tags.strip()); st.success('Note saved.'); st.rerun()
            else: st.warning('Enter both a title and note content.')
        for note in _notes(uid):
            with st.expander(f"{note['title']} · {note['created_at'][:10]}"):
                st.caption(note.get('tags','')); st.write(note['body'])
                a,b=st.columns(2)
                a.download_button('Download note',note['body'],file_name=re.sub(r'[^a-zA-Z0-9_-]','_',note['title'])+'.txt',mime='text/plain',key=f"download_note_{note['id']}")
                if b.button('Delete note',key=f"delete_note_{note['id']}"): _delete_note(uid,note['id']); st.rerun()
    with tab2:
        topic=st.text_input('Assignment topic'); course=st.text_input('Course / subject'); words=st.number_input('Approximate word count',300,5000,1000,100)
        if st.button('Generate assignment structure'):
            if topic.strip(): st.markdown(_ai(f'Create an academic assignment outline for {topic} in {course}. Target {words} words. Include sections, key questions, research directions, and citation reminders. Do not fabricate references.'))
            else: st.warning('Enter an assignment topic.')

def analytics(uid):
    _header('Analytics & Reports','Review your study activity and export your records.')
    ts=tasks(uid); at=attempts(uid); ms=mistakes(uid); rs=revisions(uid)
    a,b,c,d=st.columns(4); a.metric('Tasks',len(ts)); b.metric('Quiz attempts',len(at)); c.metric('Mistakes',len(ms)); d.metric('Revision topics',len(rs))
    if at:
        df=pd.DataFrame(at); st.subheader('Performance by subject'); st.bar_chart(df.groupby('topic')['score'].mean());
    if ts: st.subheader('Task status'); st.bar_chart(pd.Series([x['status'] for x in ts]).value_counts())
    report={'tasks':ts,'quiz_attempts':at,'mistakes':ms,'revisions':rs,'focus_minutes':focus_total(uid)}
    st.download_button('Export all available activity as JSON',json.dumps(report,indent=2,default=str),file_name='studigence_activity_report.json',mime='application/json')

def settings(uid,profile):
    _header('Settings & Profile','Update your learner profile and review application configuration.')
    with st.form('profile_form'):
        name=st.text_input('Name',profile.get('name','')); level=st.selectbox('Education level',['School','College','University','Competitive exam','Lifelong learner'],index=['School','College','University','Competitive exam','Lifelong learner'].index(profile.get('education_level','College')) if profile.get('education_level','College') in ['School','College','University','Competitive exam','Lifelong learner'] else 1); goal=st.text_input('Learning goal',profile.get('goal','')); ok=st.form_submit_button('Save profile')
    if ok:
        from src.db import update_profile
        update_profile(uid,name,level,goal); st.success('Profile updated. Please sign out and back in to refresh the sidebar name.')
    st.markdown('**AI configuration**')
    st.write(
        'Set GEMINI_API_KEY and GEMINI_MODEL in your .env file '
        'or Streamlit Secrets. The core app remains usable without an API key.'
    )
    st.markdown('**Data & privacy**'); st.write('Your account and learning records are stored in SQLite in this deployment. For durable multi-user production hosting, use managed PostgreSQL and private object storage; Community Cloud local files may not be persistent.')

MODULES=[('Dashboard',dashboard),('AI Tutor',tutor),('PDF Lab',pdf_lab),('Exam Center',exam),('Study Planner',planner),('Learning DNA',learning_dna),('Mistake DNA',mistake_dna),('Memory Revision',revision),('Career Intelligence',career),('Resume Studio',resume),('YouTube Finder',video_finder),('Notes Studio',notes_studio),('Analytics & Reports',analytics),('Settings',settings)]
