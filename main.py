import json
import os
from openai import OpenAI
from prompts import SYSTEM_PROMPTS

# 1. Setup our "connection" to the LLM
# We are using Gemini's "OpenAI-compatible" link
client = OpenAI(
    api_key=os.environ.get("GITHUB_TOKEN"), 
    base_url="https://models.inference.ai.azure.com"
)

def classify_intent(message):
    """
    Step 1: Detect what the user wants (Code, Data, Writing, or Career)
    """
    
    # This is the "Instruction" we give to the LLM
    classifier_instruction = """
    Your task is to classify the user's intent. 
    Choose one of these labels: code, data, writing, career, unclear. 
    Respond ONLY with a JSON object like this:
    {"intent": "label", "confidence": 0.95}
    """

    try:
        # Call the LLM
        response = client.chat.completions.create(
            model="gpt-4o-mini", # A fast, cheap model
            messages=[
                {"role": "system", "content": classifier_instruction},
                {"role": "user", "content": message}
            ],
            response_format={ "type": "json_object" } # This forces JSON output
        )

        # Extract the text and turn it into a Python dictionary
        result = json.loads(response.choices[0].message.content)
        return result

    except Exception as e:
        # If the LLM makes a mistake or the internet fails, 
        # we return a "Safe" default so the program doesn't crash.
        print(f"Error occurred: {e}")
        return {"intent": "unclear", "confidence": 0.0}

def route_and_respond(message, intent_data):
    """
    Step 2: Use the intent to pick an expert and get a final response.
    """
    intent = intent_data.get("intent")
    
    # Requirement #4: Handle 'unclear' intent
    if intent == "unclear" or intent_data.get("confidence") < 0.5:
        return "I'm not quite sure what you need. Are you looking for help with coding, data analysis, writing, or career advice?"

    # Requirement #3: Map intent to the expert prompt
    # We get the specific persona from our SYSTEM_PROMPTS dictionary
    system_prompt = SYSTEM_PROMPTS.get(intent)

    try:
        # Second LLM call for the actual answer
        response = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": message}
            ]
        )
        return response.choices[0].message.content

    except Exception as e:
        return f"I ran into an error getting the expert response: {e}"


def log_request(intent_data, message, response):
    """
    Requirement #5: Log the request to a .jsonl file.
    """
    log_entry = {
        "intent": intent_data.get("intent"),
        "confidence": intent_data.get("confidence"),
        "user_message": message,
        "final_response": response
    }
    
    # We open the file in 'a' (append) mode so we don't delete old logs
    with open("route_log.jsonl", "a") as f:
        # json.dumps turns the dictionary into a string
        f.write(json.dumps(log_entry) + "\n")
        
# --- TESTING AREA ---
if __name__ == "__main__":
    # The official test list from your instructions
    test_messages = [
        "how do i sort a list of objects in python?",
        "explain this sql query for me",
        "This paragraph sounds awkward, can you help me fix it?",
        "I'm preparing for a job interview, any tips?",
        "what's the average of these numbers: 12, 45, 23, 67, 34",
        "Help me make this better.",
        "I need to write a function that takes a user id and returns their profile, but also i need help with my resume.",
        "hey",
        "Can you write me a poem about clouds?",
        "Rewrite this sentence to be more professional.",
        "I'm not sure what to do with my career.",
        "what is a pivot table",
        "fxi thsi bug pls: for i in range(10) print(i)",
        "How do I structure a cover letter?",
        "My boss says my writing is too verbose."
    ]

    print(f"--- Starting Batch Test of {len(test_messages)} messages ---\n")

    for msg in test_messages:
        print(f"Processing: {msg}")
        
        # 1. Classify
        classification = classify_intent(msg)
        
        # 2. Route and Respond
        final_answer = route_and_respond(msg, classification)
        
        # 3. Log
        log_request(classification, msg, final_answer)
        
        print(f"Result: {classification['intent']} (Conf: {classification['confidence']})")
        print("-" * 20)

    print("\n--- All tests complete. Check route_log.jsonl for details! ---")