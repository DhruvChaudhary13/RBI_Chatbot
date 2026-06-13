"""
RBI CHATBOT EVALUATION - ENHANCED STRICT ANSWER MATCHING
Testing against predefined exact answers for NBFC questions
"""

import time
import re
from typing import Dict, List
from langsmith import Client
from langsmith.evaluation import evaluate
from langsmith.schemas import Run, Example
from sentence_transformers import SentenceTransformer, util
from chatbot import RBI_Chatbot


class RBI_Chatbot_Strict_Evaluator:
    def __init__(self):
        print("🔧 Initializing RBI Chatbot Evaluator - Enhanced Strict Answer Matching...")
        self.chatbot = RBI_Chatbot()
        self.client = Client()
        self.dataset_name = "rbi-nbfc-enhanced-strict-evaluation"

        try:
            self.similarity_model = SentenceTransformer('all-MiniLM-L6-v2')
            print("✅ Semantic similarity model loaded successfully")
        except Exception as e:
            print(f"❌ Error loading similarity model: {e}")
            self.similarity_model = None

    def strict_semantic_match(self, chatbot_answer: str, expected_answer: str) -> Dict:
        """Enhanced strict semantic matching with paraphrase handling"""
        chatbot_lower = chatbot_answer.lower()
        key_phrases = self.extract_key_phrases(expected_answer)

        matched_phrases = 0
        missing_critical = []

        for phrase in key_phrases:
            phrase_lower = phrase.lower()
            if phrase_lower in chatbot_lower:
                matched_phrases += 1
            else:
                # Semantic similarity fallback
                if self.semantic_similarity(phrase, chatbot_answer) > 0.5:
                    matched_phrases += 1
                else:
                    missing_critical.append(phrase)

        coverage_score = matched_phrases / len(key_phrases) if key_phrases else 0.0
        overall_similarity = self.semantic_similarity(chatbot_answer, expected_answer)

        # Slightly more weight on overall similarity to catch paraphrases
        final_score = (coverage_score * 0.6) + (overall_similarity * 0.4)

        return {
            "score": final_score,
            "coverage": coverage_score,
            "overall_similarity": overall_similarity,
            "matched_phrases": matched_phrases,
            "total_phrases": len(key_phrases),
            "missing_phrases": missing_critical
        }

    def extract_key_phrases(self, text: str) -> List[str]:
        """Extract meaningful key phrases from expected answer"""
        phrases = []
        sentences = re.split(r'[.!?]', text)
        for sentence in sentences:
            sentence = sentence.strip()
            if len(sentence) < 10:
                continue
            # Remove common prefixes and extra spaces
            clean_sentence = re.sub(r'^(The|It|Further|As part of|If|Where)', '', sentence).strip()
            if len(clean_sentence) > 10:  # Lowered from 15
                phrases.append(clean_sentence)
        return phrases

    def semantic_similarity(self, text1: str, text2: str) -> float:
        """Compute semantic similarity using SentenceTransformer embeddings"""
        if not self.similarity_model:
            return 0.3
        try:
            emb1 = self.similarity_model.encode(text1, convert_to_tensor=True)
            emb2 = self.similarity_model.encode(text2, convert_to_tensor=True)
            similarity = util.cos_sim(emb1, emb2).item()
            return max(0.0, min(1.0, similarity))
        except:
            return 0.3

    def predict_function(self, input_dict: Dict) -> Dict:
        question = input_dict["question"]
        print(f"\n🤔 QUESTION: {question}")
        start_time = time.time()
        response = self.chatbot.ask_question(question)
        response_time = time.time() - start_time
        print(f"✅ ANSWER: {response['answer'][:150]}...")
        return {
            "answer": response["answer"],
            "sources_count": response.get("sources_count", 0),
            "response_time": response_time,
            "answer_length": len(response["answer"]),
            "word_count": len(response["answer"].split())
        }

    def create_strict_dataset(self):
        """Create dataset with 5 NBFC questions and predefined answers"""
        test_cases = [
            {
                "inputs": {"question": "What are the powers of the Reserve Bank with regard to Non-Bank Financial Companies that meet the Principal Business Criteria or 50-50 criteria?"},
                "outputs": {"expected_answer": "The Reserve Bank has been empowered under the RBI Act 1934 to register, determine policy, issue directions, inspect, regulate, supervise and exercise surveillance over NBFCs that fulfil the principal business criteria or 50-50 criteria of principal business. The Reserve Bank can penalize NBFCs for violating the provisions of the RBI Act or the directions or orders issued by the Reserve Bank under RBI Act. The penal action may also include cancellation of the Certificate of Registration issued to the NBFC."}
            },
            {
                "inputs": {"question": "What action can be taken against persons/financial companies making false claim of being regulated by the Reserve Bank?"},
                "outputs": {"expected_answer": "It is illegal for any person/ entity/ financial company to make a false claim of being regulated by the Reserve Bank to mislead the public to collect deposits and is liable for penal action under the Law. Information in this regard may be forwarded to the nearest office of the Reserve Bank and the Police."}
            },
            {
                "inputs": {"question": "What action is taken if financial companies which are lending or making investments as their principal business do not obtain a Certificate of Registration from the Reserve Bank?"},
                "outputs": {"expected_answer": "If companies that are required to be registered with the Reserve Bank as NBFCs, are found to be conducting non-banking financial activity, such as, lending, investment or deposit acceptance as their principal business, without obtaining Certificate of Registration from the Reserve Bank, the same would be treated as contravention of the provisions of the RBI Act, 1934 and would invite penal action viz., penalty or fine or even prosecution in a Court of Law. If members of public come across any entity which undertakes non-banking financial activity but does not figure in the list of authorized NBFCs on the Reserve Bank’s website, they should inform the nearest Regional Office of the Reserve Bank, for appropriate action to be taken for contravention of the provisions of the RBI Act, 1934."}
            },
            {
                "inputs": {"question": "Where can one find list of Registered NBFCs and instructions issued to NBFCs?"},
                "outputs": {"expected_answer": "The list of registered NBFCs is available on the web site of Reserve Bank (www.rbi.org.in) under ‘Regulation → Non-Banking’. Further, the instructions issued to NBFCs from time to time through circulars and/ or master directions are hosted on the Reserve Bank’s website under ‘Notifications’, and some instructions are issued through Official Gazette notifications and press releases as well."}
            },
            {
                "inputs": {"question": "What are the regulations prescribed by the Reserve Bank for NBFCs?"},
                "outputs": {"expected_answer": "As part of regulatory framework prescribed by the Reserve Bank for NBFCs, the Reserve Bank prescribes prudential regulations viz., capital adequacy/ leverage, provisioning, corporate governance framework, etc.; conduct of business regulations viz., KYC/ AML regulations, fair practices code, etc.; and other miscellaneous regulations to ensure that NBFCs are financially sound and follow transparency in their operations. The regulations for NBFCs are contained in various master directions and notifications/ circulars issued from time to time, and are available on the website of the Reserve Bank (www.rbi.org.in) under ‘notifications’."}
            }
        ]

        try:
            dataset = self.client.create_dataset(
                dataset_name=self.dataset_name,
                description="Enhanced strict NBFC questions with predefined exact answers"
            )
            for tc in test_cases:
                self.client.create_example(
                    dataset_id=dataset.id,
                    inputs=tc["inputs"],
                    outputs=tc["outputs"]
                )
            print(f"✅ Dataset created with {len(test_cases)} questions")
            return dataset
        except Exception as e:
            print(f"❌ Dataset creation error: {e}")
            return None

    def run_evaluation(self):
        """Run enhanced strict evaluation"""
        print("🚀 Starting ENHANCED STRICT ANSWER EVALUATION...")
        dataset = self.create_strict_dataset()
        if not dataset:
            print("❌ Dataset not created")
            return

        results = evaluate(
            self.predict_function,
            data=dataset.name,
            evaluators=[self.evaluate_accuracy],
            max_concurrency=1,
            num_repetitions=1
        )
        print("✅ Evaluation complete!")
        return results

    def evaluate_accuracy(self, run: Run, example: Example):
        """Evaluator function for Langsmith"""
        chatbot_answer = run.outputs.get("answer", "")
        expected_answer = example.outputs.get("expected_answer", "")
        match_result = self.strict_semantic_match(chatbot_answer, expected_answer)
        return {"key": "strict_accuracy", "score": match_result["score"]}


def main():
    evaluator = RBI_Chatbot_Strict_Evaluator()
    evaluator.run_evaluation()


if __name__ == "__main__":
    main()
