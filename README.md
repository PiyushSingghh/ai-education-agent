# ai-education-agent
created 2 agents who can generate educational content and questions accurately using lamma 3.1
1st is a generator agent who creats the explanation and mcq for any grade and topic
2nd is a reviwer agent who checks is content is age apporpriate nad conceptually correct?

if reviewer fails the content genrator runs again with feedback

## Tech Used
- Python
- Streamlit (UI)
- Groq API with Llama model
- Two agent classes with structured JSON

- ## How to Run
1. Clone this repo
2. pip install -r requirements.txt
3. Create .env file and add:
   GROQ_API_KEY=your_key_here
   Get free key at: console.groq.com
4. streamlit run app.py
