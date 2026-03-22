from src.vector_search.vector_search import perform_vector_search

def get_search_results(query):
    """
    Returns the top 5 documents matching the query.
    """
    results = perform_vector_search(query, 5)
    return results

if __name__ == "__main__":
    # For testing purposes
    query = input("Enter your legal query: ")
    results = get_search_results(query)
    for i, doc in enumerate(results, start=1):
        print(f"Result {i}: {doc}")