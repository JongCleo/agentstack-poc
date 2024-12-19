# Tweet Proposer
This is a POC to explore the ergonomics of using AgentStack.

I decided to build a tool that scrapes the users' timeline, identifies salient tweets based on the user's interests and proposes drafts to those tweets.

## Learnings

### On Scraping
1. Most Twitter scraping libraries are dusted. The lone survivor is [twikit](https://github.com/d60/twikit). Don't dare think of rolling it yourself - just look at the guts of the login method to get an idea of how much work it does to bypass their bot detection.
2. Firecrawl will pre-emptively block scraping Twitter and Reddit 

## On AgentStack
1. Using `kickoff_for_each` appeared to break the observability as this message was repeatedly thrown:
`🖇 AgentOps: Could not record event. Start a session by calling agentops.start_session().`
2. Logging output was surpressed for the code running inside custom tools, would like to figure out a way to get that back.
3. It was v useful to see the input tokens and output token counts in the traces. 

## On CrewAI
1. The agent and task taxonomy isn't necessary for simple flows and you're sometimes better off just calling the tools directly. Realizing this I stopped trying to force the Twitter stuff in CrewAI primitives and just invoked it before calling run.

2. Almost always favour using the `output_pydantic` or `output_json` over natural language expected output alone. It wasn't obvious that expected_output was required in addition to these fields and could use guidance on what to specify besides maybe explaining the pydantic class.

3. It wasn't obvious how to map the output of one task to spawn multiple instance of another task.

4. I don't think the list of available models is comprehensive (from the agent gen cli) I couldn't find gpt-4o-mini in the list.


## Installation 
1. `poetry install`  
2. `poetry shell`
3. To run your project, use the following command:  
`crewai run` or `python src/main.py`
4. To replay tasks from the last run, use the following command:  
`crewai replay <task_id>`  
Replace <task_id> with the ID of the task you want to replay.

#### Reset Crew Memory
If you need to reset the memory of your crew before running it again, you can do so by calling the reset memory feature:  
`crewai reset-memory`  
This will clear the crew's memory, allowing for a fresh start.


