from django.shortcuts import render
import google.generativeai as genai
import re

model = genai.GenerativeModel("gemini-2.5-flash")

def parse_mcqs(text):
    import re
    pattern = re.compile(r"\*\*(\d+)\.\s(.+?)\*\*\s+a\)\s(.+?)\s+b\)\s(.+?)\s+c\)\s(.+?)\s+d\)\s(.+?)\s+\*\*Correct Answer: (\w)\)\*\*", re.DOTALL)
    questions = []
    for match in pattern.finditer(text):
        _, question, a, b, c, d, correct = match.groups()
        options = [('a', a.strip()), ('b', b.strip()), ('c', c.strip()), ('d', d.strip())]
        questions.append({
            'question': question.strip(),
            'options': options,
            'correct': correct.lower()
        })
    return questions

def quiz(request):
    if request.method == "POST":
        if "subject" in request.POST:
            subject = request.POST["subject"]
            level = request.POST.get("level", "beginner")
            question_count = int(request.POST.get("question_count", 10))

            prompt = f"""
Generate {question_count} multiple-choice questions on the subject: "{subject}".
Difficulty level: {level.capitalize()}.

Use this exact format:

**1. Your question here**

a) Option A  
b) Option B  
c) Option C  
d) Option D  

**Correct Answer: b)**

Repeat the format for all {question_count} questions.
"""

            response = model.generate_content(prompt)
            text = response.candidates[0].content.parts[0].text.strip()
            questions = parse_mcqs(text)

            request.session["quiz"] = questions
            request.session["subject"] = subject
            request.session["level"] = level
            request.session["question_count"] = question_count

            return render(request, "quiz/ai_quiz.html", {
                "questions": questions,
                "subject": subject,
                "level": level,
                "question_count": question_count,
                "show_quiz": True,
                "show_results": False
            })

        elif any(key.startswith("q") for key in request.POST):
            questions = request.session.get("quiz", [])
            subject = request.session.get("subject", "Unknown")
            level = request.session.get("level", "Unknown")
            question_count = request.session.get("question_count", len(questions))

            score = 0
            results = []

            for i, q in enumerate(questions):
                selected = request.POST.get(f"q{i}")
                is_correct = selected == q["correct"]
                if is_correct:
                    score += 1
                results.append({
                    "question": q["question"],
                    "your_answer": dict(q["options"]).get(selected, ""),
                    "correct": dict(q["options"]).get(q["correct"], ""),
                    "is_correct": is_correct
                })

            return render(request, "quiz/ai_quiz.html", {
                "score": score,
                "results": results,
                "subject": subject,
                "level": level,
                "question_count": question_count,
                "show_quiz": False,
                "show_results": True
            })

    return render(request, "quiz/ai_quiz.html", {
        "show_quiz": False,
        "show_results": False
    })