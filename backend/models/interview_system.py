"""
AI-Powered Interview System
Generates adaptive interviews, coding challenges, and AI-based evaluation
"""

import os
import uuid
import json
from datetime import datetime, timedelta
from config.groq_config import generate_job_description, suggest_skills, generate_interview_questions as groq_generate_interview_questions
import requests
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Interview configuration
INTERVIEW_DURATION_MINUTES = 45  # Total interview time
CODING_ROUND_DURATION_MINUTES = 20
TECHNICAL_QUESTIONS_COUNT = 15  # Generate 15 technical questions
BEHAVIORAL_QUESTIONS_COUNT = 20  # Generate 20 behavioral questions

# Use tunnel URL for external candidate access, fallback to localhost for local dev
FRONTEND_TUNNEL_URL = os.environ.get('FRONTEND_TUNNEL_URL', '')
FRONTEND_URL = FRONTEND_TUNNEL_URL if FRONTEND_TUNNEL_URL else os.environ.get('FRONTEND_URL', 'http://localhost:3000')
print(f"[InterviewSystem] Using FRONTEND_URL: {FRONTEND_URL}")

class InterviewGenerator:
    """Generates AI-powered interview questions based on job requirements"""
    
    def __init__(self):
        self.question_types = {
            'technical': 'Technical depth assessment',
            'coding': 'Practical coding ability',
            'behavioral': 'Soft skills and culture fit',
            'system_design': 'Architecture and design thinking'
        }
    
    def generate_interview_questions(self, job_requirements: dict, candidate_skills: list, candidate_id: str = None, job_id: str = None, job_title: str = "Software Engineer") -> dict:
        """
        Generate adaptive interview questions based on job requirements
        
        Args:
            job_requirements: Job must_have and good_to_have skills
            candidate_skills: Candidate's technical skills
            candidate_id: Candidate ID for uniqueness
            job_id: Job ID for context
        
        Returns:
            Dictionary with interview questions: 15 technical + 20 behavioral + 2 coding
        """
        print("[InterviewGenerator] Generating complete interview with Groq AI...")
        print(f"[InterviewGenerator] Job skills: {job_requirements.get('must_have', [])}")
        print(f"[InterviewGenerator] Candidate skills: {candidate_skills}")
        
        try:
            # Call Groq API to generate full interview (15+20+2 questions)
            groq_result = groq_generate_interview_questions(
                job_requirements, 
                candidate_skills,
                candidate_id=candidate_id,
                job_id=job_id,
                job_title=job_title
            )
            
            # Check if Groq API succeeded and actually generated questions
            if 'error' not in groq_result:
                technical = groq_result.get('technical', [])
                behavioral = groq_result.get('behavioral', [])
                coding = self._normalize_coding_challenges(groq_result.get('coding', []))
                groq_result['coding'] = coding
                
                # Check if we have at least some questions
                if len(technical) > 0 or len(behavioral) > 0 or len(coding) > 0:
                    print(f"[InterviewGenerator] ✅ Successfully generated {len(technical)} tech, {len(behavioral)} behavioral, {len(coding)} coding questions with Groq API")
                    
                    # Fill in missing parts if AI partially failed
                    must_have = job_requirements.get('must_have', [])
                    if not technical:
                        print("[InterviewGenerator] ⚠️ Tech questions empty, adding local fallback...")
                        groq_result['technical'] = self._generate_technical_questions(must_have, 15)
                    if not behavioral:
                        print("[InterviewGenerator] ⚠️ Behavioral questions empty, adding local fallback...")
                        groq_result['behavioral'] = self._generate_behavioral_questions(20)
                    if not coding:
                        print("[InterviewGenerator] ⚠️ Coding questions empty, adding local fallback...")
                        groq_result['coding'] = self._normalize_coding_challenges(
                            self._generate_coding_challenges(must_have, 2)
                        )
                        
                    return groq_result
                else:
                    print(f"[InterviewGenerator] Groq API returned 0 questions. Falling back...")
            else:
                print(f"[InterviewGenerator] Groq API failed: {groq_result.get('message', 'Unknown error')}")
                print("[InterviewGenerator] Falling back to structured question generation...")
        
        except Exception as e:
            print(f"[InterviewGenerator] Exception calling Groq: {e}")
            return {'error': str(e), 'message': 'System exception during AI generation'}
        
        # Fallback: Generate questions locally if Groq fails
        try:
            must_have = job_requirements.get('must_have', [])
            
            # Generate technical questions (15 total)
            technical_questions = self._generate_technical_questions(must_have, 15)
            
            # Generate behavioral questions (20 total)
            behavioral_questions = self._generate_behavioral_questions(20)
            
            # Generate coding challenges (2 total - medium and hard)
            coding_challenges = self._generate_coding_challenges(must_have, 2)
            coding_challenges = self._normalize_coding_challenges(coding_challenges)
            
            interview_questions = {
                'technical': technical_questions,
                'behavioral': behavioral_questions,
                'coding': coding_challenges,
                'total_questions': len(technical_questions) + len(behavioral_questions) + len(coding_challenges),
                'generated_at': datetime.now().isoformat(),
                'candidate_id': candidate_id,
                'job_id': job_id,
                'fallback': True
            }
            
            print(f"[InterviewGenerator] ⚠️ Generated {len(technical_questions)} technical + {len(behavioral_questions)} behavioral + {len(coding_challenges)} coding (fallback)")
            return interview_questions
            
        except Exception as e:
            print(f"[InterviewGenerator] Fallback Exception: {e}")
            return {'error': str(e)}
    
    def _generate_technical_questions(self, skills: list, count: int) -> list:
        """Generate technical questions based on required skills"""
        questions = []
        
        # Sample question templates
        question_templates = [
            f"Explain how you would design a {{skill}} solution for {{scenario}}",
            f"What are the key considerations when using {{skill}} in production?",
            f"Can you describe a complex problem you solved using {{skill}}?",
            f"How do you approach {{skill}} performance optimization?",
            f"What {{skill}} best practices do you follow in your projects?",
        ]
        
        scenarios = [
            "handling high traffic",
            "ensuring data consistency",
            "scaling horizontally",
            "real-time data processing",
            "security and authentication"
        ]
        
        for i in range(min(count, len(skills))):
            skill = skills[i % len(skills)]
            scenario = scenarios[i % len(scenarios)]
            
            template = question_templates[i % len(question_templates)]
            question_text = template.format(skill=skill, scenario=scenario)
            
            questions.append({
                'id': f'Q{i+1}',
                'type': 'technical',
                'skill': skill,
                'question': question_text,
                'time_limit_minutes': 5,
                'difficulty': 'medium'
            })
        
        return questions
    
    def _generate_behavioral_questions(self, count: int) -> list:
        """Generate behavioral questions"""
        behavioral_questions = [
            {'id': 'B1', 'question': 'Tell us about a time when you had to work with a difficult team member. How did you handle it?', 'type': 'behavioral', 'competency': 'teamwork', 'difficulty': 'easy'},
            {'id': 'B2', 'question': 'Describe a project failure. What did you learn and how would you approach it differently?', 'type': 'behavioral', 'competency': 'resilience', 'difficulty': 'medium'},
            {'id': 'B3', 'question': 'How do you stay updated with new technologies and industry trends?', 'type': 'behavioral', 'competency': 'continuous_learning', 'difficulty': 'easy'},
            {'id': 'B4', 'question': 'What interests you about this role and our company?', 'type': 'behavioral', 'competency': 'motivation', 'difficulty': 'easy'},
            {'id': 'B5', 'question': 'Tell me about a time you took initiative on a project without being asked.', 'type': 'behavioral', 'competency': 'initiative', 'difficulty': 'medium'},
            {'id': 'B6', 'question': 'How do you handle feedback and criticism from colleagues?', 'type': 'behavioral', 'competency': 'adaptability', 'difficulty': 'medium'},
            {'id': 'B7', 'question': 'Describe a situation where you had to make a difficult decision with incomplete information.', 'type': 'behavioral', 'competency': 'decision_making', 'difficulty': 'medium'},
            {'id': 'B8', 'question': 'Tell me about a time you mentored or helped a junior team member.', 'type': 'behavioral', 'competency': 'leadership', 'difficulty': 'hard'},
            {'id': 'B9', 'question': 'How do you prioritize when you have multiple competing deadlines?', 'type': 'behavioral', 'competency': 'time_management', 'difficulty': 'easy'},
            {'id': 'B10', 'question': 'Describe a complex technical problem you solved and your approach.', 'type': 'behavioral', 'competency': 'problem_solving', 'difficulty': 'hard'},
            {'id': 'B11', 'question': 'Tell me about a time you had to communicate complex ideas to non-technical stakeholders.', 'type': 'behavioral', 'competency': 'communication', 'difficulty': 'medium'},
            {'id': 'B12', 'question': 'How do you approach learning a new technology or framework?', 'type': 'behavioral', 'competency': 'learning', 'difficulty': 'easy'},
            {'id': 'B13', 'question': 'Describe a time when your solution was rejected and how you handled it.', 'type': 'behavioral', 'competency': 'resilience', 'difficulty': 'medium'},
            {'id': 'B14', 'question': 'Tell me about your experience working in an agile/fast-paced environment.', 'type': 'behavioral', 'competency': 'adaptability', 'difficulty': 'medium'},
            {'id': 'B15', 'question': 'How do you ensure code quality and prevent bugs in your projects?', 'type': 'behavioral', 'competency': 'quality_focus', 'difficulty': 'easy'},
            {'id': 'B16', 'question': 'Describe a conflict with a colleague and how you resolved it.', 'type': 'behavioral', 'competency': 'conflict_resolution', 'difficulty': 'hard'},
            {'id': 'B17', 'question': 'Tell me about your biggest professional achievement.', 'type': 'behavioral', 'competency': 'accomplishment', 'difficulty': 'medium'},
            {'id': 'B18', 'question': 'How do you stay motivated during long, challenging projects?', 'type': 'behavioral', 'competency': 'motivation', 'difficulty': 'easy'},
            {'id': 'B19', 'question': 'Describe a time you had to work with an unfamiliar technology or tool.', 'type': 'behavioral', 'competency': 'adaptability', 'difficulty': 'medium'},
            {'id': 'B20', 'question': 'Where do you see yourself in 5 years and how does this role fit into your career goals?', 'type': 'behavioral', 'competency': 'vision', 'difficulty': 'hard'},
        ]
        
        # Return requested count, cycling through if needed
        result = []
        for i in range(count):
            result.append(behavioral_questions[i % len(behavioral_questions)])
        return result
    
    def _generate_coding_challenges(self, skills: list, count: int) -> list:
        """Generate coding challenges"""
        coding_challenges = [
            {
                'id': 'CODE1',
                'title': 'Two Sum Problem',
                'description': 'Given an array of integers, find two numbers that add up to a target sum.',
                'difficulty': 'medium',
                'language': 'python',
                'time_limit_minutes': 20,
                'type': 'coding',
                'concepts': ['arrays', 'hash_tables']
            },
            {
                'id': 'CODE2',
                'title': 'Design Rate Limiter',
                'description': 'Design and implement a rate limiter that allows N requests per M seconds.',
                'difficulty': 'hard',
                'language': 'python',
                'time_limit_minutes': 25,
                'type': 'coding',
                'concepts': ['design', 'algorithms', 'data_structures']
            },
        ]
        
        return coding_challenges[:count]

    def _normalize_coding_challenges(self, coding_list: list) -> list:
        """Ensure coding challenges have examples, constraints, and test cases."""
        normalized = []
        if not coding_list:
            return normalized
        for idx, item in enumerate(coding_list):
            if not isinstance(item, dict):
                continue
            challenge = item.copy()
            challenge['language'] = (challenge.get('language') or 'python').lower()

            # Constraints
            constraints = challenge.get('constraints') or []
            if not isinstance(constraints, list):
                constraints = [str(constraints)]
            if not constraints:
                constraints = [
                    'Handle empty, null, and edge-case inputs explicitly.',
                    'Return output in the exact format specified.'
                ]
            challenge['constraints'] = constraints

            # Examples
            examples = challenge.get('examples') or []
            normalized_examples = []
            for ex in examples:
                if isinstance(ex, dict):
                    normalized_examples.append({
                        'input': ex.get('input', ''),
                        'output': ex.get('output', ex.get('expected_output', '')),
                        'explanation': ex.get('explanation', '')
                    })
                else:
                    normalized_examples.append({
                        'input': str(ex),
                        'output': '',
                        'explanation': ''
                    })
            while len(normalized_examples) < 2:
                normalized_examples.append({
                    'input': f'Sample input {len(normalized_examples) + 1}',
                    'output': 'Sample output',
                    'explanation': 'Sample explanation'
                })
            challenge['examples'] = normalized_examples[:4]

            # Test cases
            test_cases = challenge.get('test_cases') or []
            normalized_tests = []
            for tc in test_cases:
                if isinstance(tc, dict):
                    normalized_tests.append({
                        'input': tc.get('input', ''),
                        'expected_output': tc.get('expected_output', tc.get('output', ''))
                    })
                else:
                    normalized_tests.append({
                        'input': str(tc),
                        'expected_output': ''
                    })
            while len(normalized_tests) < 2:
                normalized_tests.append({
                    'input': f'Sample input {idx + 1}.{len(normalized_tests) + 1}',
                    'expected_output': 'Sample expected output'
                })
            challenge['test_cases'] = normalized_tests[:6]

            # Hints
            hints = challenge.get('hints') or []
            if not isinstance(hints, list):
                hints = [str(hints)]
            if not hints:
                hints = ['Think about time and space complexity; handle edge cases.']
            challenge['hints'] = hints

            normalized.append(challenge)

        return normalized
    
    def _generate_coding_challenge(self, skills: list) -> dict:
        """Generate a coding challenge based on candidate skills"""
        coding_challenges = [
            {
                'id': 'CODE1',
                'title': 'Two Sum Problem',
                'description': 'Given an array of integers, find two numbers that add up to a target sum.',
                'language': 'python',
                'difficulty': 'easy',
                'test_cases': [
                    {'input': '[2, 7, 11, 15], target=9', 'expected_output': '[0, 1]'},
                    {'input': '[3, 2, 4], target=6', 'expected_output': '[1, 2]'},
                ],
                'time_limit_minutes': 15,
                'concepts': ['arrays', 'hash_tables', 'sorting']
            },
            {
                'id': 'CODE2',
                'title': 'Reverse a Linked List',
                'description': 'Reverse the order of elements in a linked list.',
                'language': 'python',
                'difficulty': 'medium',
                'test_cases': [
                    {'input': '1->2->3->4->5', 'expected_output': '5->4->3->2->1'},
                ],
                'time_limit_minutes': 15,
                'concepts': ['linked_lists', 'recursion', 'pointers']
            },
            {
                'id': 'CODE3',
                'title': 'LRU Cache Implementation',
                'description': 'Implement an LRU (Least Recently Used) cache with get and put operations.',
                'language': 'python',
                'difficulty': 'hard',
                'test_cases': [
                    {'input': 'capacity=2, put(1,1), put(2,2), get(1)', 'expected_output': '1'},
                ],
                'time_limit_minutes': 20,
                'concepts': ['design_patterns', 'hash_tables', 'linked_lists']
            },
        ]
        
        # Select based on skill level
        if 'python' in [s.lower() for s in skills]:
            selected = coding_challenges[0]  # Easy
        elif 'javascript' in [s.lower() for s in skills]:
            selected = coding_challenges[1]  # Medium
        else:
            selected = coding_challenges[2]  # Hard
        
        return selected
    
    def _generate_system_design_question(self, skills: list) -> dict:
        """Generate a system design question for senior candidates"""
        return {
            'id': 'SD1',
            'type': 'system_design',
            'question': 'Design a URL shortening service (like bit.ly). Consider scalability, storage, and performance.',
            'topics': ['scalability', 'database_design', 'caching', 'load_balancing'],
            'time_limit_minutes': 20,
            'difficulty': 'hard',
            'evaluation_criteria': [
                'System architecture clarity',
                'Handling of edge cases',
                'Scalability considerations',
                'Technology choices justification'
            ]
        }


class CodingRoundEvaluator:
    """Evaluates coding solutions submitted during interview"""
    
    def __init__(self):
        pass
    
    def evaluate_code(self, code: str, test_cases: list, language: str = 'python') -> dict:
        """
        Evaluate submitted code against test cases
        
        Args:
            code: Submitted code solution
            test_cases: List of test cases to validate
            language: Programming language
        
        Returns:
            Evaluation results with score and feedback
        """
        print("[CodingEvaluator] Evaluating submitted code...")
        
        try:
            results = {
                'passed_tests': 0,
                'total_tests': len(test_cases),
                'execution_time': 0,
                'code_quality_score': self._evaluate_code_quality(code),
                'test_results': [],
                'overall_score': 0
            }
            
            # Run each test case
            for test in test_cases:
                test_result = self._run_test(code, test, language)
                results['test_results'].append(test_result)
                
                if test_result.get('passed'):
                    results['passed_tests'] += 1
            
            # Calculate overall score
            test_pass_rate = (results['passed_tests'] / results['total_tests']) * 100 if results['total_tests'] > 0 else 0
            results['overall_score'] = round((test_pass_rate * 0.7) + (results['code_quality_score'] * 0.3), 2)
            
            print(f"[CodingEvaluator] ✅ Evaluation complete: {results['overall_score']}/100")
            return results
            
        except Exception as e:
            print(f"[CodingEvaluator] Exception: {e}")
            return {
                'error': str(e),
                'overall_score': 0,
                'passed_tests': 0,
                'total_tests': len(test_cases)
            }
    
    def _run_test(self, code: str, test_case: dict, language: str) -> dict:
        """Run a single test case (simulated)"""
        # In production, this would actually execute code in a sandbox
        return {
            'test_input': test_case.get('input'),
            'expected_output': test_case.get('expected_output'),
            'actual_output': test_case.get('expected_output'),  # Simulated
            'passed': True,  # Simulated
            'execution_time_ms': 45
        }
    
    def _evaluate_code_quality(self, code: str) -> float:
        """Evaluate code quality (readability, efficiency, structure)"""
        score = 70.0
        
        # Deductions for poor practices
        if len(code) < 20:
            score -= 30  # Too short, incomplete
        if code.count('TODO') > 0:
            score -= 10  # Incomplete implementation
        if '  ' in code and '\t' not in code:
            score += 10  # Good indentation
        if len([l for l in code.split('\n') if len(l) > 100]) > 0:
            score -= 5  # Long lines
        
        return round(max(0, min(100, score)), 2)


class InterviewSessionManager:
    """Manages interview session lifecycle"""
    
    def __init__(self):
        self.sessions = {}  # In-memory cache
        # Resolve path relative to backend directory
        backend_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        self.sessions_file = os.path.join(backend_dir, 'data', 'interview_sessions.json')
        self.load_sessions()  # Load from file on startup
    
    def load_sessions(self):
        """Load all sessions from file"""
        try:
            if os.path.exists(self.sessions_file):
                with open(self.sessions_file, 'r') as f:
                    self.sessions = json.load(f)
                print(f"[InterviewSessionManager] Loaded {len(self.sessions)} sessions from file")
            else:
                self.sessions = {}
        except Exception as e:
            print(f"[InterviewSessionManager] Error loading sessions: {e}")
            self.sessions = {}
    
    def save_sessions(self):
        """Save all sessions to file"""
        try:
            os.makedirs(os.path.dirname(self.sessions_file), exist_ok=True)
            with open(self.sessions_file, 'w') as f:
                json.dump(self.sessions, f, indent=2)
            print(f"[InterviewSessionManager] Saved {len(self.sessions)} sessions to file")
        except Exception as e:
            print(f"[InterviewSessionManager] Error saving sessions: {e}")
    
    def create_interview_session(self, candidate_id: str, candidate_name: str, job_id: str, 
                                interview_questions: dict) -> dict:
        """
        Create an interview session and generate public link
        
        Args:
            candidate_id: Candidate ID
            candidate_name: Candidate name
            job_id: Job ID
            interview_questions: Generated interview questions
        
        Returns:
            Session details including public link
        """
        session_id = str(uuid.uuid4())[:8].upper()
        interview_token = str(uuid.uuid4())
        
        session = {
            'session_id': session_id,
            'interview_token': interview_token,
            'candidate_id': candidate_id,
            'candidate_name': candidate_name,
            'job_id': job_id,
            'questions': interview_questions,
            'status': 'pending',  # pending, in_progress, completed
            'started_at': None,
            'completed_at': None,
            'responses': {},
            'coding_submission': None,
            'scores': {},
            'created_at': datetime.now().isoformat(),
            'expires_at': (datetime.now() + timedelta(days=7)).isoformat()
        }
        
        self.sessions[session_id] = session
        self.save_sessions()  # Persist to file
        
        # Generate public interview link using FRONTEND_URL from environment
        interview_link = f"{FRONTEND_URL}/interview/{interview_token}"
        
        print(f"[InterviewSession] ✅ Created session {session_id}")
        print(f"[InterviewSession] Interview link: {interview_link}")
        
        return {
            'session_id': session_id,
            'interview_token': interview_token,
            'interview_link': interview_link,
            'interview_duration_minutes': interview_questions.get('total_estimated_duration', 45),
            'expires_at': session['expires_at']
        }
    
    def get_interview_session(self, interview_token: str) -> dict:
        """Retrieve interview session by token"""
        for session in self.sessions.values():
            if session['interview_token'] == interview_token:
                return session
        return None
    
    def start_interview_session(self, interview_token: str) -> dict:
        """Mark interview as started"""
        session = self.get_interview_session(interview_token)
        if not session:
            return {'error': 'Session not found'}
        
        session['status'] = 'in_progress'
        session['started_at'] = datetime.now().isoformat()
        self.save_sessions()  # Persist changes
        
        print(f"[InterviewSession] Interview started for {session['candidate_name']}")
        return {'success': True, 'started_at': session['started_at']}
    
    def submit_question_response(self, interview_token: str, question_id: str, response: str) -> dict:
        """Submit response to a question"""
        session = self.get_interview_session(interview_token)
        if not session:
            return {'error': 'Session not found'}
        
        session['responses'][question_id] = {
            'response': response,
            'submitted_at': datetime.now().isoformat()
        }
        self.save_sessions()  # Persist changes
        
        print(f"[InterviewSession] Response submitted for question {question_id}")
        return {'success': True}
    
    def update_session(self, interview_token: str, session_data: dict) -> dict:
        """Update an existing session with new data"""
        session = self.get_interview_session(interview_token)
        if not session:
            return {'error': 'Session not found'}
        
        # Find the session_id and update
        for session_id, stored_session in self.sessions.items():
            if stored_session['interview_token'] == interview_token:
                self.sessions[session_id] = session_data
                self.save_sessions()
                return {'success': True}
        
        return {'error': 'Session not found'}
    
    def submit_coding_solution(self, interview_token: str, code: str, language: str) -> dict:
        """Submit coding solution"""
        session = self.get_interview_session(interview_token)
        if not session:
            return {'error': 'Session not found'}
        
        coding_challenge = session['questions'].get('coding', {})
        evaluator = CodingRoundEvaluator()
        
        # Evaluate code
        evaluation = evaluator.evaluate_code(
            code,
            coding_challenge.get('test_cases', []),
            language
        )
        
        session['coding_submission'] = {
            'code': code,
            'language': language,
            'submitted_at': datetime.now().isoformat(),
            'evaluation': evaluation
        }
        self.save_sessions()  # Persist changes
        
        print(f"[InterviewSession] Coding solution evaluated: {evaluation.get('overall_score')}/100")
        return {
            'success': True,
            'evaluation': evaluation
        }
    
    def complete_interview(self, interview_token: str) -> dict:
        """Mark interview as completed and generate score"""
        session = self.get_interview_session(interview_token)
        if not session:
            return {'error': 'Session not found'}
        
        session['status'] = 'completed'
        session['completed_at'] = datetime.now().isoformat()
        
        # Calculate interview score
        interview_score = self._calculate_interview_score(session)
        session['scores']['interview_score'] = interview_score
        self.save_sessions()  # Persist changes
        
        print(f"[InterviewSession] Interview completed. Score: {interview_score}/100")
        
        return {
            'success': True,
            'session_id': session['session_id'],
            'interview_score': interview_score,
            'completed_at': session['completed_at']
        }
    
    def _calculate_interview_score(self, session: dict) -> float:
        """Calculate overall interview score from all components"""
        scores = []
        
        # Coding score (40% weight)
        if session.get('coding_submission'):
            coding_score = session['coding_submission'].get('evaluation', {}).get('overall_score', 0)
            scores.append(coding_score * 0.40)
        
        # Response quality (30% weight) - simulated
        response_quality = 75.0  # In production, use NLP to evaluate
        scores.append(response_quality * 0.30)
        
        # Communication/Presentation (20% weight) - simulated
        communication_score = 80.0  # In production, analyze speech patterns
        scores.append(communication_score * 0.20)
        
        # Behavioral fit (10% weight)
        behavioral_score = 75.0  # Based on behavioral question responses
        scores.append(behavioral_score * 0.10)
        
        overall_score = sum(scores)
        return round(min(100, max(0, overall_score)), 2)


# Global instances
interview_generator = InterviewGenerator()
coding_evaluator = CodingRoundEvaluator()
interview_session_manager = InterviewSessionManager()
