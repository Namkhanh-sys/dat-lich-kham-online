import re
from typing import Any, Dict, List, Optional
from src.csv_helper import CSVHelper

class SymptomMatcher:
    @staticmethod
    def clean_text(text: Optional[str]) -> str:
        """Clean and lowercase text for better matching."""
        if not text:
            return ""
        # Lowercase and strip whitespace
        cleaned = text.lower().strip()
        # Remove common punctuation
        cleaned = re.sub(r'[.,\/#!$%\^&\*;:{}=\-_`~()?]', ' ', cleaned)
        return cleaned.strip()

    @classmethod
    def match_doctors_by_symptom(cls, query_text: str) -> List[Dict[str, Any]]:
        """
        Analyze user's query text for symptoms, and match doctors.
        Returns a list of matched doctor dicts with matching metadata.
        """
        df_doctors = CSVHelper.get_doctors()
        if df_doctors.empty:
            return []

        cleaned_query = cls.clean_text(query_text)
        matched_doctors: List[Dict[str, Any]] = []

        doctors_list = df_doctors.to_dict('records')
        for doctor in doctors_list:
            # Symptoms in doctor record are separated by ';'
            symptoms = [s.strip().lower() for s in doctor.get('symptoms', '').split(';') if s.strip()]
            
            match_score = 0
            matched_symptoms_list = []
            
            # Check if any doctor's symptom is mentioned in user's query
            for symptom in symptoms:
                # Use word boundaries or substring to check if symptom is in the query
                # For Vietnamese, substring matching is generally effective
                if symptom in cleaned_query:
                    match_score += 1
                    matched_symptoms_list.append(symptom)
            
            # If there's a match, or if the specialty name itself is in the query
            specialty = doctor.get('specialty', '').lower()
            if specialty in cleaned_query:
                match_score += 2 # Higher weight for matching specialty directly
                matched_symptoms_list.append(specialty)
                
            if match_score > 0:
                doctor_copy = doctor.copy()
                doctor_copy['match_score'] = match_score
                doctor_copy['matched_symptoms'] = matched_symptoms_list
                matched_doctors.append(doctor_copy)

        # Sort doctors by match score descending
        matched_doctors = sorted(matched_doctors, key=lambda x: x['match_score'], reverse=True)
        
        # Ensure at least 3 doctors are returned
        if len(matched_doctors) < 3:
            matched_ids = {doc['id'] for doc in matched_doctors}
            for doctor in doctors_list:
                if doctor['id'] not in matched_ids:
                    doctor_copy = doctor.copy()
                    doctor_copy['match_score'] = 0
                    doctor_copy['matched_symptoms'] = []
                    matched_doctors.append(doctor_copy)
                if len(matched_doctors) >= 3:
                    break
                    
        # If no doctor was matched and no doctors exist at all, return empty, otherwise we now have at least 3
        return matched_doctors

