"""
Adaptive Interview System with Groq AI
Generates contextual follow-up questions based on candidate responses
"""

import json
from config.groq_config import call_groq
from datetime import datetime

class AdaptiveInterviewManager:
    """Manages adaptive interview flow with Groq AI-powered question generation"""
    
    def __init__(self):
        self.interview_sessions = {}
        self.response_history = {}
    
    def _parse_json_robustly(self, response: str, is_array: bool = False) -> any:
        """Robustly parse JSON (object or array) from Groq response"""
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
                pattern = r'\[.*\]' if is_array else r'\{.*\}'
                json_match = re.search(pattern, response, re.DOTALL)
                if json_match:
                    try:
                        return json.loads(json_match.group())
                    except:
                        pass
        return None
    
    def generate_initial_questions(self, job_title: str, candidate_skills: list, interview_type: str = 'behavioral') -> dict:
        """
        Generate initial set of questions for the interview phase
        
        Args:
            job_title: Job position being interviewed for
            candidate_skills: List of candidate's skills
            interview_type: 'behavioral', 'technical', 'system_design'
        
        Returns:
            Dictionary with questions and interview metadata
        """
        print(f"[AdaptiveInterview] Generating {interview_type} questions for {job_title}")
        
        # Create context for Groq
        if interview_type == 'behavioral':
            return self._generate_behavioral_questions(job_title, candidate_skills)
        elif interview_type == 'technical':
            return self._generate_technical_questions(job_title, candidate_skills)
        elif interview_type == 'system_design':
            return self._generate_system_design_questions(job_title, candidate_skills)
        else:
            return {'error': 'Unknown interview type'}
    
    def _generate_behavioral_questions(self, job_title: str, candidate_skills: list) -> dict:
        """Generate behavioral interview questions using Groq"""
        system_prompt = """You are an expert HR interviewer specializing in behavioral interviews.
Generate 3 behavioral interview questions that assess:
1. Problem-solving and decision-making
2. Teamwork and collaboration
3. Handling challenges and setbacks

For each question, provide:
- The question text
- Why this question is important
- Key competencies being assessed

Format as JSON array with objects containing: question, importance, competencies (array)"""
        
        user_prompt = f"""Generate behavioral interview questions for a {job_title} position.
Candidate skills: {', '.join(candidate_skills) if candidate_skills else 'Not specified'}

Create 3 thought-provoking behavioral questions that will help assess cultural fit and soft skills."""
        
        try:
            response = call_groq(user_prompt, system_prompt, max_tokens=2000)
            questions = self._parse_groq_response(response, interview_type='behavioral')
            return {
                'success': True,
                'type': 'behavioral',
                'questions': questions,
                'generated_at': datetime.now().isoformat()
            }
        except Exception as e:
            print(f"[AdaptiveInterview] Error generating behavioral questions: {e}")
            return self._fallback_behavioral_questions()
    
    def _generate_technical_questions(self, job_title: str, candidate_skills: list) -> dict:
        """Generate technical interview questions using Groq"""
        system_prompt = """You are an expert technical interviewer.
Generate 3 technical interview questions that assess:
1. Core technical knowledge
2. Problem-solving approach
3. Architecture and design thinking

For each question, provide:
- The question text
- Technical skills being assessed
- Difficulty level (beginner, intermediate, advanced)
- Expected answer depth

Format as JSON array with objects containing: question, skills_assessed (array), difficulty, depth"""
        
        user_prompt = f"""Generate technical interview questions for a {job_title} position.
Candidate technical skills: {', '.join(candidate_skills) if candidate_skills else 'Not specified'}

Create 3 technical questions that assess practical knowledge and problem-solving abilities."""
        
        try:
            response = call_groq(user_prompt, system_prompt, max_tokens=2000)
            questions = self._parse_groq_response(response, interview_type='technical')
            return {
                'success': True,
                'type': 'technical',
                'questions': questions,
                'generated_at': datetime.now().isoformat()
            }
        except Exception as e:
            print(f"[AdaptiveInterview] Error generating technical questions: {e}")
            return self._fallback_technical_questions()
    
    def _generate_system_design_questions(self, job_title: str, candidate_skills: list) -> dict:
        """Generate system design questions for senior roles"""
        system_prompt = """You are an expert in system design interviews.
Generate 2 system design questions that assess:
1. Scalability and architecture design
2. Trade-off analysis
3. Real-world system design experience

For each question, provide:
- The question text
- Design considerations to evaluate
- What a good answer should include

Format as JSON array with objects containing: question, considerations (array), good_answer_includes (array)"""
        
        user_prompt = f"""Generate system design interview questions for a {job_title} position.
Candidate experience level: {len(candidate_skills)} years worth of skills

Create 2 realistic system design scenarios that assess architectural thinking."""
        
        try:
            response = call_groq(user_prompt, system_prompt, max_tokens=2000)
            questions = self._parse_groq_response(response, interview_type='system_design')
            return {
                'success': True,
                'type': 'system_design',
                'questions': questions,
                'generated_at': datetime.now().isoformat()
            }
        except Exception as e:
            print(f"[AdaptiveInterview] Error generating system design questions: {e}")
            return self._fallback_system_design_questions()
    
    def generate_follow_up_question(self, original_question: str, candidate_response: str, 
                                   interview_type: str = 'behavioral', depth_level: int = 1) -> dict:
        """
        Generate contextual follow-up question based on candidate's response
        
        Args:
            original_question: The question that was asked
            candidate_response: The candidate's response
            interview_type: Type of interview (behavioral, technical, etc.)
            depth_level: How deep to go (1-3, where 3 is deepest)
        
        Returns:
            Dictionary with follow-up question and analysis
        """
        print(f"[AdaptiveInterview] Generating follow-up question (depth: {depth_level})")
        
        system_prompt = f"""You are an expert {interview_type} interviewer.
Based on the candidate's response, generate a thoughtful follow-up question that:
1. Digs deeper into their answer
2. Explores gaps or interesting points
3. Assesses their reasoning at a deeper level

The follow-up should be at depth level {depth_level}/3 where:
- Level 1: Surface level clarification
- Level 2: Deep dive into technical/behavioral aspects
- Level 3: Challenge their assumptions or explore edge cases

Respond with JSON containing:
- follow_up_question: The next question to ask
- rationale: Why this follow-up is valuable
- what_to_listen_for: Key indicators of a good answer
- assessment_criteria: How to evaluate the answer"""
        
        user_prompt = f"""Original {interview_type} interview question:
"{original_question}"

Candidate's response:
"{candidate_response}"

Generate a follow-up question at depth level {depth_level} that will help better assess the candidate."""
        
        try:
            response = call_groq(user_prompt, system_prompt, max_tokens=1500)
            follow_up = self._parse_follow_up_response(response)
            return {
                'success': True,
                'follow_up_question': follow_up.get('follow_up_question'),
                'rationale': follow_up.get('rationale'),
                'assessment_criteria': follow_up.get('assessment_criteria', []),
                'depth_level': depth_level,
                'original_question': original_question,
                'candidate_response_summary': candidate_response[:200] + '...' if len(candidate_response) > 200 else candidate_response
            }
        except Exception as e:
            print(f"[AdaptiveInterview] Error generating follow-up: {e}")
            return {
                'success': False,
                'error': str(e),
                'follow_up_question': 'Can you elaborate more on that?'
            }
    
    def generate_skill_assessment(self, responses: list, interview_type: str = 'behavioral') -> dict:
        """
        Generate assessment based on all responses in an interview phase
        
        Args:
            responses: List of question-response pairs
            interview_type: Type of interview
        
        Returns:
            Assessment with strengths, weaknesses, and scores
        """
        print(f"[AdaptiveInterview] Generating {interview_type} skill assessment")
        
        system_prompt = """You are an expert interview assessor.
Analyze the candidate's responses and provide:
1. Key strengths demonstrated
2. Areas for improvement
3. Overall assessment score (0-100)
4. Recommendation for next phase

Respond with JSON containing:
- strengths: Array of demonstrated strengths
- areas_for_improvement: Array of areas to work on
- overall_score: Number 0-100
- phase_recommendation: 'proceed' or 'revisit'
- summary: Brief assessment summary (2-3 sentences)"""
        
        response_text = "\n\n".join([
            f"Q{i+1}: {r.get('question', 'N/A')}\nA: {r.get('response', 'No response')}"
            for i, r in enumerate(responses[:5])  # Limit to 5 responses
        ])
        
        user_prompt = f"""Assess these {interview_type} interview responses:

{response_text}

Provide a comprehensive assessment including strengths, areas for improvement, and an overall score."""
        
        try:
            response = call_groq(user_prompt, system_prompt, max_tokens=1500)
            assessment = self._parse_assessment_response(response)
            return {
                'success': True,
                'assessment': assessment,
                'type': interview_type,
                'generated_at': datetime.now().isoformat()
            }
        except Exception as e:
            print(f"[AdaptiveInterview] Error generating assessment: {e}")
            return {
                'success': False,
                'error': str(e),
                'assessment': {'overall_score': 50, 'summary': 'Assessment pending'}
            }
    
    def suggest_next_interview_path(self, current_phase: str, candidate_performance: dict) -> dict:
        """
        Suggest the next interview phase based on performance
        
        Args:
            current_phase: Current interview phase (e.g., 'behavioral')
            candidate_performance: Performance metrics and scores
        
        Returns:
            Suggestion for next phase and rationale
        """
        print(f"[AdaptiveInterview] Analyzing interview path from {current_phase}")
        
        system_prompt = """You are an interview coordinator.
Based on the candidate's performance, recommend the next interview phase.
Consider:
1. Performance score
2. Strengths and weaknesses
3. Interview flow
4. Optimal candidate experience

Respond with JSON containing:
- recommended_next_phase: 'technical', 'coding', 'system_design', or 'end'
- confidence_score: 0-100 (confidence in recommendation)
- rationale: Why this recommendation
- suggested_adjustments: Any interview adjustments recommended"""
        
        perf_text = json.dumps(candidate_performance, indent=2)
        
        user_prompt = f"""Based on this {current_phase} phase performance:

{perf_text}

Recommend the next interview phase and any adjustments needed."""
        
        try:
            response = call_groq(user_prompt, system_prompt, max_tokens=1000)
            suggestion = self._parse_suggestion_response(response)
            return {
                'success': True,
                'current_phase': current_phase,
                'recommendation': suggestion,
                'generated_at': datetime.now().isoformat()
            }
        except Exception as e:
            print(f"[AdaptiveInterview] Error suggesting next phase: {e}")
            return {
                'success': False,
                'error': str(e),
                'recommendation': {'next_phase': 'technical'}
            }
    
    # Helper methods
    
    def _parse_groq_response(self, response: str, interview_type: str = 'behavioral') -> list:
        """Parse Groq response and extract questions"""
        try:
            questions_data = self._parse_json_robustly(response, is_array=True)
            if questions_data and isinstance(questions_data, list):
                questions = []
                for i, q in enumerate(questions_data):
                    questions.append({
                        'id': f'{interview_type.upper()}{i+1}',
                        'question': q.get('question', f'Question {i+1}'),
                        'type': interview_type,
                        'details': {
                            'importance': q.get('importance'),
                            'competencies': q.get('competencies', q.get('skills_assessed', [])),
                            'difficulty': q.get('difficulty', 'medium')
                        }
                    })
                return questions
            else:
                # Handle case where it returned an object instead of array
                data = self._parse_json_robustly(response, is_array=False)
                if data and 'questions' in data and isinstance(data['questions'], list):
                    return self._parse_groq_response(json.dumps(data['questions']), interview_type)
        except Exception as e:
            print(f"[AdaptiveInterview] Error parsing: {e}")
            
        return self._fallback_parse_questions(response, interview_type)
    
    def _parse_follow_up_response(self, response: str) -> dict:
        """Parse follow-up question response"""
        try:
            import re
            json_match = re.search(r'\{.*\}', response, re.DOTALL)
            if json_match:
                return json.loads(json_match.group())
        except:
            pass
        
        return {
            'follow_up_question': response.split('\n')[0][:100],
            'rationale': 'Follow-up to explore deeper understanding',
            'assessment_criteria': ['Depth of knowledge', 'Critical thinking']
        }
    
    def _parse_assessment_response(self, response: str) -> dict:
        """Parse assessment response"""
        try:
            import re
            json_match = re.search(r'\{.*\}', response, re.DOTALL)
            if json_match:
                return json.loads(json_match.group())
        except:
            pass
        
        return {
            'overall_score': 75,
            'strengths': ['Communication', 'Problem-solving'],
            'areas_for_improvement': ['Technical depth'],
            'summary': 'Good performance overall'
        }
    
    def _parse_suggestion_response(self, response: str) -> dict:
        """Parse next phase suggestion"""
        try:
            import re
            json_match = re.search(r'\{.*\}', response, re.DOTALL)
            if json_match:
                return json.loads(json_match.group())
        except:
            pass
        
        return {
            'next_phase': 'technical',
            'confidence_score': 75,
            'rationale': 'Ready for next phase'
        }
    
    def _fallback_parse_questions(self, response: str, interview_type: str) -> list:
        """Fallback question parsing"""
        questions = []
        lines = response.split('\n')
        q_count = 0
        
        for line in lines:
            if line.strip().startswith(('-', '•', '*')) or line.strip().startswith(('Question', 'Q')):
                q_count += 1
                questions.append({
                    'id': f'{interview_type.upper()}{q_count}',
                    'question': line.replace('-', '').replace('•', '').replace('*', '').strip()[:200],
                    'type': interview_type
                })
        
        return questions[:3] if questions else [{
            'id': f'{interview_type.upper()}1',
            'question': 'Tell me about yourself and your experience.',
            'type': interview_type
        }]
    
    def _fallback_behavioral_questions(self) -> dict:
        """Fallback behavioral questions"""
        return {
            'success': True,
            'type': 'behavioral',
            'questions': [
                {
                    'id': 'B1',
                    'question': 'Tell us about a challenging project you worked on and how you handled it.',
                    'type': 'behavioral'
                },
                {
                    'id': 'B2',
                    'question': 'Describe a time you had to work with a difficult team member.',
                    'type': 'behavioral'
                },
                {
                    'id': 'B3',
                    'question': 'What interests you about this role and why do you think you\'re a good fit?',
                    'type': 'behavioral'
                }
            ]
        }
    
    def _fallback_technical_questions(self) -> dict:
        """Fallback technical questions"""
        return {
            'success': True,
            'type': 'technical',
            'questions': [
                {
                    'id': 'T1',
                    'question': 'Explain the architecture you would use for a distributed system.',
                    'type': 'technical'
                },
                {
                    'id': 'T2',
                    'question': 'How do you approach performance optimization in your code?',
                    'type': 'technical'
                },
                {
                    'id': 'T3',
                    'question': 'What design patterns have you used in your recent projects?',
                    'type': 'technical'
                }
            ]
        }
    
    def _fallback_system_design_questions(self) -> dict:
        """Fallback system design questions"""
        return {
            'success': True,
            'type': 'system_design',
            'questions': [
                {
                    'id': 'SD1',
                    'question': 'Design a URL shortening service like TinyURL.',
                    'type': 'system_design'
                },
                {
                    'id': 'SD2',
                    'question': 'Design a real-time notification system for a social media platform.',
                    'type': 'system_design'
                }
            ]
        }


# Create singleton instance
adaptive_interview_manager = AdaptiveInterviewManager()
