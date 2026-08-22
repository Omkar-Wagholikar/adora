class SafeRetrievalQA:
    def __init__(self, qa_chain, default_answer="I don't know", hallucination_checker=None):
        self.qa_chain = qa_chain
        self.default_answer = default_answer
        self.hallucination_checker = hallucination_checker

    def __call__(self, query: str):
        try:
            result = self.qa_chain(query)
            if self.hallucination_checker is not None:
                result["hallucination_check"] = self.hallucination_checker.check(
                    result.get("result", ""), result.get("source_documents") or []
                )
            return result
        except Exception as e:
            # The exception could come from either the retriever or the LLM
            # combine step -- most commonly the latter (bad/missing API key,
            # rate limit), in which case retrieval itself likely succeeded.
            # Re-running just the retriever (cheap, already fully
            # configured) means callers still get real chunks back instead
            # of an unconditionally empty source_documents list.
            try:
                source_documents = self.qa_chain.retriever.invoke(query)
            except Exception:
                source_documents = []
            return {
                "result": self.default_answer,
                "source_documents": source_documents,
                "error": str(e),
            }

    def run(self, query: str):
        # Support LangChain's .run() API
        try:
            return self.qa_chain.run(query)
        except Exception:
            return self.default_answer