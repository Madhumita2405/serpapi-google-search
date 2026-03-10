#ReactwithWikiTools
import os,getpass
from dotenv import load_dotenv
load_dotenv()
hf=getpass.getpass("Enter your HF token: ")
# print(hf)
from langchain_huggingface import ChatHuggingFace,HuggingFaceEndpoint
endpoint=HuggingFaceEndpoint(repo_id="openai/gpt-oss-20b")
llm=ChatHuggingFace(llm=endpoint)
# resp=llm.invoke("What is the capital of France?")
# print(resp.content)
#instead of open ai chathuggingface llm is used
from langchain_community.utilities import WikipediaAPIWrapper
from langchain_community.tools import WikipediaQueryRun
api_wrapper = WikipediaAPIWrapper(top_k_results=1, doc_content_chars_max=100)
wiki_tool = WikipediaQueryRun(api_wrapper=api_wrapper)
print(wiki_tool.run({"query": "AI Agents"}))
tools = [wiki_tool]
llm_with_tools = llm.bind_tools([wiki_tool])
result = llm_with_tools.invoke("What are AI agents?")
print(result)


