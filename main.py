from dotenv import load_dotenv
from crewai import Crew, Process

# Načteme API klíč hned na začátku
load_dotenv()

# Importujeme agenta a úkol z našich 'core' modulů
from core.agents import developer_agent
from core.tasks import documentation_task


def main():
    """Hlavní funkce pro sestavení a spuštění Crew."""
    print("🚀 Initializing the Sophia v2 Crew for a documentation task...")

    # Sestavení posádky
    sophia_crew = Crew(
        agents=[developer_agent],
        tasks=[documentation_task],
        process=Process.sequential,
        verbose=2,
    )

    print("🏁 Crew assembled. Kicking off the task...")
    result = sophia_crew.kickoff()

    print("\n\n########################")
    print("## ✅ Task Completed!")
    print("## Here is the result:")
    print("########################\n")
    print(result)


if __name__ == "__main__":
    main()
