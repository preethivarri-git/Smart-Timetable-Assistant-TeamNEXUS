from backend.agent.scheduler_agent import schedule

print("SMART SCHEDULER")
print("Type 'exit' to quit.\n")

while True:

    user = input("You: ")

    if user.lower() == "exit":
        break

    schedule(user)