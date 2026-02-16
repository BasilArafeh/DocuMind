"""
DocuMind Evaluation Suite
Measures accuracy and response time for RAG system
"""

import json
import time
import requests
from pathlib import Path
from typing import Dict, List
import statistics

# Configuration
API_BASE_URL = "https://basilarafeh-documind.hf.space"  # Change if testing locally
TEST_QUESTIONS_FILE = Path(__file__).parent / "test_questions.json"


def load_test_questions() -> List[Dict]:
    """Load test questions from JSON file"""
    with open(TEST_QUESTIONS_FILE, 'r', encoding='utf-8') as f:
        data = json.load(f)
    return data['test_cases']


def upload_documents(pdf_paths: List[str]) -> bool:
    """Upload test documents to DocuMind"""
    print(" Uploading test documents...")
    try:
        files = []
        for pdf_path in pdf_paths:
            if Path(pdf_path).exists():
                files.append(('files', open(pdf_path, 'rb')))
            else:
                print(f"  Warning: {pdf_path} not found")
        
        if not files:
            print(" No files to upload")
            return False
            
        response = requests.post(f"{API_BASE_URL}/upload", files=files)
        
        # Close file handles
        for _, file in files:
            file.close()
        
        if response.status_code == 200:
            print(f" Documents uploaded successfully")
            return True
        else:
            print(f" Upload failed: {response.status_code}")
            return False
    except Exception as e:
        print(f" Upload error: {e}")
        return False


def query_documind(question: str) -> Dict:
    """Query DocuMind and measure response time"""
    start_time = time.time()
    
    try:
        response = requests.post(
            f"{API_BASE_URL}/query",
            json={"query": question, "top_k": 3},
            timeout=30
        )
        
        elapsed_time = time.time() - start_time
        
        if response.status_code == 200:
            data = response.json()
            return {
                "success": True,
                "answer": data.get("answer", ""),
                "response_time": elapsed_time,
                "chunks_used": data.get("chunks_used", 0)
            }
        else:
            return {
                "success": False,
                "error": f"Status {response.status_code}",
                "response_time": elapsed_time
            }
    except Exception as e:
        elapsed_time = time.time() - start_time
        return {
            "success": False,
            "error": str(e),
            "response_time": elapsed_time
        }


def check_answer_quality(answer: str, expected_keywords: List[str]) -> bool:
    """Check if answer contains expected keywords (case-insensitive)"""
    answer_lower = answer.lower()
    
    # Count how many keywords are present
    matches = sum(1 for keyword in expected_keywords if keyword.lower() in answer_lower)
    
    # Consider correct if at least 40% of keywords are present
    threshold = max(1, len(expected_keywords) * 0.4)
    return matches >= threshold


def run_evaluation(pdf_paths: List[str]) -> Dict:
    """Run full evaluation suite"""
    print("=" * 60)
    print(" DocuMind Evaluation Suite")
    print("=" * 60)
    
    # Load test questions
    test_cases = load_test_questions()
    print(f"\nLoaded {len(test_cases)} test questions")
    
    # Upload documents
    if not upload_documents(pdf_paths):
        print(" Cannot proceed without documents")
        return None
    
    # Wait for indexing
    print("\n Waiting 5 seconds for indexing...")
    time.sleep(5)
    
    # Run evaluation
    print("\n🔍 Running evaluation...\n")
    
    results = []
    correct_count = 0
    response_times = []
    
    for i, test_case in enumerate(test_cases, 1):
        question = test_case['question']
        expected_keywords = test_case['expected_keywords']
        difficulty = test_case['difficulty']
        
        print(f"[{i}/{len(test_cases)}] Testing: {question[:50]}...")
        
        # Query DocuMind
        result = query_documind(question)
        
        if result['success']:
            answer = result['answer']
            response_time = result['response_time']
            response_times.append(response_time)
            
            # Check quality
            is_correct = check_answer_quality(answer, expected_keywords)
            
            if is_correct:
                correct_count += 1
                print(f"     Correct ({response_time:.2f}s)")
            else:
                print(f"     Incorrect ({response_time:.2f}s)")
            
            results.append({
                "question_id": test_case['id'],
                "question": question,
                "difficulty": difficulty,
                "answer": answer,
                "expected_keywords": expected_keywords,
                "correct": is_correct,
                "response_time": response_time
            })
        else:
            print(f"    ❌ Query failed: {result.get('error', 'Unknown')}")
            results.append({
                "question_id": test_case['id'],
                "question": question,
                "difficulty": difficulty,
                "correct": False,
                "error": result.get('error', 'Unknown')
            })
    
    # Calculate metrics
    accuracy = (correct_count / len(test_cases)) * 100
    avg_response_time = statistics.mean(response_times) if response_times else 0
    median_response_time = statistics.median(response_times) if response_times else 0
    
    # Print results
    print("\n" + "=" * 60)
    print(" EVALUATION RESULTS")
    print("=" * 60)
    print(f" Correct answers: {correct_count}/{len(test_cases)}")
    print(f" Accuracy: {accuracy:.1f}%")
    print(f"  Average response time: {avg_response_time:.2f}s")
    print(f"  Median response time: {median_response_time:.2f}s")
    print("=" * 60)
    
    # Breakdown by difficulty
    difficulties = {}
    for result in results:
        diff = result.get('difficulty', 'unknown')
        if diff not in difficulties:
            difficulties[diff] = {"correct": 0, "total": 0}
        difficulties[diff]['total'] += 1
        if result.get('correct', False):
            difficulties[diff]['correct'] += 1
    
    print("\n Breakdown by difficulty:")
    for diff, stats in difficulties.items():
        diff_accuracy = (stats['correct'] / stats['total']) * 100
        print(f"  {diff.capitalize()}: {stats['correct']}/{stats['total']} ({diff_accuracy:.1f}%)")
    
    # Save results
    output_file = Path(__file__).parent / "evaluation_results.json"
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump({
            "summary": {
                "total_questions": len(test_cases),
                "correct_answers": correct_count,
                "accuracy": f"{accuracy:.1f}%",
                "avg_response_time": f"{avg_response_time:.2f}s",
                "median_response_time": f"{median_response_time:.2f}s"
            },
            "breakdown_by_difficulty": difficulties,
            "detailed_results": results
        }, f, indent=2)
    
    print(f"\n Results saved to: {output_file}")
    
    return {
        "accuracy": accuracy,
        "avg_response_time": avg_response_time,
        "correct": correct_count,
        "total": len(test_cases)
    }


if __name__ == "__main__":
    # Specify your PDF paths here
    PDF_PATHS = [
        "path/to/2304.10557v6.pdf",  # Transformer intro paper
        "path/to/8.pdf"               # Jurafsky & Martin chapter
    ]
    
    print("\n IMPORTANT: Update PDF_PATHS in the script with actual file paths!")
    print("Example: PDF_PATHS = ['C:/Users/basel/Desktop/2304.10557v6.pdf']\n")
    
    # Uncomment to run with actual paths
    # run_evaluation(PDF_PATHS)
