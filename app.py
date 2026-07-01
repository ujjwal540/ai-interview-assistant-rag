"""
AI Interview Assistant (RAG)
----------------------------
Streamlit Frontend

Run:
    streamlit run app.py
"""

import tempfile
from pathlib import Path

import streamlit as st

from src.config import settings
from src.ingest import build_documents
from src.vectorstore import (
    build_vectorstore,
    save_vectorstore,
    load_vectorstore,
    vectorstore_exists,
)
from src.question_generator import generate_interview_questions
from src.answer_evaluator import evaluate_answer
from src.mock_interview import MockInterviewSession

# ==========================================================
# Streamlit Configuration
# ==========================================================

st.set_page_config(
    page_title="AI Interview Assistant",
    page_icon="🎯",
    layout="wide",
    initial_sidebar_state="expanded",
)

st.title("🎯 AI Interview Assistant")

st.markdown(
    """
Upload your **Resume** and **Job Description**, then let AI:

- 📄 Build a knowledge base
- ❓ Generate interview questions
- 🎤 Conduct a mock interview
- ✅ Evaluate your answers
"""
)

# ==========================================================
# Initialize Session State
# ==========================================================

if "store" not in st.session_state:
    st.session_state["store"] = None

if "session" not in st.session_state:
    st.session_state["session"] = None

if "chat" not in st.session_state:
    st.session_state["chat"] = []

# ==========================================================
# Sidebar
# ==========================================================

with st.sidebar:

    st.header("⚙️ Knowledge Base")

    st.markdown(
        """
### Tech Stack

- Gemini 2.5 Flash
- LangChain
- FAISS
- Sentence Transformers
- Streamlit
"""
    )

    st.divider()

    resume_file = st.file_uploader(
        "Upload Resume",
        type=["pdf", "docx", "txt"],
    )

    jd_text = st.text_area(
        "Paste Job Description",
        height=220,
        placeholder="Paste the job description here...",
    )

    # ------------------------------------------------------

    if st.button(
        "🚀 Build Knowledge Base",
        use_container_width=True,
        type="primary",
    ):

        if resume_file is None:
            st.error("Please upload your resume.")
            st.stop()

        if not jd_text.strip():
            st.error("Please paste the job description.")
            st.stop()

        try:

            progress = st.progress(0)

            with tempfile.TemporaryDirectory() as tmp_dir:

                progress.progress(15)

                resume_path = Path(tmp_dir) / resume_file.name

                resume_path.write_bytes(
                    resume_file.getvalue()
                )

                progress.progress(35)

                with st.spinner("Reading documents..."):

                    documents = build_documents(
                        str(resume_path),
                        jd_text,
                        jd_is_file=False,
                    )

                progress.progress(60)

                with st.spinner("Creating embeddings..."):

                    vector_store = build_vectorstore(
                        documents
                    )

                progress.progress(85)

                save_vectorstore(vector_store)

                st.session_state["store"] = vector_store

                progress.progress(100)

            st.success("Knowledge Base Created Successfully!")

            st.info(
                f"""
Resume : **{resume_file.name}**

Document Chunks : **{len(documents)}**
"""
            )

        except Exception as e:

            st.exception(e)

    # ------------------------------------------------------

    st.divider()

    st.subheader("Saved Knowledge Base")

    if (
        st.session_state["store"] is None
        and vectorstore_exists()
    ):

        if st.button(
            "📂 Load Existing Index",
            use_container_width=True,
        ):

            try:

                st.session_state["store"] = load_vectorstore()

                st.success(
                    "Knowledge Base Loaded Successfully!"
                )

            except Exception as e:

                st.exception(e)

    # ------------------------------------------------------

    if st.button(
        "🗑 Clear Loaded Index",
        use_container_width=True,
    ):

        st.session_state["store"] = None

        st.session_state["session"] = None

        st.session_state["chat"] = []

        st.success("Session Cleared.")

# ==========================================================
# Stop if No Knowledge Base
# ==========================================================

if st.session_state["store"] is None:

    st.info(
        """
👈 Build a new knowledge base or load an existing one
from the sidebar to continue.
"""
    )

    st.stop()

# Active Vector Store
store = st.session_state["store"]

# ==========================================================
# Tabs
# ==========================================================

tab_questions, tab_mock, tab_feedback = st.tabs(
    [
        "📋 Interview Questions",
        "🎤 Mock Interview",
        "✅ Answer Evaluation",
    ]
)# ==========================================================
# TAB 1 : Interview Question Generator
# ==========================================================

with tab_questions:

    st.subheader("📋 Generate AI Interview Questions")

    num_questions = st.slider(
        "Number of Questions",
        min_value=3,
        max_value=15,
        value=8,
    )

    if st.button(
        "Generate Questions",
        use_container_width=True,
    ):

        try:

            with st.spinner("Generating interview questions..."):

                questions = generate_interview_questions(
                    store=store,
                    num_questions=num_questions,
                )

            st.success("Questions Generated Successfully!")

            st.markdown(questions)

        except Exception as e:

            st.exception(e)


# ==========================================================
# TAB 2 : Mock Interview
# ==========================================================

with tab_mock:

    st.subheader("🎤 AI Mock Interview")

    if st.session_state["session"] is None:

        if st.button(
            "Start Interview",
            type="primary",
            use_container_width=True,
        ):

            try:

                st.session_state["session"] = (
                    MockInterviewSession(store)
                )

                first_message = (
                    st.session_state["session"].start()
                )

                st.session_state["chat"] = [
                    ("assistant", first_message)
                ]

                st.rerun()

            except Exception as e:

                st.exception(e)

    else:

        # Display Chat

        for role, message in st.session_state["chat"]:

            with st.chat_message(role):

                st.markdown(message)

        # User Input

        user_message = st.chat_input(
            "Type your interview answer..."
        )

        if user_message:

            st.session_state["chat"].append(
                ("user", user_message)
            )

            try:

                reply = (
                    st.session_state["session"]
                    .respond(user_message)
                )

            except Exception as e:

                reply = f"❌ Error: {e}"

            st.session_state["chat"].append(
                ("assistant", reply)
            )

            st.rerun()

        col1, col2 = st.columns(2)

        with col1:

            if st.button(
                "Next Question",
                use_container_width=True,
            ):

                try:

                    next_question = (
                        st.session_state["session"]
                        .respond("")
                    )

                    st.session_state["chat"].append(
                        ("assistant", next_question)
                    )

                    st.rerun()

                except Exception as e:

                    st.exception(e)

        with col2:

            if st.button(
                "Reset Interview",
                use_container_width=True,
            ):

                st.session_state["session"] = None

                st.session_state["chat"] = []

                st.rerun()


# ==========================================================
# TAB 3 : Answer Evaluation
# ==========================================================

with tab_feedback:

    st.subheader("✅ Evaluate Your Interview Answer")

    question = st.text_input(
        "Interview Question"
    )

    answer = st.text_area(
        "Your Answer",
        height=220,
    )

    if st.button(
        "Evaluate Answer",
        type="primary",
        use_container_width=True,
    ):

        if not question.strip():

            st.warning(
                "Please enter an interview question."
            )

        elif not answer.strip():

            st.warning(
                "Please enter your answer."
            )

        else:

            try:

                with st.spinner(
                    "Analyzing your answer..."
                ):

                    feedback = evaluate_answer(
                        store=store,
                        question=question,
                        answer=answer,
                    )

                st.success(
                    "Evaluation Completed!"
                )

                st.markdown(feedback)

            except Exception as e:

                st.exception(e)


# ==========================================================
# Footer
# ==========================================================

st.divider()

col1, col2, col3 = st.columns(3)

with col1:
    st.metric("LLM", settings.GEMINI_MODEL)

with col2:
    st.metric(
        "Embedding Model",
        settings.EMBEDDING_MODEL.split("/")[-1],
    )

with col3:
    st.metric(
        "Retriever Top-K",
        settings.RETRIEVER_TOP_K,
    )

st.markdown("---")

st.caption(
    """
🎯 **AI Interview Assistant**

Built with:

- Google Gemini
- LangChain
- FAISS
- Sentence Transformers
- Streamlit

Developed as an end-to-end RAG application for interview preparation.
"""
)