from src.agents import (
    create_policy_guardian,
    create_fee_calculator,
    create_document_architect,
)

agents = [
    create_policy_guardian(),
    create_fee_calculator(),
    create_document_architect(),
]

for agent in agents:
    print(f"SUCCESS: {agent.role}")