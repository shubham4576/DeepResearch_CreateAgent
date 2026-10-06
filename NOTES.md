1. Model chooses the tool to execute and it is excutes by sysstem via python script.
2. When we get tool_call = none
3. It exits with the error of max steps reached. This is to avoid the agent to get stuck in a infinte loop.
4. Because it contains previous + current context. Hence, the input cost increases per turn.