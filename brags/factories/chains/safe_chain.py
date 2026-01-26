class SafeRetrievalQA:
    def __init__(self, qa_chain, default_answer="I don't know"):
        self.qa_chain = qa_chain
        self.default_answer = default_answer

    def __call__(self, query: str):
        try:
            return self.qa_chain(query)
        except Exception as e:
            print("There seems to be some error")
            return {
                "result": self.default_answer,
                "source_documents": [],
                "error": str(e),  # optional: remove if you want it silent
            }

    def run(self, query: str):
        # Support LangChain's .run() API
        try:
            return self.qa_chain.run(query)
        except Exception:
            return self.default_answer