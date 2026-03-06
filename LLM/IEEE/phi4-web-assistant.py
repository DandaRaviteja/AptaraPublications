import requests
from foundry_local import FoundryLocalManager
from ddgs import DDGS
import json

def search_web(query):
    """Search the web and return top results"""
    try:
        results = list(DDGS().text(query, max_results=3))
        
        if not results:
            return "No search results found."
        
        search_summary = "\n\n".join([
            f"[Source {i+1}] {r['title']}\n{r['body'][:500]}"
            for i, r in enumerate(results)
        ])
        return search_summary
    except Exception as e:
        return f"Search failed: {e}"

def ask_phi4(endpoint, model_id, prompt):
    """Send a prompt to Phi-4 and stream response"""
    response = requests.post(
        f"{endpoint}/chat/completions",
        json={
            "model": model_id,
            "messages": [{"role": "user", "content": prompt}],
            "stream": True
        },
        stream=True,
        timeout=180
    )
    
    full_response = ""
    for line in response.iter_lines():
        if line:
            line_text = line.decode('utf-8')
            if line_text.startswith('data: '):
                line_text = line_text[6:]  # Remove 'data: ' prefix
            
            if line_text.strip() == '[DONE]':
                break
                
            try:
                data = json.loads(line_text)
                if 'choices' in data and len(data['choices']) > 0:
                    delta = data['choices'][0].get('delta', {})
                    if 'content' in delta:
                        chunk = delta['content']
                        print(chunk, end="", flush=True)
                        full_response += chunk
            except json.JSONDecodeError:
                continue
    
    print()
    return full_response

def web_enhanced_query(question):
    """Combine web search with Phi-4 reasoning"""
    # By using an alias, the most suitable model will be downloaded
    # to your device automatically
    alias = "phi-4-mini"
    
    # Create a FoundryLocalManager instance. This will start the Foundry
    # Local service if it is not already running and load the specified model.
    manager = FoundryLocalManager(alias)
    model_info = manager.get_model_info(alias)
    
    print("🔍 Searching the web...\n")
    search_results = search_web(question)
    
    prompt = f"""Here are recent search results:

{search_results}

Question: {question}

Using only the information above, give a clear answer with specific details."""
    
    print("🤖 Phi-4 Answer:\n")
    return ask_phi4(manager.endpoint, model_info.id, prompt)

if __name__ == "__main__":
    # Try different questions
    question = "Who won the 2024 NBA championship?"
    # question = "What is the latest iPhone model released in 2024?"
    # question = "What is the current price of Bitcoin?"
    
    print(f"Question: {question}\n")
    print("=" * 60 + "\n")
    
    web_enhanced_query(question)
    print("\n" + "=" * 60)
