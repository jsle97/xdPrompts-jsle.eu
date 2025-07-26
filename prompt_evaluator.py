#!/usr/bin/env python3
"""
AI Prompt Evaluation System
Rates prompts on a scale of 1-10 based on multiple criteria
"""

import os
import re
import json
from pathlib import Path
from typing import Dict, List, Tuple
from dataclasses import dataclass

@dataclass
class PromptRating:
    filename: str
    clarity_structure: int  # 0-2 points
    completeness: int       # 0-2 points  
    specificity: int        # 0-2 points
    safety_ethics: int      # 0-1 points
    adaptability: int       # 0-1 points
    practical_value: int    # 0-2 points
    total_score: int        # 0-10 total
    details: Dict[str, str] # Explanation of scoring

class PromptEvaluator:
    def __init__(self, prompts_dir: str):
        self.prompts_dir = Path(prompts_dir)
        self.ratings = []
        
    def evaluate_clarity_structure(self, content: str) -> Tuple[int, str]:
        """Evaluate clarity and structure (0-2 points)"""
        score = 0
        details = []
        
        # Check for clear section headers
        required_sections = ['ROLE AND GOAL', 'TASKS', 'USER-PROVIDED PARAMETERS']
        sections_found = sum(1 for section in required_sections if section in content)
        
        if sections_found >= 3:
            score += 1
            details.append("Has all required sections")
        elif sections_found >= 2:
            score += 0.5
            details.append("Has most required sections")
        else:
            details.append("Missing key sections")
            
        # Check for organized structure with clear numbering/bullets
        if re.search(r'\d+\.\s+\*\*.*\*\*:', content) or re.search(r'[\-\*]\s+\*\*.*\*\*:', content):
            score += 1
            details.append("Well-organized with clear formatting")
        elif re.search(r'\d+\.', content) or re.search(r'[\-\*]', content):
            score += 0.5
            details.append("Some organization present")
        else:
            details.append("Poor organization")
            
        return min(2, int(score)), "; ".join(details)
    
    def evaluate_completeness(self, content: str) -> Tuple[int, str]:
        """Evaluate completeness (0-2 points)"""
        score = 0
        details = []
        
        # Check for essential components
        essential_components = [
            ('ROLE AND GOAL', 'role definition'),
            ('TASKS', 'task specification'),
            ('USER-PROVIDED PARAMETERS', 'parameter handling'),
            ('BOUNDARIES', 'safety boundaries'),
            ('PRINCIPLES', 'operating principles')
        ]
        
        components_found = 0
        for component, description in essential_components:
            if component in content or description.split()[1].upper() in content:
                components_found += 1
                
        if components_found >= 4:
            score += 2
            details.append("Comprehensive coverage of all components")
        elif components_found >= 3:
            score += 1.5
            details.append("Good coverage of most components")
        elif components_found >= 2:
            score += 1
            details.append("Basic coverage of key components")
        else:
            details.append("Incomplete coverage")
            
        return min(2, int(score)), "; ".join(details)
    
    def evaluate_specificity(self, content: str) -> Tuple[int, str]:
        """Evaluate specificity and actionability (0-2 points)"""
        score = 0
        details = []
        
        # Check for specific instructions
        specific_patterns = [
            r'must\s+\w+',
            r'should\s+\w+',
            r'will\s+\w+',
            r'step\s+\d+',
            r'Example\s+Values?:',
            r'Type:\s+\w+',
            r'Default\s+if'
        ]
        
        specificity_indicators = sum(1 for pattern in specific_patterns 
                                   if re.search(pattern, content, re.IGNORECASE))
        
        if specificity_indicators >= 10:
            score += 2
            details.append("Highly specific with clear instructions")
        elif specificity_indicators >= 5:
            score += 1.5
            details.append("Good specificity")
        elif specificity_indicators >= 2:
            score += 1
            details.append("Some specificity")
        else:
            details.append("Lacks specific instructions")
            
        # Check for parameter validation
        if 'Validation:' in content or 'Handling if missing' in content:
            score += 0.5
            details.append("includes parameter validation")
            
        return min(2, int(score)), "; ".join(details)
    
    def evaluate_safety_ethics(self, content: str) -> Tuple[int, str]:
        """Evaluate safety and ethical boundaries (0-1 points)"""
        score = 0
        details = []
        
        safety_indicators = [
            'SAFETY',
            'ETHICAL',
            'BOUNDARIES',
            'avoid',
            'not provide',
            'cannot',
            'must not',
            'disclaimer',
            'professional',
            'qualified'
        ]
        
        safety_count = sum(1 for indicator in safety_indicators 
                          if indicator.lower() in content.lower())
        
        if safety_count >= 5:
            score = 1
            details.append("Strong safety and ethical guidelines")
        elif safety_count >= 3:
            score = 0.5
            details.append("Some safety considerations")
        else:
            details.append("Limited safety guidelines")
            
        return score, "; ".join(details)
    
    def evaluate_adaptability(self, content: str) -> Tuple[int, str]:
        """Evaluate adaptability and parameter handling (0-1 points)"""
        score = 0
        details = []
        
        adaptability_indicators = [
            'parameter',
            'adapt',
            'adjust',
            'Default if',
            'missing or invalid',
            'enum',
            'Example Values',
            'STATE MANAGEMENT',
            'dynamic'
        ]
        
        adaptability_count = sum(1 for indicator in adaptability_indicators 
                               if indicator.lower() in content.lower())
        
        if adaptability_count >= 8:
            score = 1
            details.append("Highly adaptable with robust parameter handling")
        elif adaptability_count >= 5:
            score = 0.5
            details.append("Some adaptability features")
        else:
            details.append("Limited adaptability")
            
        return score, "; ".join(details)
    
    def evaluate_practical_value(self, content: str) -> Tuple[int, str]:
        """Evaluate practical value and usefulness (0-2 points)"""
        score = 0
        details = []
        
        # Check for real-world applicability
        practical_indicators = [
            'example',
            'use case',
            'scenario',
            'implementation',
            'workflow',
            'process',
            'step-by-step',
            'actionable',
            'practical'
        ]
        
        practical_count = sum(1 for indicator in practical_indicators 
                            if indicator.lower() in content.lower())
        
        if practical_count >= 8:
            score += 2
            details.append("High practical value with clear use cases")
        elif practical_count >= 5:
            score += 1.5
            details.append("Good practical value")
        elif practical_count >= 3:
            score += 1
            details.append("Some practical value")
        else:
            details.append("Limited practical application")
            
        # Bonus for comprehensive examples
        if 'Example Values:' in content and content.count('Example') >= 3:
            score += 0.5
            details.append("includes comprehensive examples")
            
        return min(2, int(score)), "; ".join(details)
    
    def evaluate_prompt(self, filepath: Path) -> PromptRating:
        """Evaluate a single prompt file"""
        try:
            with open(filepath, 'r', encoding='utf-8') as f:
                content = f.read()
        except Exception as e:
            return PromptRating(
                filename=filepath.name,
                clarity_structure=0, completeness=0, specificity=0,
                safety_ethics=0, adaptability=0, practical_value=0,
                total_score=0,
                details={'error': f"Failed to read file: {e}"}
            )
        
        # Evaluate each criterion
        clarity, clarity_detail = self.evaluate_clarity_structure(content)
        completeness, completeness_detail = self.evaluate_completeness(content)
        specificity, specificity_detail = self.evaluate_specificity(content)
        safety, safety_detail = self.evaluate_safety_ethics(content)
        adaptability, adaptability_detail = self.evaluate_adaptability(content)
        practical, practical_detail = self.evaluate_practical_value(content)
        
        total = clarity + completeness + specificity + safety + adaptability + practical
        
        return PromptRating(
            filename=filepath.name,
            clarity_structure=clarity,
            completeness=completeness,
            specificity=specificity,
            safety_ethics=safety,
            adaptability=adaptability,
            practical_value=practical,
            total_score=total,
            details={
                'clarity_structure': clarity_detail,
                'completeness': completeness_detail,
                'specificity': specificity_detail,
                'safety_ethics': safety_detail,
                'adaptability': adaptability_detail,
                'practical_value': practical_detail
            }
        )
    
    def evaluate_all_prompts(self) -> List[PromptRating]:
        """Evaluate all prompts in the directory"""
        prompt_files = list(self.prompts_dir.glob("*.txt"))
        print(f"Found {len(prompt_files)} prompt files to evaluate...")
        
        ratings = []
        for i, filepath in enumerate(prompt_files, 1):
            if i % 50 == 0:
                print(f"Processed {i}/{len(prompt_files)} prompts...")
            
            rating = self.evaluate_prompt(filepath)
            ratings.append(rating)
        
        return sorted(ratings, key=lambda x: x.total_score, reverse=True)
    
    def generate_report(self, ratings: List[PromptRating]) -> str:
        """Generate a comprehensive evaluation report"""
        total_prompts = len(ratings)
        avg_score = sum(r.total_score for r in ratings) / total_prompts if total_prompts > 0 else 0
        
        # Score distribution
        score_distribution = {}
        for rating in ratings:
            score = rating.total_score
            score_distribution[score] = score_distribution.get(score, 0) + 1
        
        # Top and bottom performers
        top_10 = ratings[:10] if len(ratings) >= 10 else ratings
        bottom_10 = ratings[-10:] if len(ratings) >= 10 else []
        
        report = f"""# AI Prompt Evaluation Report

## Summary Statistics
- Total Prompts Evaluated: {total_prompts}
- Average Score: {avg_score:.2f}/10
- Highest Score: {ratings[0].total_score}/10 ({ratings[0].filename})
- Lowest Score: {ratings[-1].total_score}/10 ({ratings[-1].filename})

## Score Distribution
"""
        for score in sorted(score_distribution.keys(), reverse=True):
            count = score_distribution[score]
            percentage = (count / total_prompts * 100)
            report += f"- Score {score}/10: {count} prompts ({percentage:.1f}%)\n"
        
        report += f"""
## Top 10 Performers
"""
        for i, rating in enumerate(top_10, 1):
            report += f"{i}. **{rating.filename}** - {rating.total_score}/10\n"
            report += f"   - Clarity: {rating.clarity_structure}/2, Completeness: {rating.completeness}/2, Specificity: {rating.specificity}/2\n"
            report += f"   - Safety: {rating.safety_ethics}/1, Adaptability: {rating.adaptability}/1, Practical: {rating.practical_value}/2\n\n"
        
        if bottom_10:
            report += f"""
## Bottom 10 Performers
"""
            for i, rating in enumerate(reversed(bottom_10), 1):
                report += f"{i}. **{rating.filename}** - {rating.total_score}/10\n"
        
        return report
    
    def save_detailed_results(self, ratings: List[PromptRating], output_file: str):
        """Save detailed results to JSON file"""
        results = []
        for rating in ratings:
            results.append({
                'filename': rating.filename,
                'scores': {
                    'clarity_structure': rating.clarity_structure,
                    'completeness': rating.completeness,
                    'specificity': rating.specificity,
                    'safety_ethics': rating.safety_ethics,
                    'adaptability': rating.adaptability,
                    'practical_value': rating.practical_value,
                    'total_score': rating.total_score
                },
                'details': rating.details
            })
        
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(results, f, indent=2, ensure_ascii=False)

def main():
    """Main execution function"""
    prompts_dir = "/home/runner/work/xdPrompts-jsle.eu/xdPrompts-jsle.eu/prompts"
    
    evaluator = PromptEvaluator(prompts_dir)
    ratings = evaluator.evaluate_all_prompts()
    
    # Generate and save report
    report = evaluator.generate_report(ratings)
    with open("prompt_evaluation_report.md", 'w', encoding='utf-8') as f:
        f.write(report)
    
    # Save detailed results
    evaluator.save_detailed_results(ratings, "prompt_ratings_detailed.json")
    
    # Create simple ratings file
    with open("prompt_ratings.txt", 'w', encoding='utf-8') as f:
        f.write("# AI Prompt Ratings (1-10 Scale)\n")
        f.write("# Format: filename | score | breakdown\n\n")
        for rating in ratings:
            f.write(f"{rating.filename} | {rating.total_score}/10 | ")
            f.write(f"C:{rating.clarity_structure} Comp:{rating.completeness} S:{rating.specificity} ")
            f.write(f"Safe:{rating.safety_ethics} A:{rating.adaptability} P:{rating.practical_value}\n")
    
    print(f"\nEvaluation complete!")
    print(f"- Evaluated {len(ratings)} prompts")
    print(f"- Average score: {sum(r.total_score for r in ratings) / len(ratings):.2f}/10")
    print(f"- Results saved to prompt_evaluation_report.md and prompt_ratings.txt")

if __name__ == "__main__":
    main()