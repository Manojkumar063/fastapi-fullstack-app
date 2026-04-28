import os
import tempfile
from fastapi import HTTPException, UploadFile
from langchain_google_genai import ChatGoogleGenerativeAI, GoogleGenerativeAIEmbeddings
from langchain_community.vectorstores import FAISS
from langchain_community.document_loaders import PyPDFLoader, TextLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain_core.runnables import RunnableLambda
from langchain_core.runnables.history import RunnableWithMessageHistory
from langchain_core.output_parsers import StrOutputParser
from langchain_core.chat_history import InMemoryChatMessageHistory

GEMINI_API_KEY = os.getenv("GEMINI_API_KEY", "")

# user_id -> {"vectorstore": FAISS, "chain": chain, "history": InMemoryChatMessageHistory}
_user_data: dict = {}

_prompt = ChatPromptTemplate.from_messages([
    ("system", "You are a helpful assistant. Use the following context to answer the question.\n\nContext:\n{context}"),
    MessagesPlaceholder(variable_name="chat_history"),
    ("human", "{question}"),
])


def _build_chain(vectorstore: FAISS):
    llm = ChatGoogleGenerativeAI(model="gemini-1.5-flash", google_api_key=GEMINI_API_KEY)
    retriever = vectorstore.as_retriever(search_kwargs={"k": 4})

    def retrieve_context(inputs):
        docs = retriever.invoke(inputs["question"])
        return {**inputs, "context": "\n\n".join(d.page_content for d in docs)}

    chain = RunnableLambda(retrieve_context) | _prompt | llm | StrOutputParser()
    return RunnableWithMessageHistory(
        chain,
        lambda session_id: _user_data[session_id]["history"],
        input_messages_key="question",
        history_messages_key="chat_history",
    )


async def ingest_document(file: UploadFile, user_id: str):
    if not GEMINI_API_KEY:
        raise HTTPException(status_code=500, detail="GEMINI_API_KEY not configured")
    suffix = os.path.splitext(file.filename)[1].lower()
    if suffix not in (".pdf", ".txt"):
        raise HTTPException(status_code=400, detail="Only .pdf and .txt files are supported")

    with tempfile.NamedTemporaryFile(delete=False, suffix=suffix) as tmp:
        tmp.write(await file.read())
        tmp_path = tmp.name
    try:
        loader = PyPDFLoader(tmp_path) if suffix == ".pdf" else TextLoader(tmp_path)
        docs = loader.load()
    finally:
        os.unlink(tmp_path)

    chunks = RecursiveCharacterTextSplitter(chunk_size=1000, chunk_overlap=150).split_documents(docs)
    embeddings = GoogleGenerativeAIEmbeddings(model="models/embedding-001", google_api_key=GEMINI_API_KEY)

    if user_id in _user_data:
        _user_data[user_id]["vectorstore"].add_documents(chunks)
    else:
        vectorstore = FAISS.from_documents(chunks, embeddings)
        _user_data[user_id] = {
            "vectorstore": vectorstore,
            "chain": _build_chain(vectorstore),
            "history": InMemoryChatMessageHistory(),
        }
    return {"message": f"Uploaded and indexed '{file.filename}' ({len(chunks)} chunks)"}


async def ask_question(question: str, user_id: str):
    if user_id not in _user_data:
        raise HTTPException(status_code=400, detail="No documents uploaded yet. Please upload a document first.")
    answer = await _user_data[user_id]["chain"].ainvoke(
        {"question": question},
        config={"configurable": {"session_id": user_id}},
    )
    return {"answer": answer}


def reset(user_id: str):
    _user_data.pop(user_id, None)
    return {"message": "Chat history and documents cleared"}
