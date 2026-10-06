from ollama import chat, ChatResponse
from datetime import datetime

def get_time():
    """Returns the current time."""
    return  datetime.now().strftime("%Y-%m-%d %H:%M:%S")

def llm_call(messages:list) -> ChatResponse:
    """Calls the LLM with the given prompt and returns the response."""
    llm: ChatResponse = chat(
        model="gemma4:31b-cloud",
        messages=messages,
        tools=[get_time]
    )

    return llm

if __name__ == "__main__":
    
    available_functions = {
        "get_time": get_time    
    }   

    messages = [{'role': 'user', 'content': 'What time is it?'}]
    response = llm_call(messages)
    
    if response.message.tool_calls:
        # There may be multiple tool calls in the response
        # Add the assistant message with tool calls to the conversation
        messages.append(response.message)

        for tool in response.message.tool_calls:
            # Ensure the function is available, and then call it
            if function_to_call := available_functions.get(tool.function.name):
                print('Calling function:', tool.function.name)
                print('Arguments:', tool.function.arguments)
                output = function_to_call(**tool.function.arguments)
                print('Function output:', output)
            else:
                print('Function', tool.function.name, 'not found')
                output = 'Function not found'

            # Add each tool result as a separate message
            messages.append({'role': 'tool', 'content': str(output), 'tool_name': tool.function.name})

        # Get final response from model with all tool call results
        final_response = llm_call(messages)
        print('Final response:', final_response)

    else:
        print('No tool calls returned from model')