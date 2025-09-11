from langchain.schema import Document

documents = [
    # --- Machine Learning Core ---
    Document(page_content="Machine learning enables computers to learn from data.", metadata={"id": "doc1"}),
    Document(page_content="Deep learning is a subset of machine learning using neural networks.", metadata={"id": "doc2"}),
    Document(page_content="Support vector machines are supervised learning models used for classification.", metadata={"id": "doc3"}),
    Document(page_content="Neural networks consist of layers of interconnected nodes inspired by the human brain.", metadata={"id": "doc4"}),
    Document(page_content="Reinforcement learning trains agents to take actions in an environment to maximize reward.", metadata={"id": "doc5"}),
    
    # --- NLP ---
    Document(page_content="Natural language processing enables computers to understand human language.", metadata={"id": "doc6"}),
    Document(page_content="Transformers revolutionized NLP by introducing self-attention mechanisms.", metadata={"id": "doc7"}),
    Document(page_content="Word embeddings map words into continuous vector spaces.", metadata={"id": "doc8"}),
    Document(page_content="Sentiment analysis is the task of classifying text according to its emotional tone.", metadata={"id": "doc9"}),
    Document(page_content="Named Entity Recognition extracts entities such as people, locations, and organizations from text.", metadata={"id": "doc10"}),

    # --- Statistics & Optimization ---
    Document(page_content="Gradient descent is an optimization algorithm used to minimize loss functions.", metadata={"id": "doc11"}),
    Document(page_content="Overfitting occurs when a model learns noise in the training data rather than general patterns.", metadata={"id": "doc12"}),
    Document(page_content="Regularization techniques such as L1 and L2 prevent models from overfitting.", metadata={"id": "doc13"}),
    Document(page_content="Cross-validation helps evaluate model performance by splitting data into training and validation sets.", metadata={"id": "doc14"}),
    Document(page_content="Principal Component Analysis reduces the dimensionality of data while preserving variance.", metadata={"id": "doc15"}),

    # --- AI Applications ---
    Document(page_content="Computer vision enables machines to interpret and process visual information from the world.", metadata={"id": "doc16"}),
    Document(page_content="Autonomous vehicles rely on machine learning models for perception, prediction, and planning.", metadata={"id": "doc17"}),
    Document(page_content="Speech recognition converts spoken language into text using acoustic and language models.", metadata={"id": "doc18"}),
    Document(page_content="Recommendation systems suggest products or content based on user preferences and behavior.", metadata={"id": "doc19"}),
    Document(page_content="Chatbots simulate human conversation using natural language processing techniques.", metadata={"id": "doc20"}),

    # --- AI Foundations & History ---
    Document(page_content="Artificial intelligence research began in the 1950s with symbolic reasoning systems.", metadata={"id": "doc21"}),
    Document(page_content="The perceptron was one of the earliest neural network models, proposed in 1958.", metadata={"id": "doc22"}),
    Document(page_content="Expert systems were early AI programs designed to mimic human decision-making in specific domains.", metadata={"id": "doc23"}),
    Document(page_content="The AI winter refers to periods of reduced funding and interest in artificial intelligence research.", metadata={"id": "doc24"}),
    Document(page_content="Alan Turing proposed the Turing Test as a way to evaluate machine intelligence.", metadata={"id": "doc25"}),

    # --- financial_documents ---
    Document(page_content="Budgeting helps individuals manage their income and expenses effectively.", metadata={"id": "fin_doc1"}),
    Document(page_content="Understanding interest rates is crucial for making informed borrowing and saving decisions.", metadata={"id": "fin_doc2"}),
    Document(page_content="Compound interest allows investments to grow faster over time compared to simple interest.", metadata={"id": "fin_doc3"}),
    Document(page_content="Credit scores affect your ability to get loans and the interest rates you are offered.", metadata={"id": "fin_doc4"}),
    Document(page_content="Diversification reduces risk by spreading investments across different asset classes.", metadata={"id": "fin_doc5"}),

    Document(page_content="Stock markets allow investors to buy and sell ownership in public companies.", metadata={"id": "fin_doc6"}),
    Document(page_content="Bonds are debt instruments where investors lend money to an entity in exchange for interest payments.", metadata={"id": "fin_doc7"}),
    Document(page_content="Mutual funds pool money from multiple investors to invest in a diversified portfolio.", metadata={"id": "fin_doc8"}),
    Document(page_content="Exchange-Traded Funds (ETFs) trade like stocks but offer diversified exposure.", metadata={"id": "fin_doc8"}),

    # ---  ---
     Document(
        page_content=(
            "Budgeting is the process of creating a plan to spend your money. "
            "It allows you to prioritize essential expenses, track your income, and save for future goals. "
            "A well-structured budget helps prevent overspending, reduces financial stress, and builds a foundation for financial stability."
        ),
        metadata={"id": "fin_doc1"}
    ),
    Document(
        page_content=(
            "Understanding interest rates is essential for both borrowing and investing. "
            "High interest rates increase the cost of loans, while low rates can make saving less profitable. "
            "By comparing different loan offers and considering the impact of compound interest, individuals can make better financial decisions."
        ),
        metadata={"id": "fin_doc2"}
    ),
    Document(
        page_content=(
            "Credit scores are numerical representations of a person's creditworthiness. "
            "They are calculated based on payment history, credit utilization, length of credit history, types of credit, and recent inquiries. "
            "A high credit score can result in lower interest rates and better loan terms, while a low score may limit borrowing options."
        ),
        metadata={"id": "fin_doc3"}
    ),
    Document(
        page_content=(
            "Investing in the stock market involves purchasing shares of publicly traded companies. "
            "Stocks can generate returns through price appreciation and dividends, but they carry risks such as market volatility. "
            "Diversifying investments across sectors and geographies can help manage risk and improve long-term financial outcomes."
        ),
        metadata={"id": "fin_doc4"}
    ),
    Document(
        page_content=(
            "Bonds are debt instruments issued by governments, municipalities, or corporations to raise capital. "
            "Investors receive regular interest payments and the principal at maturity. "
            "Bonds are generally considered lower-risk than stocks, but their returns can be affected by interest rate changes and inflation."
        ),
        metadata={"id": "fin_doc5"}
    ),
    Document(
        page_content=(
            "Mutual funds pool money from multiple investors to invest in a diversified portfolio of stocks, bonds, or other assets. "
            "They offer professional management and diversification, making them suitable for investors who prefer a hands-off approach. "
            "Fees and expense ratios should be considered when selecting a mutual fund."
        ),
        metadata={"id": "fin_doc6"}
    ),
    Document(
        page_content=(
            "Retirement planning involves setting financial goals and investing to ensure a comfortable future. "
            "Contributing to retirement accounts like 401(k)s or IRAs can provide tax advantages and compound growth over time. "
            "Early and consistent saving is key to achieving long-term retirement security."
        ),
        metadata={"id": "fin_doc7"}
    ),
    Document(
        page_content=(
            "Insurance is a financial product designed to protect against unforeseen events and losses. "
            "Health insurance covers medical expenses, life insurance provides financial security for dependents, and property insurance protects assets. "
            "Choosing the right coverage and understanding policy terms is essential to avoid gaps in protection."
        ),
        metadata={"id": "fin_doc8"}
    ),
    Document(
        page_content=(
            "Diversification is an investment strategy that spreads capital across multiple assets to reduce risk. "
            "By investing in a mix of stocks, bonds, real estate, and commodities, an investor can minimize the impact of poor performance in any single asset. "
            "Diversification does not eliminate risk entirely but can improve the stability of returns."
        ),
        metadata={"id": "fin_doc9"}
    ),
    Document(
        page_content=(
            "Emergency funds are savings set aside to cover unexpected expenses such as medical emergencies, car repairs, or job loss. "
            "Financial advisors typically recommend keeping three to six months of living expenses in a liquid, easily accessible account. "
            "Having an emergency fund prevents the need to rely on high-interest debt during crises and provides peace of mind."
        ),
        metadata={"id": "fin_doc10"}
    ),
]
