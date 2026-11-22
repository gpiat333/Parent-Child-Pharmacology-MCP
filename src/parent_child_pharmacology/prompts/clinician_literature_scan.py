def register(mcp):
    @mcp.prompt()
    def clinician_literature_scan(topic: str) -> str:

        return (
            f"For a clinician: use search_literature, search_trials and search_funded_research on "
            f"'{topic}'. Return a short table of key papers, active trials and funded projects with links, "
            "followed by a 3-sentence evidence summary and the gaps in evidence."
        )
