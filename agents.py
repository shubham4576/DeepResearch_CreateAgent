from langchain_ollama import ChatOllama
from langchain_core.messages import AIMessage

llm = ChatOllama(
    model="gemma4:31b-cloud",
    temperature=0,
)

def log_usage(response: AIMessage) -> None:
    print("Tokens used:", response.usage_metadata)
    print("\n")
    print("prompt_eval_count:", response.response_metadata["prompt_eval_count"])
    print("completion_tokens:", response.response_metadata["eval_count"], end="\n\n")


response = llm.invoke("Write a poem about a lonely robot.")
log_usage(response)
print(response.content)
