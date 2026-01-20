from config.magical_config import match_skills_with_magical, calculate_match_score_fallback


class SkillMatcher:
    def __init__(self):
        pass
    
    def calculate_match_score(self, candidate_skills, job_requirements):
        """
        Calculate percentage match between candidate and job using Magical AI
        Falls back to simple calculation if API unavailable
        
        Args:
            candidate_skills: List of candidate skills
            job_requirements: Job requirements dict with 'must_have' and 'good_to_have'
        
        Returns:
            Match score percentage
        """
        if not job_requirements or not candidate_skills:
            return 0
        
        must_have = job_requirements.get('must_have', [])
        
        print("[SkillMatcher] Attempting to match skills with Magical AI...")
        
        try:
            # Try Magical AI matching
            result = match_skills_with_magical(candidate_skills, job_requirements)
            
            if result.get('success'):
                match_score = result.get('match_percentage', 0)
                print(f"[SkillMatcher] ✅ Magical AI match score: {match_score}%")
                return match_score
            else:
                print(f"[SkillMatcher] Magical AI unavailable: {result.get('error')}")
        except Exception as e:
            print(f"[SkillMatcher] Exception during Magical AI call: {e}")
        
        # Fallback to simple calculation
        print("[SkillMatcher] Using fallback simple calculation...")
        candidate_skills_lower = [s.lower() for s in candidate_skills]
        required_skills_lower = [s.lower() for s in must_have]
        
        matches = len(set(candidate_skills_lower) & set(required_skills_lower))
        total_required = len(required_skills_lower)
        
        if total_required == 0:
            return 0
        
        match_percentage = (matches / total_required) * 100
        return round(match_percentage, 2)
    
    def get_missing_skills(self, candidate_skills, job_requirements):
        """
        Identify skills gap between candidate and job requirements
        Uses Magical AI if available, otherwise simple set difference
        """
        if not job_requirements:
            return []
        
        must_have = job_requirements.get('must_have', [])
        
        try:
            # Try Magical AI
            result = match_skills_with_magical(candidate_skills, job_requirements)
            
            if result.get('success'):
                missing_skills = result.get('missing_skills', [])
                print(f"[SkillMatcher] ✅ Magical AI identified {len(missing_skills)} missing skills")
                return missing_skills
        except Exception as e:
            print(f"[SkillMatcher] Exception getting missing skills: {e}")
        
        # Fallback: Simple set difference
        candidate_skills_lower = [s.lower() for s in candidate_skills]
        required_skills_lower = [s.lower() for s in must_have]
        
        missing = set(required_skills_lower) - set(candidate_skills_lower)
        return list(missing)
    
    def categorize_candidate(self, match_score):
        """
        Categorize candidate based on match score
        
        Args:
            match_score: ATS match percentage score
        
        Returns:
            Dictionary with priority, action, and color
        """
        print(f"[SkillMatcher] Categorizing candidate with score: {match_score}%")
        
        if match_score >= 75:
            return {
                "priority": "High",
                "action": "Interview",
                "color": "green",
                "description": "Strong match - Ready for interview"
            }
        elif match_score >= 50:
            return {
                "priority": "Medium",
                "action": "Review",
                "color": "orange",
                "description": "Moderate match - Review and consider"
            }
        else:
            return {
                "priority": "Low",
                "action": "Reject",
                "color": "red",
                "description": "Below threshold - Auto-reject"
            }
    
    def get_skill_gap_analysis(self, candidate_skills, job_requirements):
        """
        Get detailed skill gap analysis using Magical AI
        """
        try:
            result = match_skills_with_magical(candidate_skills, job_requirements)
            
            if result.get('success'):
                return {
                    'matched_skills': result.get('matched_skills', []),
                    'missing_skills': result.get('missing_skills', []),
                    'gap_analysis': result.get('gap_analysis', {}),
                    'match_score': result.get('match_percentage', 0)
                }
        except Exception as e:
            print(f"[SkillMatcher] Exception in gap analysis: {e}")
        
        return {
            'matched_skills': [],
            'missing_skills': job_requirements.get('must_have', []),
            'gap_analysis': {},
            'match_score': 0
        }
