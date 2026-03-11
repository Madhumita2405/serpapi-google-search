import os
from serpapi import GoogleSearch
import pandas as pd
from dotenv import load_dotenv
import streamlit as st
load_dotenv()
hf=os.getenv("SERP_API_KEY")
kw_list=["Nike Shoes","Bata Shoes","Puma Shoes"]
for keyword in kw_list:
    params={
        "q":keyword,
        "engine":"google",
        "location":"Austin,Texas,United States",
        "hl":"en",
        "gl":"us",
        "num":10,
        "api_key":hf
    }
    search=GoogleSearch(params)
    results=search.get_dict()
    organic=results.get("organic_results",[])
    #print(f"\nResults for {keyword}:\n")
    titls,linkls,snipls=[],[],[]
    for r in organic[:5]:
        titls.append(r.get("title"))
        linkls.append(r.get("link"))
        snipls.append(r.get("snippet"))
    dt={"title":titls,"link":linkls,"snippet":snipls}
    st.dataframe(dt)
