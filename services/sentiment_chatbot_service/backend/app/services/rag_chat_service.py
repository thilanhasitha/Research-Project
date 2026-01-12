# class RAGChatService:
#     def __init__(self, llm, embed_client, rss_repo):
#         self.llm = llm
#         self.embed = embed_client
#         self.repo = rss_repo

#     async def answer(self, question: str):
#         q_emb = await self.embed.embed_text(question)

#         docs = await self.repo.search_similar(q_emb)

#         context = "\n\n".join(
#             [f"Title: {d['title']}\nSummary: {d['summary']}" for d in docs]
#         )

#         prompt = f"""
#         Use the financial context to answer the user's question.
        
#         CONTEXT:
#         {context}

#         QUESTION:
#         {question}
#         """

#         return await self.llm.ainvoke(prompt)
