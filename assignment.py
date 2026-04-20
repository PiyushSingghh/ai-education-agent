#importing importent libraries like streamlit to display output, groq to use lamma 3,  json to convert python dictionary into json text
# os to access system things, dotenv to reads our .env file
import streamlit as st
from groq import Groq
import json
from dotenv import load_dotenv
import os
load_dotenv()

client = Groq(api_key=os.getenv("GROQ_API_KEY"))

#using lamma 3 for this assignment

#creating blueprint of our agent
class GeneratorAgent:
    def generate(self, grade, topic, feedback=None):
        if feedback:#check if feedback is passed or not
            feedback_text = "\n".join(feedback)
#this is the instruction we send to AI  when we want content
            prompt = f"""Create educational content for Grade {grade} about {topic}.
Previous feedback to fix: {feedback_text}

Return JSON only:
{{"explanation": "...", "mcqs": [{{"question": "...", "options": ["A. ...", "B. ...", "C. ...", "D. ..."], "answer": "A"}}]}}
Make exactly 3 mcqs."""
        else:
            prompt = f"""Create educational content for Grade {grade} students about {topic}.
Use simple language suitable for Grade {grade}.

Return JSON only:
{{"explanation": "...", "mcqs": [{{"question": "...", "options": ["A. ...", "B. ...", "C. ...", "D. ..."], "answer": "A"}}]}}
Make exactly 3 mcqs."""

#to get the responce from lamma 
        response = client.chat.completions.create(
            model="llama-3.3-70b-versatile",
            messages=[
                {"role": "system", "content": "You are an educational content creator. Return valid JSON only."},
                {"role": "user", "content": prompt} #instructions
            ],
            temperature=0.7 #control the creativeness
        )
        #return the responcess
        raw = response.choices[0].message.content
        start = raw.find("{")
        end = raw.rfind("}") + 1
        return json.loads(raw[start:end])

#creating blueprint of agent for checking content
class ReviewerAgent:
    def review(self, content, grade, topic):
        prompt = f"""Review this educational content for Grade {grade} about {topic}:

{json.dumps(content, indent=2)}

Check:
- Is language appropriate for Grade {grade}?
- Are concepts correct?
- Are MCQs relevant to {topic}?

Return JSON only:
{{"status": "pass", "feedback": []}}

status must be pass or fail. if fail, add specific issues in feedback list."""

        response = client.chat.completions.create(
            model="llama-3.3-70b-versatile",
            messages=[
                {"role": "system", "content": "You are an educational reviewer. Return valid JSON only."},
                {"role": "user", "content": prompt}
            ],
            temperature=0.3
        )
        
        raw = response.choices[0].message.content
        start = raw.find("{")
        end = raw.rfind("}") + 1
        return json.loads(raw[start:end])

#this will add both agents together for work
def run_pipeline(grade, topic):
    results = {
        "initial_content": None,
        "review": None,
        "refined_content": None,
        "refined": False
    }#dict to store results
    
    gen = GeneratorAgent()
    rev = ReviewerAgent()
    
    results["initial_content"] = gen.generate(grade, topic)
    results["review"] = rev.review(results["initial_content"], grade, topic)
    
    if results["review"]["status"] == "fail":
        results["refined"] = True
        results["refined_content"] = gen.generate(
            grade, topic,
            feedback=results["review"]["feedback"]
        )
    
    return results

#to show initial genrator output and refined output 
def show_content(content):
    st.write(content["explanation"])
    st.markdown("**Questions:**")
    for i, mcq in enumerate(content["mcqs"], 1):
        with st.expander(f"Q{i}: {mcq['question']}"):
            for opt in mcq["options"]:
                st.write(opt)
            st.success(f"Answer: {mcq['answer']}")


# =======================================UI==================================

st.set_page_config(page_title="AI Edu Agent",)
st.title("AI Content And Questions Generator")
st.write("Generate grade-appropriate content using AI agents")
st.divider()

col1, col2 = st.columns(2)
with col1:
    grade = st.number_input("Grade", min_value=1, max_value=12, value=4)
with col2:
    topic = st.text_input("Topic", value="Types of angles")

if st.button("Generate", type="primary", use_container_width=True):
    if not topic.strip():
        st.error("Please enter a topic")
    else:
        with st.spinner("Agents are working..."):
            results = run_pipeline(grade, topic)

        st.divider()

        # pipeline flow
        st.subheader("Pipeline Flow")
        if results["refined"]:
            st.warning("Generator → Reviewer (Failed) → Generator (Refined)")
        else:
            st.success("Generator → Reviewer (Passed)")

        st.divider()

        # generator output
        st.subheader(" Generator Agent Output")
        show_content(results["initial_content"])

        st.divider()

        # reviewer output
        st.subheader(" Reviewer Agent Feedback")
        review = results["review"]
        
        if review["status"] == "pass":
            st.success("Status: PASS")
            st.write("Content looks good for this grade level")
        else:
            st.error("Status: FAIL")
            for issue in review["feedback"]:
                st.warning(issue)

        # refined output
        if results["refined"]:
            st.divider()
            st.subheader(" Refined Output")
            st.info("Generator re-ran after reviewer feedback")
            show_content(results["refined_content"])