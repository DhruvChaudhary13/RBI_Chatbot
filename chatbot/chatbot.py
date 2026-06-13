import os
import time
from langchain.chains import RetrievalQA
from langchain_groq import ChatGroq
from langchain.prompts import PromptTemplate
from vector_store import VectorStoreManager
from config import Config
from typing import Dict

class RBI_Chatbot:
    def __init__(self):
        self.vector_mgr = VectorStoreManager()
        
        try:
            self.llm = ChatGroq(
                groq_api_key=os.getenv("GROQ_API_KEY"),
                model_name="llama-3.1-8b-instant",
                temperature=0.1,
                max_tokens=800,  #  to prevent rambling
                top_p=0.9  #  to reduce repetition
            )
            print(f"Groq LLM initialized successfully with {self.llm.model_name}")
        except Exception as e:
            print(f"Error initializing Groq LLM: {e}")
            raise
        
        self.qa_chain = None
        self.setup_chain()
    
    def setup_chain(self):
        """Setup the retrieval QA chain"""
        print("Setting up QA chain...")
        
        prompt_template = """You are an expert RBI regulatory assistant. Provide clear, concise answers using the context.

                    CONTEXT FROM RBI DOCUMENTS:
                    {context}

                    QUESTION: {question}

                    ANSWER INSTRUCTIONS:
                    1. Provide direct, factual answers without repetition
                    2. Use exact RBI terminology from the context
                    3. Organize information logically without repeating points
                    4. Do NOT repeat the same information in different words
                    5. If listing powers, list each power only once
                    6. Keep answers comprehensive but concise
                    7. Do NOT start with "According to RBI" or similar phrases
                    8. Present information in a structured but natural way
                    9. Avoid redundant statements and looping
                    10. Stop when all key points are covered

                    ANSWER:"""
        
        PROMPT = PromptTemplate(template=prompt_template, input_variables=["context", "question"])
        retriever = self.vector_mgr.get_retriever()
        
        if retriever:
            try:
                self.qa_chain = RetrievalQA.from_chain_type(
                    llm=self.llm,
                    chain_type="stuff",
                    retriever=retriever,
                    chain_type_kwargs={"prompt": PROMPT},
                    return_source_documents=True
                )
                print("QA Chain setup successfully")
            except Exception as e:
                print(f"Error setting up QA chain: {e}")
                self.qa_chain = None
        else:
            print("Retriever not available - cannot setup QA chain")
            self.qa_chain = None
    
    def verify_context_relevance(self, question: str, source_docs: list) -> bool:
        """Verify if retrieved context is relevant to the question"""
        if not source_docs:
            return False
            
        question_lower = question.lower()
        all_content = " ".join([doc.page_content for doc in source_docs]).lower()
        
        key_terms_map = {
            "scale based regulatory framework": ["scale based", "sbr", "layers", "base", "middle", "upper", "top"],
            "credit rating": ["sebi", "credit rating", "agencies", "rating"],
            "money circulation": ["prize chits", "money circulation", "state governments"],
            "slcc": ["state level", "coordination", "committees", "slcc"],
            "deposit definition": ["section 45", "deposit", "public deposit", "defined"],
            "rbi powers": ["rbi act", "powers", "register", "penalize", "directions"]
        }
        
        for topic, terms in key_terms_map.items():
            if any(topic_word in question_lower for topic_word in topic.split()):
                found_terms = [term for term in terms if term in all_content]
                print(f"Context relevance - {len(found_terms)}/{len(terms)} key terms found")
                return len(found_terms) >= 2
        
        return True
    
    def remove_repetition(self, answer: str) -> str:
        """Remove repetitive content from the answer"""
        sentences = answer.split('. ')
        if len(sentences) <= 1:
            return answer
        
        # Remove duplicate sentences
        unique_sentences = []
        seen_sentences = set()
        
        for sentence in sentences:
            # Normalize sentence for comparison
            normalized = sentence.lower().strip()
            if normalized and normalized not in seen_sentences:
                seen_sentences.add(normalized)
                unique_sentences.append(sentence)
        
        # If still too repetitive, take only first 15 sentences
        if len(unique_sentences) > 15:
            unique_sentences = unique_sentences[:15]
        
        return '. '.join(unique_sentences) + ('.' if unique_sentences and not unique_sentences[-1].endswith('.') else '')
    
    def clean_answer(self, answer: str) -> str:
        """Clean the answer to remove unwanted phrases and repetition"""
        # Remove common introductory phrases
        phrases_to_remove = [
            "According to the RBI Master Direction,",
            "According to RBI Master Direction,",
            "Based on the provided context,",
            "Based on the context,",
            "The Reserve Bank of India has",
            "As per the RBI Master Direction,",
            "According to the RBI Act,"
        ]
        
        cleaned_answer = answer
        for phrase in phrases_to_remove:
            cleaned_answer = cleaned_answer.replace(phrase, "").strip()
        
        # Remove repetition
        cleaned_answer = self.remove_repetition(cleaned_answer)
        
        # Remove redundant "The RBI" at start if it appears
        if cleaned_answer.startswith("The RBI "):
            cleaned_answer = cleaned_answer[8:]
        elif cleaned_answer.startswith("RBI "):
            cleaned_answer = cleaned_answer[4:]
        
        # Ensure the answer starts with proper capitalization
        if cleaned_answer and len(cleaned_answer) > 0:
            cleaned_answer = cleaned_answer[0].upper() + cleaned_answer[1:]
        
        return cleaned_answer.strip()
    
    def ask_question(self, question: str) -> Dict:
        """Ask question to the chatbot and return structured answer"""
        try:
            if not self.qa_chain:
                return {
                    "answer": "Chatbot is still initializing. Please wait...",
                    "source_documents": [],
                    "sources_count": 0
                }
            
            start_time = time.time()
            result = self.qa_chain.invoke({"query": question})
            response_time = time.time() - start_time
            
            source_docs = result.get("source_documents", [])
            is_relevant = self.verify_context_relevance(question, source_docs)
            
            if not is_relevant:
                print("Note: Retrieved context may not be highly relevant")
            
            # Clean the answer
            cleaned_answer = self.clean_answer(result["result"])
            
            return {
                "answer": cleaned_answer,
                "source_documents": source_docs,
                "sources_count": len(source_docs),
                "response_time": response_time,
                "question": question,
                "context_relevant": is_relevant
            }
        except Exception as e:
            print(f"Error answering question: {e}")
            return {
                "answer": f"Error: {str(e)}",
                "source_documents": [],
                "sources_count": 0,
                "response_time": 0,
                "question": question,
                "context_relevant": False
            }
    
    def chat_interface(self):
        """Interactive chat interface"""
        if not self.qa_chain:
            print("Chatbot not ready. Please check initialization.")
            return
            
        print("=" * 60)
        print("RBI NBFC CHATBOT (CONCISE ANSWERS)")
        print("=" * 60)
        print("Powered by: llama-3.1-8b-instant (Groq)")
        print("Provides direct, non-repetitive RBI regulatory information")
        print("\nCommands: 'test' - run test | 'quit' - exit | Ask any RBI question")
        print("-" * 60)
        
        while True:
            question = input("\nYou: ").strip()
            
            if question.lower() in ['quit', 'exit', 'bye']:
                print("Thank you for using RBI Chatbot!")
                break
            elif question.lower() == 'test':
                self.test_key_questions()
                continue
            elif not question:
                continue
                
            response = self.ask_question(question)
            print(f"\nBot: {response['answer']}")
            
            if response.get('source_documents'):
                print(f"Based on {len(response['source_documents'])} relevant documents")
                if not response.get('context_relevant', True):
                    print("Note: Retrieved documents may not be highly relevant")
            
            if response.get('response_time'):
                print(f"Response time: {response['response_time']:.2f}s")
            print("-" * 60)
    
    def test_key_questions(self):
        """Test the chatbot with key RBI questions"""
        test_questions = [
            "What are the powers of the Reserve Bank with regard to Non-Bank Financial Companies?",
            "What is Scale Based Regulatory Framework for NBFCs?",
            "Who rates deposit taking NBFCs for acceptance of deposit?",
            "What is deposit and public deposit?"
        ]
        
        print("\nTESTING KEY RBI QUESTIONS")
        print("=" * 60)
        
        for i, question in enumerate(test_questions, 1):
            print(f"\n{i}. {question}")
            response = self.ask_question(question)
            answer = response["answer"]
            word_count = len(answer.split())
            
            # Check for repetition
            sentences = answer.split('. ')
            unique_sentences = len(set(sentence.lower().strip() for sentence in sentences if sentence.strip()))
            repetition_ratio = unique_sentences / len(sentences) if sentences else 1.0
            
            if repetition_ratio < 0.7:
                status = "REPETITIVE"
            elif "not available" in answer.lower():
                status = "MISSING"
            elif word_count > 200:
                status = "LONG"
            elif word_count > 80:
                status = "GOOD"
            else:
                status = "SHORT"
                
            print(f"Status: {status} | Words: {word_count} | Unique: {unique_sentences}/{len(sentences)} | Sources: {response['sources_count']}")
            print(f"Preview: {answer[:150]}...")