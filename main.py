from backend.agent.scheduler_agent import schedule
DEFAULT_USER_ID = 1
print("SMART SCHEDULER")
print("Type 'exit' to quit.\n")

while True:
    user = input("You: ")
    if user.lower() == "exit":
        break
    result = schedule(user, DEFAULT_USER_ID)

    if result:
        print(result)