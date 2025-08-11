❓ Question:
What is the purpose of the chunk_overlap parameter when using RecursiveCharacterTextSplitter to prepare documents for RAG, and what trade-offs arise as you increase or decrease its value?

##### ✅ Answer: 
The chunk_overlap parameter in RecursiveCharacterTextSplitter serves to maintain contextual continuity between consecutive chunks of text when preparing documents for Retrieval Augmented Generation (RAG). It specifies the number of characters or tokens that will be shared between the end of one chunk and the beginning of the next. This overlap helps to ensure that no critical information or context is lost at the boundaries where a document is split. <br>

Trade-offs of increasing chunk_overlap:<br>
1) Increased context preservation <br>
2) Increased redundancy and storage <br>
3) Higher computational cost for embeddings <br>
Trade-offs of decreasing chunk_overlap: <br>
1) Reduced redundancy and storage<br>
2) Potential loss of context <br>
3) Lower computational cost for embeddings<br>
The optimal chunk_overlap value depends on the specific characteristics of the data and the requirements of the RAG application. A commonly recommended starting point is an overlap of around 10% of the chunk_size.

❓ Question:
Your retriever is configured with search_kwargs={"k": 5}. How would adjusting k likely affect RAGAS metrics such as Context Precision and Context Recall in practice, and why?
##### ✅ Answer: 
Adjusting the 'k' parameter in a retriever, which controls the number of documents retrieved, significantly impacts RAGAS metrics. Increasing 'k' (e.g., from 5 to 10) can improve Context Precision by potentially including more relevant documents, but might also introduce irrelevant ones, decreasing precision. Simultaneously, it can boost Context Recall, as more relevant documents are likely to be present in the retrieved set. The optimal 'k' depends on the specific dataset and application, requiring careful tuning and evaluation. 

❓ Question:
Compare the agent and agent_helpful assistants defined in langgraph.json. Where does the helpfulness evaluator fit in the graph, and under what condition should execution route back to the agent vs. terminate?

##### ✅ Answer: 
Comparison: <br>
agent (Simple Agent): <br>
Graph: simple_agent (app.graphs.simple_agent:graph)<br>
Flow: agent → (if tool_calls) action → back to agent; else END.<br>
Terminates as soon as the model responds without tool calls.<br>
agent_helpful (Agent with Helpfulness Check): <br>
Graph: agent_with_helpfulness (app.graphs.agent_with_helpfulness:graph)<br>
Flow: agent → (if tool_calls) action → back to agent; otherwise → helpfulness evaluator → route based on decision.<br>

Where the helpfulness evaluator fits: <br>
The evaluator is the helpfulness node. It runs only after the agent responds with no tool calls<br>

Routing condition back to agent vs. terminate: <br>
Route back to agent: when the evaluator returns HELPFULNESS:N (unhelpful) and the loop limit is not exceeded.<br>
Terminate: when the evaluator returns HELPFULNESS:Y (helpful) or when the loop limit triggers HELPFULNESS:END.