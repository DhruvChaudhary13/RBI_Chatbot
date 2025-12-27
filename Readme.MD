## RBI Regulatory Chatbot 

A sophisticated AI-powered chatbot designed to provide accurate, concise answers to questions about RBI (Reserve Bank of India) regulations and NBFC (Non-Banking Financial Company) guidelines using advanced natural language processing and retrieval-augmented generation.


## Overview

The RBI Regulatory Chatbot is an intelligent question-answering system that processes complex RBI regulatory documents and provides precise, non-repetitive answers to user queries. It combines state-of-the-art NLP technologies with domain-specific optimizations for financial regulatory compliance.

## Directory Structure 

RBL_CHATBOT/
├── .venv/                          # Virtual environment
├── chatbot/                        # Main application package
│   ├── __pycache__/
│   ├── add_definitions.py          # Adds standard RBI definitions to vector store
│   ├── chatbot.py                  # Main chatbot class with question-answering logic
│   ├── config.py                   # Configuration settings and paths
│   ├── data_processing.py          # PDF processing and text chunking utilities
│   ├── langsmith_evaluation.py     # Enhanced evaluation system for answer quality
│   ├── main.py                     # Main entry point and system setup
│   ├── rbl_textbook.pdf            # RBI regulatory document (source data)
│   ├── setup_system.py             # System initialization scripts
│   └── vector_store.py             # FAISS vector database management
├── faiss_vector_db/                # Persistent vector storage
├── .env                            # Environment variables (API keys)
├── evaluation_question.txt         # Test questions for evaluation
└── requirements.txt                # Python dependencies



## For installing required files 
 Run: pip install -r requirements.txt



## To run the application
 Run : python chatbot/main.py 

## Choose from menu options:

                1 - Setup/Rebuild System (first time)

                2 - Chat Interface (start asking questions)

                3 - Test System

                4 - Add Definitions

                5 - Exit

## Ask RBI-related questions like:

        "What are the powers of RBI regarding NBFCs?"

        "What is Scale Based Regulatory Framework?"

        "What is deposit and public deposit?" 