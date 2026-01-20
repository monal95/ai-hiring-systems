"""
Enhanced Adaptive Interview System with Groq AI
- Generates 20 behavioral + 15 technical questions per session
- Supports 3 difficulty levels (Easy, Medium, Hard)
- Adaptive questions based on candidate answers
- Strict code evaluation
"""

import json
from config.groq_config import call_groq
from config.judge0_config import execute_code, run_test_cases
from datetime import datetime

class EnhancedInterviewManager:
    """Manages comprehensive interview with multiple questions and difficulty levels"""
    
    def __init__(self):
        self.interview_sessions = {}
        self.response_history = {}
    
    def _parse_json_robustly(self, response: str) -> dict:
        """Robustly parse JSON from Groq response"""
        if not response:
            return None
            
        try:
            # Try direct parse
            return json.loads(response.strip())
        except json.JSONDecodeError:
            try:
                # Try cleaning markdown blocks
                cleaned = response.strip()
                if "```json" in cleaned:
                    cleaned = cleaned.split("```json", 1)[1]
                    if "```" in cleaned:
                        cleaned = cleaned.rsplit("```", 1)[0]
                elif "```" in cleaned:
                    cleaned = cleaned.split("```", 1)[1]
                    if "```" in cleaned:
                        cleaned = cleaned.rsplit("```", 1)[0]
                return json.loads(cleaned.strip())
            except:
                # Try regex extraction
                import re
                json_match = re.search(r'\{.*\}', response, re.DOTALL)
                if json_match:
                    try:
                        return json.loads(json_match.group())
                    except:
                        pass
        return None
    
    def generate_full_interview_questions(self, job_title: str, candidate_skills: list) -> dict:
        """
        Generate complete interview with 20 behavioral + 15 technical questions
        
        Args:
            job_title: Job position
            candidate_skills: List of candidate skills
        
        Returns:
            Dictionary with all interview questions organized by type and difficulty
        """
        print(f"[EnhancedInterview] ✅ Starting interview generation for {job_title}")
        print(f"[EnhancedInterview] Skills: {candidate_skills}")
        
        try:
            # Generate behavioral questions (20 total)
            print(f"[EnhancedInterview] Generating behavioral questions...")
            behavioral_questions = self._generate_behavioral_questions_full(job_title, candidate_skills)
            behavioral_count = len(behavioral_questions.get('questions', []))
            print(f"[EnhancedInterview] ✅ Behavioral questions generated: {behavioral_count} total")
            
            # Generate technical questions (15 total)
            print(f"[EnhancedInterview] Generating technical questions...")
            technical_questions = self._generate_technical_questions_full(job_title, candidate_skills)
            technical_count = len(technical_questions.get('questions', []))
            print(f"[EnhancedInterview] ✅ Technical questions generated: {technical_count} total")
            
            # Generate coding question (1 total)
            print(f"[EnhancedInterview] Generating coding question...")
            coding_questions = self._generate_coding_questions_full(job_title, candidate_skills)
            print(f"[EnhancedInterview] ✅ Coding question generated")
            
            return {
                'success': True,
                'interview': {
                    'behavioral': behavioral_questions,  # 20 questions
                    'technical': technical_questions,    # 15 questions
                    'coding': coding_questions,          # 1 question
                    'total_questions': 36,
                    'generated_at': datetime.now().isoformat()
                }
            }
        except Exception as e:
            print(f"[EnhancedInterview] ❌ ERROR: {e}")
            import traceback
            traceback.print_exc()
            print(f"[EnhancedInterview] Using fallback questions")
            return self._get_fallback_full_interview()
    
    def _generate_behavioral_questions_full(self, job_title: str, candidate_skills: list) -> dict:
        """Generate 20 behavioral questions with 3 difficulty levels (Easy: 8, Medium: 7, Hard: 5)"""
        
        system_prompt = """You are an expert HR interviewer. Generate EXACTLY 20 behavioral interview questions 
organized by difficulty level. Return a JSON object with three arrays: "easy" (8 questions), "medium" (7 questions), "hard" (5 questions).

For each question include: question, what_to_assess, expected_competencies

CRITICAL: Generate COMPLETELY UNIQUE and DIVERSE questions. Vary scenarios, contexts, and competencies being tested.
Use creative scenarios and avoid generic/standard interview questions.

Return ONLY valid JSON, no other text."""
        
        user_prompt = f"""Generate 20 UNIQUE behavioral interview questions for a {job_title} position.
Candidate skills: {', '.join(candidate_skills) if candidate_skills else 'Not specified'}

IMPORTANT: Diversify questions across: teamwork dynamics, leadership styles, communication methods, adaptability scenarios, 
ethical dilemmas, resilience tests, learning ability, conflict resolution, innovation thinking, mentoring, failure recovery.

Create:
- 8 EASY questions (basic soft skills, teamwork, communication)
- 7 MEDIUM questions (conflict resolution, decision making, leadership)
- 5 HARD questions (complex scenarios, ethical dilemmas, strategic thinking)

Each question must be UNIQUE and different from standard interview pools.

Return as JSON with keys: easy, medium, hard"""
        
        try:
            response = call_groq(user_prompt, system_prompt, max_tokens=3000)
            return self._parse_behavioral_response(response, job_title)
        except Exception as e:
            print(f"[EnhancedInterview] Error generating behavioral: {e}")
            return self._fallback_behavioral_questions()
    
    def _generate_technical_questions_full(self, job_title: str, candidate_skills: list) -> dict:
        """Generate 15 technical questions with 3 difficulty levels (Easy: 6, Medium: 5, Hard: 4)"""
        
        system_prompt = """You are an expert technical interviewer. Generate EXACTLY 15 technical interview questions 
organized by difficulty level. Return a JSON object with three arrays: "easy" (6 questions), "medium" (5 questions), "hard" (4 questions).

For each question include: question, skills_required, difficulty_explanation

CRITICAL: Generate COMPLETELY UNIQUE and DIVERSE questions. Vary topics, scenarios, and approaches.
Use practical scenarios and avoid standard/generic interview questions.

Return ONLY valid JSON, no other text."""
        
        user_prompt = f"""Generate 15 UNIQUE technical interview questions for a {job_title} position.
Candidate technical skills: {', '.join(candidate_skills) if candidate_skills else 'Not specified'}

IMPORTANT: Diversify questions across: system design, code optimization, debugging, architecture decisions,
real-world problems, performance tuning, scalability, trade-offs, design patterns, practical scenarios.

Cover different aspects of: {', '.join(candidate_skills) if candidate_skills else 'the required technical skills'}

Create:
- 6 EASY questions (basic concepts, definitions, fundamentals)
- 5 MEDIUM questions (implementation, problem-solving, design patterns)
- 4 HARD questions (architecture, optimization, complex scenarios)

Each question must be UNIQUE and different from standard interview pools.

Return as JSON with keys: easy, medium, hard"""
        
        try:
            response = call_groq(user_prompt, system_prompt, max_tokens=3000)
            return self._parse_technical_response(response, job_title)
        except Exception as e:
            print(f"[EnhancedInterview] Error generating technical: {e}")
            return self._fallback_technical_questions()
    
    def _generate_coding_questions_full(self, job_title: str, candidate_skills: list) -> dict:
        """Generate 1 coding question with test cases"""
        
        system_prompt = """You are an expert coding interview expert. Generate a UNIQUE coding problem 
with: problem statement, constraints, examples, test cases, and solution approach.

Return a JSON object with:
- problem: The coding problem statement
- constraints: List of constraints
- examples: List of input/output examples
- difficulty: 'medium' or 'hard'
- languages_supported: List of languages (python, javascript, java, cpp, go, rust)
- test_cases: List of {input, expected_output}
- hints: List of hints
- estimated_time_minutes: Time estimate

CRITICAL: Generate UNIQUE and INTERESTING problems. Avoid standard LeetCode problems.
Make it relevant to the {job_title} role and test real-world skills.

Return ONLY valid JSON."""
        
        user_prompt = f"""Generate 1 UNIQUE coding problem for a {job_title} position.
Candidate skills: {', '.join(candidate_skills) if candidate_skills else 'Not specified'}

IMPORTANT REQUIREMENTS:
- Problem must be UNIQUE and INTERESTING (not standard problems)
- Difficulty: Medium to Hard
- Must be solvable in multiple languages
- Test candidate's practical skills for {job_title}
- Include: realistic scenarios, edge cases, performance considerations
- Provide clear examples and test cases

Make it challenging but fair for the skill level."""
        
        try:
            response = call_groq(user_prompt, system_prompt, max_tokens=3000)
            return self._parse_coding_response(response)
        except Exception as e:
            print(f"[EnhancedInterview] Error generating coding: {e}")
            return self._fallback_coding_questions()
    
    def _parse_coding_response(self, response: str) -> dict:
        """Parse coding question response from Groq"""
        try:
            import re
            # Extract JSON from response
            json_match = re.search(r'\{.*\}', response, re.DOTALL)
            if json_match:
                raw = json.loads(json_match.group())
                # Normalize fields for frontend
                problem_data = {
                    'id': raw.get('id', 'CODE1'),
                    'title': raw.get('title') or raw.get('problem', 'Coding Challenge'),
                    'description': raw.get('problem') or raw.get('description', ''),
                    'difficulty': (raw.get('difficulty') or 'MEDIUM').upper(),
                    'language': raw.get('language', 'python'),
                    'constraints': raw.get('constraints', []),
                    'examples': raw.get('examples', []),
                    'test_cases': raw.get('test_cases', []),
                    'hints': raw.get('hints', []),
                    'estimated_time_minutes': raw.get('estimated_time_minutes', 45),
                    'languages_supported': raw.get('languages_supported', ['python', 'javascript', 'java', 'cpp', 'go', 'rust']),
                    'type': 'coding'
                }
                return {'questions': [problem_data]}
        except Exception as e:
            print(f"[EnhancedInterview] Error parsing coding response: {e}")
        
        return self._fallback_coding_questions()
    
    def generate_adaptive_follow_up(self, question: str, candidate_response: str, 
                                   question_type: str = 'behavioral') -> dict:
        """
        Generate follow-up question based on candidate's response
        
        Args:
            question: Original question asked
            candidate_response: Candidate's answer
            question_type: 'behavioral' or 'technical'
        
        Returns:
            Follow-up question and assessment
        """
        print(f"[EnhancedInterview] Generating adaptive follow-up")
        
        system_prompt = f"""You are an expert {question_type} interviewer. Based on the candidate's response, 
generate a probing follow-up question that:
1. Explores deeper understanding
2. Challenges their assumptions
3. Uncovers gaps in knowledge

Return JSON with:
- follow_up_question: The next question
- explores: What aspect this explores
- assesses: Key competencies being tested
- difficulty_level: Estimated difficulty (1-5)"""
        
        user_prompt = f"""Original {question_type} question:
"{question}"

Candidate response:
"{candidate_response}"

Generate a follow-up question that probes deeper."""
        
        try:
            response = call_groq(user_prompt, system_prompt, max_tokens=1000)
            return self._parse_follow_up(response)
        except Exception as e:
            print(f"[EnhancedInterview] Error: {e}")
            return {'follow_up_question': 'Can you elaborate more on that?'}
    
    def evaluate_code_strictly(self, code: str, problem_type: str = 'twosum', 
                               language: str = 'python', test_cases: list = None) -> dict:
        """
        Strictly evaluate submitted code using Judge0 and AI
        
        Args:
            code: Submitted code
            problem_type: Type/Name of coding problem
            language: Programming language
            test_cases: Optional list of test cases to run
        
        Returns:
            Evaluation with execution results and AI analysis
        """
        print(f"[EnhancedInterview] Evaluating code strictly for {problem_type} in {language}")
        
        execution_results = []
        if test_cases:
            print(f"[EnhancedInterview] Running {len(test_cases)} test cases via Judge0")
            execution_results = run_test_cases(code, language, test_cases)
        else:
            print(f"[EnhancedInterview] No test cases provided, performing basic execution check")
            # Try a basic run if no test cases (just to check for syntax errors)
            execution_results = [execute_code(code, language)]

        # Consolidate execution results for AI
        passed_count = sum(1 for r in execution_results if r.get('passed', False))
        total_count = len(execution_results)
        
        execution_summary = {
            "passed_count": passed_count,
            "total_count": total_count,
            "results": execution_results[:5] # Limit results for prompt
        }

        system_prompt = """You are an expert code reviewer and technical interviewer. 
Analyze the candidate's code AND its execution results strictly.

STRICT EVALUATION CRITERA:
1. Functionality: Did it pass ACTUAL test cases? (Wait for execution results)
2. Efficiency: Is the time complexity O(n)? O(n log n)? O(n^2)? (Optimal is preferred)
3. Quality: Is the code clean, readable, and following idiomatic patterns?
4. Resilience: Are edge cases (null, empty, large inputs) handled?

Return JSON with:
- passes_all_tests: Boolean
- correctness_score: 0-100 (Be strict - if it fails tests, score < 50)
- execution_results_summary: String summary
- time_complexity: e.g., "O(n)"
- space_complexity: e.g., "O(1)"
- code_quality_score: 0-100
- issues_found: Array of strings
- overall_score: 0-100
- verdict: "PASS" (score >= 75) or "FAIL"
- feedback: Detailed expert feedback for the candidate"""
        
        user_prompt = f"""Evaluate this code for problem: {problem_type}
Language: {language}

CODE:
{code}

EXECUTION RESULTS:
{json.dumps(execution_summary, indent=2)}

Please provide a STRICT evaluation based on both the code logic and the actual test results."""
        
        try:
            response = call_groq(user_prompt, system_prompt, max_tokens=1500)
            ai_eval = self._parse_code_evaluation(response)
            
            # Combine with raw execution data
            ai_eval['test_results'] = execution_results
            return ai_eval
            
        except Exception as e:
            print(f"[EnhancedInterview] Error during AI evaluation: {e}")
            return {
                'passes_all_tests': passed_count == total_count if total_count > 0 else False,
                'correctness_score': (passed_count/total_count)*100 if total_count > 0 else 0,
                'overall_score': (passed_count/total_count)*100 if total_count > 0 else 0,
                'test_results': execution_results,
                'verdict': 'FAIL' if passed_count < total_count else 'PASS',
                'feedback': f'Execution completed with {passed_count}/{total_count} passing tests.'
            }
    
    def assess_phase_comprehensive(self, responses: list, question_type: str, 
                                  difficulty_distribution: dict) -> dict:
        """
        Comprehensive assessment of phase responses
        
        Args:
            responses: List of response objects with questions and answers
            question_type: 'behavioral' or 'technical'
            difficulty_distribution: Dict with easy/medium/hard counts
        
        Returns:
            Comprehensive assessment with scoring
        """
        print(f"[EnhancedInterview] Comprehensive assessment for {question_type}")
        
        system_prompt = f"""You are an expert interview assessor. Analyze the candidate's {question_type} responses comprehensively.

Evaluate:
1. Each response quality (1-10 scale)
2. Competencies demonstrated
3. Red flags or concerns
4. Overall readiness
5. Compared to difficulty levels asked

Return JSON with:
- response_scores: Object with score for each response (1-10)
- competencies_demonstrated: Array
- competencies_lacking: Array
- red_flags: Array (if any)
- strengths: Array
- improvement_areas: Array
- overall_phase_score: 0-100 (weighted by difficulty)
- phase_verdict: "STRONG PASS" | "PASS" | "BORDERLINE" | "FAIL"
- ready_for_next_phase: Boolean
- detailed_feedback: String"""
        
        responses_text = "\n\n".join([
            f"Q: {r.get('question', 'N/A')}\nA: {r.get('response', 'No answer')}"
            for r in responses[:10]  # First 10 responses
        ])
        
        user_prompt = f"""Assess these {question_type} interview responses:

{responses_text}

Evaluate fairly but strictly. Consider that easy questions should get higher scores, 
medium questions should show good understanding, hard questions test advanced knowledge."""
        
        try:
            response = call_groq(user_prompt, system_prompt, max_tokens=2000)
            return self._parse_assessment(response)
        except Exception as e:
            print(f"[EnhancedInterview] Error assessing: {e}")
            return self._default_assessment()
    
    # Parsing methods
    
    def _parse_behavioral_response(self, response: str, job_title: str) -> dict:
        """Parse behavioral questions response"""
        try:
            data = self._parse_json_robustly(response)
            if data:
                # Flatten to single array with difficulty markers
                questions = []
                question_counter = 1
                
                # Handle both {easy: [], ...} and {questions: []} formats
                if 'questions' in data and isinstance(data['questions'], list):
                    source_qs = data['questions']
                    for q in source_qs:
                        questions.append({
                            'id': f'B{question_counter}',
                            'question': q.get('question') if isinstance(q, dict) else q,
                            'difficulty': str(q.get('difficulty', 'MEDIUM')).upper(),
                            'type': 'behavioral'
                        })
                        question_counter += 1
                else:
                    for diff, qs in data.items():
                        if isinstance(qs, list):
                            for i, q in enumerate(qs):
                                questions.append({
                                    'id': f'B{question_counter}',
                                    'question': q.get('question') if isinstance(q, dict) else q,
                                    'difficulty': str(diff).upper() if isinstance(diff, str) else 'MEDIUM',
                                    'type': 'behavioral'
                                })
                                question_counter += 1
                
                if questions:
                    return {'success': True, 'questions': questions}
        except Exception as e:
            print(f"[EnhancedInterview] Error parsing behavioral: {e}")
        
        return self._fallback_behavioral_questions()
    
    def _parse_technical_response(self, response: str, job_title: str) -> dict:
        """Parse technical questions response"""
        try:
            data = self._parse_json_robustly(response)
            if data:
                questions = []
                question_counter = 1
                
                if 'questions' in data and isinstance(data['questions'], list):
                    source_qs = data['questions']
                    for q in source_qs:
                        questions.append({
                            'id': f'T{question_counter}',
                            'question': q.get('question') if isinstance(q, dict) else q,
                            'difficulty': str(q.get('difficulty', 'MEDIUM')).upper(),
                            'type': 'technical'
                        })
                        question_counter += 1
                else:
                    for diff, qs in data.items():
                        if isinstance(qs, list):
                            for i, q in enumerate(qs):
                                questions.append({
                                    'id': f'T{question_counter}',
                                    'question': q.get('question') if isinstance(q, dict) else q,
                                    'difficulty': str(diff).upper() if isinstance(diff, str) else 'MEDIUM',
                                    'type': 'technical'
                                })
                                question_counter += 1
                                
                if questions:
                    return {'success': True, 'questions': questions}
        except Exception as e:
            print(f"[EnhancedInterview] Error parsing technical: {e}")

        return self._fallback_technical_questions()
    def _parse_follow_up(self, response: str) -> dict:
        """Parse follow-up question"""
        try:
            import re
            json_match = re.search(r'\{.*\}', response, re.DOTALL)
            if json_match:
                return json.loads(json_match.group())
        except:
            pass
        return {'follow_up_question': 'Can you provide more details?'}
    
    def _parse_code_evaluation(self, response: str) -> dict:
        """Parse code evaluation"""
        try:
            import re
            json_match = re.search(r'\{.*\}', response, re.DOTALL)
            if json_match:
                return json.loads(json_match.group())
        except:
            pass
        return {
            'passes_all_tests': False,
            'overall_score': 0,
            'verdict': 'FAIL'
        }
    
    def _parse_assessment(self, response: str) -> dict:
        """Parse assessment response"""
        try:
            import re
            json_match = re.search(r'\{.*\}', response, re.DOTALL)
            if json_match:
                return json.loads(json_match.group())
        except:
            pass
        return self._default_assessment()
    
    # Fallback methods
    
    def _get_fallback_full_interview(self) -> dict:
        """Fallback interview"""
        return {
            'success': True,
            'interview': {
                'behavioral': self._fallback_behavioral_questions()['questions'][:20],
                'technical': self._fallback_technical_questions()['questions'][:15],
                'total_questions': 35
            }
        }
    
    def _fallback_behavioral_questions(self) -> dict:
        """Fallback behavioral questions"""
        return {
            'success': True,
            'questions': [
                {'id': 'B1', 'question': 'Tell us about a challenging project you worked on.', 'difficulty': 'EASY', 'type': 'behavioral'},
                {'id': 'B2', 'question': 'Describe a time you had to work with a difficult team member.', 'difficulty': 'EASY', 'type': 'behavioral'},
                {'id': 'B3', 'question': 'How do you handle conflicting priorities?', 'difficulty': 'MEDIUM', 'type': 'behavioral'},
                {'id': 'B4', 'question': 'Tell me about your biggest failure and what you learned.', 'difficulty': 'MEDIUM', 'type': 'behavioral'},
                {'id': 'B5', 'question': 'How do you approach learning new technologies?', 'difficulty': 'EASY', 'type': 'behavioral'},
                {'id': 'B6', 'question': 'Describe a situation where you had to convince others.', 'difficulty': 'MEDIUM', 'type': 'behavioral'},
                {'id': 'B7', 'question': 'How do you handle criticism?', 'difficulty': 'EASY', 'type': 'behavioral'},
                {'id': 'B8', 'question': 'Tell me about a time you showed leadership.', 'difficulty': 'HARD', 'type': 'behavioral'},
            ] * 3  # Repeat to get 20+ questions
        }
    
    def _fallback_technical_questions(self) -> dict:
        """Fallback technical questions"""
        return {
            'success': True,
            'questions': [
                {'id': 'T1', 'question': 'Explain the concept of data structures.', 'difficulty': 'EASY', 'type': 'technical'},
                {'id': 'T2', 'question': 'What is the difference between arrays and linked lists?', 'difficulty': 'EASY', 'type': 'technical'},
                {'id': 'T3', 'question': 'How would you optimize a slow database query?', 'difficulty': 'MEDIUM', 'type': 'technical'},
                {'id': 'T4', 'question': 'Explain the concept of microservices architecture.', 'difficulty': 'MEDIUM', 'type': 'technical'},
                {'id': 'T5', 'question': 'How do you handle database transactions?', 'difficulty': 'HARD', 'type': 'technical'},
                {'id': 'T6', 'question': 'Design a system that handles millions of requests.', 'difficulty': 'HARD', 'type': 'technical'},
            ] * 3  # Repeat to get 15+ questions
        }
    
    def _default_assessment(self) -> dict:
        """Default assessment"""
        return {
            'overall_phase_score': 50,
            'phase_verdict': 'BORDERLINE',
            'ready_for_next_phase': False,
            'strengths': ['Attempted questions'],
            'improvement_areas': ['More detail needed', 'Deeper understanding required'],
            'feedback': 'Assessment pending detailed review.'
        }
    
    def _fallback_coding_questions(self) -> dict:
        """Fallback coding question"""
        return {
            'medium': [
                {
                    'problem': 'Implement a function to find the longest substring without repeating characters in a given string.',
                    'constraints': [
                        '0 <= string length <= 10^5',
                        'Characters are alphanumeric and special characters',
                        'Return both the substring and its length'
                    ],
                    'examples': [
                        {'input': 'abcabcbb', 'output': 'abc (length: 3)'},
                        {'input': 'bbbbb', 'output': 'b (length: 1)'},
                        {'input': 'pwwkew', 'output': 'wke (length: 3)'}
                    ],
                    'difficulty': 'medium',
                    'languages_supported': ['python', 'javascript', 'java', 'cpp', 'go', 'rust'],
                    'test_cases': [
                        {'input': 'abcabcbb', 'expected_output': '{"substring": "abc", "length": 3}'},
                        {'input': 'bbbbb', 'expected_output': '{"substring": "b", "length": 1}'},
                        {'input': 'pwwkew', 'expected_output': '{"substring": "wke", "length": 3}'},
                        {'input': 'au', 'expected_output': '{"substring": "au", "length": 2}'},
                        {'input': 'dvdf', 'expected_output': '{"substring": "vdf", "length": 3}'}
                    ],
                    'hints': [
                        'Use sliding window technique',
                        'Maintain a set or map of characters in current window',
                        'Expand window by adding characters, shrink when duplicate found',
                        'Track maximum length and substring'
                    ],
                    'estimated_time_minutes': 25
                }
            ]
        }


# Create singleton instance
enhanced_interview_manager = EnhancedInterviewManager()
