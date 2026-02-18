import wikipedia

search_term = "Python (programming language)"

page = wikipedia.page(search_term)

print("Title:", page.title)

print("\nSummary:\n")
print(wikipedia.summary(search_term, sentences=3))
